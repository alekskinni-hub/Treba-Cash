#!/usr/bin/env python3
"""
Скрипт для GitHub Actions: получает актуальные оферы МФО Казахстана из
PDL-Profit API и генерирует mfo-kz-live-data.json для страницы
/porivnyannya-mfo-kz/.

Это аналог fetch_offers.py (украинская версия), адаптированный под
country=KZ. Отличия:
  - API_URL берёт country=KZ вместо country=UA
  - таблица юрлиц берётся из requisites-kz.json (БИН вместо ЄДРПОУ)
  - логика badge/ставок такая же, но лимиты ГЭСВ в Казахстане иные
    (см. determine_badge) — ориентировочно 46% для обычных микрокредитов
    МФО и до 179% для PDL-займов сроком до 45 дней (данные АРРФР/Нацбанк
    РК на 2026 год, могут измениться — проверяйте актуальные пределы
    перед публикацией сайта)

ВАЖНО: не хардкодь API_KEY в этом файле — он берётся из переменной
среды PDL_API_KEY (GitHub Secrets).
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
    print("❌ ОШИБКА: переменная среды PDL_API_KEY не установлена.")
    print("   Добавь её в GitHub → Settings → Secrets and variables → Actions")
    sys.exit(1)

# ⚠️ Предположение: PDL-Profit поддерживает country=KZ так же, как country=UA
# в оригинальном скрипте. Если API вернёт status != success или пустой список —
# скрипт сообщит об этом явно (см. fetch_offers). Если у аккаунта отдельный
# ключ/эндпоинт для казахстанских офферов — замени API_URL ниже.
#
# Параметр mode здесь намеренно не указан — по документации API это значит
# "CPL, CPS" (оба типа целей) по умолчанию. Если нужны только кредитные лиды
# (CPL), без CPS/рассрочек — допиши &mode=CPL в строку ниже.
API_URL = f"https://pdl-profit.com/partnerapi/offers/data?api_key={API_KEY}&country=KZ"

REQUISITES_FILE = "requisites-kz.json"


def fetch_offers():
    """Запрос к PDL-Profit API, с учётом пагинации."""
    all_offers = []
    page = 1
    max_pages = 1

    while page <= max_pages:
        url = f"{API_URL}&page={page}"
        req = urllib.request.Request(url, headers={"User-Agent": "TrebaCash-KZ-Bot/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.URLError as e:
            print(f"❌ Ошибка запроса к API (страница {page}): {e}")
            sys.exit(1)

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            print(f"❌ Ответ API не является корректным JSON (страница {page})")
            sys.exit(1)

        if payload.get("status") != "success":
            print(f"❌ API вернул ошибку: {payload.get('message')}")
            sys.exit(1)

        page_offers = payload.get("data", [])
        all_offers.extend(page_offers)

        max_pages = payload.get("pages", 1)
        total_count = payload.get("count")
        print(f"   Страница {page}/{max_pages}: получено {len(page_offers)} офферов (total count в ответе: {total_count})")
        page += 1

    return all_offers


def load_requisites():
    if not os.path.exists(REQUISITES_FILE):
        print(f"⚠️  Файл {REQUISITES_FILE} не найден — реквизиты не будут добавлены.")
        return {}
    with open(REQUISITES_FILE, encoding="utf-8") as f:
        return json.load(f)


def clean_name(name):
    return re.sub(r"\s+KZ$", "", name).strip()


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
    """
    Логика бейджа по сумме/сроку.
    ⚠️ Пороги ("50000" и т.д.) скопированы из украинской версии как
    структурный образец — они в тенге не откалиброваны. Подставь
    реальные пороги под казахстанские суммы (10 000 – 400 000 ₸)
    перед продакшеном.
    """
    if sum_val >= 150000:
        return (f"До {int(sum_val/1000)} 000 ₸ на карту", "blue")
    if term_val >= 45:
        return ("Длительный срок возврата", "purple")
    if term_val <= 10:
        return ("Быстрое решение за минуты", "teal")
    return ("Выгодные условия для новых клиентов", "green")


def transform_offer(offer, requisites):
    name = clean_name(offer.get("name", ""))

    first_credit_sum = to_int(offer.get("first_credit") or offer.get("credit"), 0)
    term = to_int(offer.get("term") or offer.get("days"), 30)

    first_pct = to_float(offer.get("first_credit_percent"), None)
    standard_pct = to_float(offer.get("first_credit_percent_standard"), None)

    # ГЭСВ ориентировочно: дневная ставка * 365 (упрощённо, для отображения диапазона)
    rate_min = round(first_pct * 365, 1) if first_pct is not None else None
    rate_max = round(standard_pct * 365, 1) if standard_pct is not None else rate_min

    has_zero_badge = first_pct is not None and first_pct <= 0.5

    badge_text, badge_color = determine_badge(first_credit_sum, term)

    req = requisites.get(name, {})

    # Резервне джерело юр. інформації: якщо в requisites-kz.json порожньо,
    # а сама мережа PDL-Profit віддала щось у полі legal_info — використовуємо це,
    # а не одразу показуємо "уточняется". Дані з requisites-kz.json мають пріоритет,
    # бо вони перевірені вручну; legal_info з API — лише страховка.
    api_legal_info = (offer.get("legal_info") or "").strip() or None

    return {
        "id": offer.get("id"),  # ⚠️ Используется на странице как proxy для "давности" бренда
        # (MFO_SENIORITY_KZ): меньший id = раньше добавлен в систему PDL-Profit. Это НЕ точная
        # дата выхода бренда на рынок Казахстана — только порядок появления в самой сети.
        "name": name,
        "logo": offer.get("image"),
        "ref": offer.get("url"),
        "sum": first_credit_sum,
        "term": term,
        "rateMin": rate_min if rate_min is not None else 0,
        "rateMax": rate_max if rate_max is not None else 0,
        "badge": badge_text,
        "badgeColor": badge_color,
        "hasZeroBadge": has_zero_badge,
        "goldBadgeText": (
            f"Первый займ под {first_pct}%*" if has_zero_badge and first_pct is not None
            else "Первый займ под 0,01%*" if has_zero_badge else None
        ),
        "legal": req.get("legal") or api_legal_info,
        "bin": req.get("bin"),
        "license": req.get("license"),
        "address": req.get("address"),
        "phone": req.get("phone"),
        "email": req.get("email"),
        "apiTitle": offer.get("title"),
        # Мережева статистика напряму з API (по всій партнёрской сети, не только твой трафик).
        # epc_general/cr_general почти всегда заполнены; ecpc/cr (без _general) — это ТВОЯ личная
        # статистика по аккаунту и почти наверняка null, пока по KZ нет реального трафика.
        "epc": to_float(offer.get("epc_general"), None),
        "cr": to_float(offer.get("cr_general"), None),
    }


def main():
    print("📡 Запрос к PDL-Profit API (country=KZ)...")
    raw_offers = fetch_offers()
    print(f"✅ Получено офферов: {len(raw_offers)}")

    requisites = load_requisites()
    print(f"📋 Загружено реквизитов для {len(requisites)} компаний")

    transformed = [transform_offer(o, requisites) for o in raw_offers]

    missing_legal = [o["name"] for o in transformed if not o.get("legal")]
    if missing_legal:
        print(f"⚠️  Без юрлица/реквизитов: {', '.join(missing_legal)} — карточка должна честно показывать "
              f"«Юридическое лицо: уточняется», а не выдуманные данные.")

    output = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "count": len(transformed),
        "offers": transformed,
    }

    with open("mfo-kz-live-data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"💾 Сохранено mfo-kz-live-data.json ({len(transformed)} офферов)")


if __name__ == "__main__":
    main()
