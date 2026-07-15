#!/usr/bin/env python3
"""
Скрипт для GitHub Actions: отримує актуальні офери МФО з PDL-Profit API
і генерує mfo-live-data.json для сторінки /porivnyannya-mfo/.

API_KEY береться з змінної середовища PDL_API_KEY (GitHub Secrets),
НІКОЛИ не хардкодиться в цьому файлі.
"""

import os
import sys
import json
import re
import urllib.request
import urllib.error
from datetime import datetime, timezone

API_KEY = os.environ.get("PDL_API_KEY")
if not API_KEY:
    print("❌ ПОМИЛКА: змінна середовища PDL_API_KEY не встановлена.")
    print("   Додай її в GitHub → Settings → Secrets and variables → Actions")
    sys.exit(1)

API_URL = f"https://pdl-profit.com/partnerapi/offers/data?api_key={API_KEY}&country=UA&mode=CPL"

# ── Реквізити та дані, яких немає в API (юрособа, ЄДРПОУ, адреса) ──
# Підтягуються з окремого локального файлу requisites.json (не з API)
REQUISITES_FILE = "requisites.json"


def fetch_offers():
    """Робить запит до PDL-Profit API і повертає список офферів."""
    req = urllib.request.Request(API_URL, headers={"User-Agent": "TrebaCash-Bot/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.URLError as e:
        print(f"❌ Помилка запиту до API: {e}")
        sys.exit(1)

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        print("❌ Відповідь API не є коректним JSON")
        sys.exit(1)

    if payload.get("status") != "success":
        print(f"❌ API повернув помилку: {payload.get('message')}")
        sys.exit(1)

    return payload.get("data", [])


def load_requisites():
    """Завантажує локальний файл з реквізитами (ЄДРПОУ, адреса тощо)."""
    if not os.path.exists(REQUISITES_FILE):
        print(f"⚠️  Файл {REQUISITES_FILE} не знайдено — реквізити не будуть додані.")
        return {}
    with open(REQUISITES_FILE, encoding="utf-8") as f:
        return json.load(f)


def clean_name(name):
    """Прибирає зайві суфікси типу ' UA' з назви оферу."""
    return re.sub(r"\s+UA$", "", name).strip()


def to_float(val, default=0.0):
    try:
        return float(str(val).replace(",", "."))
    except (ValueError, TypeError):
        return default


def to_int(val, default=0):
    try:
        return int(float(str(val).replace(",", ".")))
    except (ValueError, TypeError):
        return default


def determine_badge(sum_val, term_val):
    """Логіка кольорового бейджа за сумою/строком (та сама, що на сайті)."""
    if sum_val >= 50000:
        return (f"До {int(sum_val/1000)} 000 ₴ на картку", "blue")
    if term_val >= 200:
        return ("До 12 місяців на повернення", "purple")
    if term_val <= 20:
        return ("Швидке рішення за хвилини", "teal")
    return ("Вигідні умови для нових клієнтів", "green")


def transform_offer(offer, requisites):
    """Конвертує один офер з формату API у формат нашого сайту."""
    name = clean_name(offer.get("name", ""))

    first_credit_sum = to_int(offer.get("first_credit") or offer.get("credit"), 0)
    term = to_int(offer.get("term") or offer.get("days"), 30)

    first_pct = to_float(offer.get("first_credit_percent"), None)
    standard_pct = to_float(offer.get("first_credit_percent_standard"), None)

    # РРПС orієнтовно: денна ставка * 365 (спрощено, для відображення діапазону)
    rate_min = round(first_pct * 365, 1) if first_pct is not None else None
    rate_max = round(standard_pct * 365, 1) if standard_pct is not None else rate_min

    # Золотий бейдж — якщо ставка першого кредиту суттєво нижча за стандартну
    has_zero_badge = first_pct is not None and first_pct <= 0.5

    badge_text, badge_color = determine_badge(first_credit_sum, term)

    req = requisites.get(name, {})

    return {
        "id": offer.get("id"),
        "name": name,
        "logo": offer.get("image"),  # пряме посилання з API, свій хостинг не потрібен
        "ref": offer.get("url"),
        "sum": first_credit_sum,
        "term": term,
        "rateMin": rate_min if rate_min is not None else 0,
        "rateMax": rate_max if rate_max is not None else 0,
        "badge": badge_text,
        "badgeColor": badge_color,
        "hasZeroBadge": has_zero_badge,
        "goldBadgeText": (
            f"Перша позика під {first_pct}%*" if has_zero_badge and first_pct is not None
            else "Перша позика під 0,01%*" if has_zero_badge else None
        ),
        "legal": req.get("legal"),
        "edrpou": req.get("edrpou"),
        "address": req.get("address"),
        "phone": req.get("phone"),
        "email": req.get("email"),
    }


def main():
    print("📡 Запит до PDL-Profit API...")
    raw_offers = fetch_offers()
    print(f"✅ Отримано офферів: {len(raw_offers)}")

    requisites = load_requisites()
    print(f"📋 Завантажено реквізитів для {len(requisites)} компаній")

    transformed = [transform_offer(o, requisites) for o in raw_offers]

    output = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "count": len(transformed),
        "offers": transformed,
    }

    with open("mfo-live-data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"💾 Збережено mfo-live-data.json ({len(transformed)} офферів)")


if __name__ == "__main__":
    main()
