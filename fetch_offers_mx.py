#!/usr/bin/env python3
"""
Script para GitHub Actions: obtiene las ofertas vigentes de MFO/SOFOM de la
API de PDL-Profit (GEO: México) y genera mfo-live-data-mx.json para la
página /porivnyannya-mfo-mx/.

API_KEY se toma de la variable de entorno PDL_API_KEY (GitHub Secrets),
NUNCA se hardcodea en este archivo.

Es la versión mexicana de fetch_offers.py (misma lógica, country=MX,
salida separada, textos de badges en español y requisites-mx.json en vez
de requisites.json).
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
    print("❌ ERROR: la variable de entorno PDL_API_KEY no está definida.")
    print("   Agrégala en GitHub → Settings → Secrets and variables → Actions")
    sys.exit(1)

# GEO México (mismo endpoint que la versión UA, cambia solo el parámetro country).
# NOTA sobre "mode": no se especifica a propósito. Según la documentación oficial
# de PDL-Profit, si "mode" se omite, la API devuelve ofertas de AMBOS tipos
# (CPL y CPS) por defecto — no solo CPL. Si en algún momento se quiere traer
# un solo tipo de lead, agregar "&mode=CPL" o "&mode=CPS" aquí.
API_URL = f"https://pdl-profit.com/partnerapi/offers/data?api_key={API_KEY}&country=MX"

# ── Datos que la API no entrega (razón social, domicilio, etc.) ──
# Se toman de un archivo local (NO de la API). Ver notas de verificación
# dentro del propio archivo: varias marcas mexicanas todavía no tienen
# razón social confirmada y deben completarse antes de publicar.
REQUISITES_FILE = "requisites-mx.json"

# Rango de plazos que se muestra en el sitio (definido a nivel de negocio,
# no viene de la API). Ver README del repo antes de cambiar estos valores.
DISPLAY_TERM_MIN_DAYS = 1
DISPLAY_TERM_MAX_DAYS = 365


def fetch_offers():
    """Llama a la API de PDL-Profit y devuelve la lista de ofertas (con paginación)."""
    all_offers = []
    page = 1
    max_pages = 1

    while page <= max_pages:
        url = f"{API_URL}&page={page}"
        req = urllib.request.Request(url, headers={"User-Agent": "TrebaCash-Bot/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.URLError as e:
            print(f"❌ Error de conexión con la API (página {page}): {e}")
            sys.exit(1)

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            print(f"❌ La respuesta de la API no es un JSON válido (página {page})")
            sys.exit(1)

        if payload.get("status") != "success":
            print(f"❌ La API devolvió un error: {payload.get('message')}")
            sys.exit(1)

        page_offers = payload.get("data", [])
        all_offers.extend(page_offers)

        max_pages = payload.get("pages", 1)
        total_count = payload.get("count")
        print(f"   Página {page}/{max_pages}: {len(page_offers)} ofertas recibidas (total reportado: {total_count})")
        page += 1

    return all_offers


def load_requisites():
    """Carga el archivo local con los datos legales (razón social, domicilio, etc.)."""
    if not os.path.exists(REQUISITES_FILE):
        print(f"⚠️  No se encontró {REQUISITES_FILE} — no se agregarán datos legales.")
        return {}
    with open(REQUISITES_FILE, encoding="utf-8") as f:
        data = json.load(f)
    data.pop("_readme", None)
    return data


def clean_name(name):
    """Quita sufijos como ' MX' del nombre de la oferta."""
    return re.sub(r"\s+MX$", "", name).strip()


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
    """Mismo criterio de badge que en el sitio UA, adaptado a MXN/español."""
    if sum_val >= 20000:
        return (f"Hasta {int(sum_val):,} MXN".replace(",", " "), "blue")
    if term_val >= 90:
        return ("Hasta 4 meses para pagar", "purple")
    if term_val <= 15:
        return ("Resolución en minutos", "teal")
    return ("Condiciones para nuevos clientes", "green")


def clamp_display_term(term_val):
    """
    Ajusta el plazo mostrado en el sitio al rango de negocio definido
    (DISPLAY_TERM_MIN_DAYS–DISPLAY_TERM_MAX_DAYS), independientemente del
    valor crudo que entregue la API para ese producto puntual.
    NOTA: esto es una decisión de negocio tomada explícitamente por el
    cliente — no es un cálculo regulatorio. Revisar antes de escalar tráfico
    pago si el plazo mostrado debe reflejar el plazo real de cada producto.
    """
    return max(DISPLAY_TERM_MIN_DAYS, min(DISPLAY_TERM_MAX_DAYS, term_val))


def transform_offer(offer, requisites):
    """Convierte una oferta del formato de la API al formato de nuestro sitio."""
    name = clean_name(offer.get("name", ""))

    first_credit_sum = to_int(offer.get("first_credit") or offer.get("credit"), 0)
    raw_term = to_int(offer.get("term") or offer.get("days"), 30)
    term = clamp_display_term(raw_term)

    # Estadísticas de rendimiento del oferta, directo de la API — sin
    # inventar placeholders. epc_general/cr_general = estadística de TODA
    # la red (disponible desde el primer request, incluso sin tráfico
    # propio). ecpc/cr (sin "_general") = estadística PERSONAL de esta
    # cuenta, solo dentro del rango date_from/date_to del endpoint
    # /statistic — no se pide aquí porque este script no lo consulta.
    # Se guardan ambos por si en el futuro se agrega un orden "Recomendado"/
    # "Top" en index-mx.html, igual que en las versiones UA/KZ.
    epc_general = to_float(offer.get("epc_general"), None)
    cr_general = to_float(offer.get("cr_general"), None)

    first_pct = to_float(offer.get("first_credit_percent"), None)
    standard_pct = to_float(offer.get("first_credit_percent_standard"), None)

    # CAT/RRPS orientativo: tasa diaria * 365 (simplificado, solo para mostrar un rango)
    rate_min = round(first_pct * 365, 1) if first_pct is not None else None
    rate_max = round(standard_pct * 365, 1) if standard_pct is not None else rate_min

    has_zero_badge = first_pct is not None and first_pct <= 0.5

    badge_text, badge_color = determine_badge(first_credit_sum, term)

    req = requisites.get(name, {})

    # Monto de crédito repetido (segundo crédito), cuando la API lo entrega.
    # No estaba mapeado antes; corresponde a la columna "Repetido" del
    # documento fuente de ofertas MX.
    repeat_sum_raw = offer.get("credit_repeat") or offer.get("second_credit")
    repeat_sum = to_int(repeat_sum_raw, 0) if repeat_sum_raw not in (None, "") else None

    # PRIORIDAD DE RAZÓN SOCIAL:
    # 1) legal_info que entrega la propia API PDL-Profit para esta oferta
    #    (si no viene vacío) — esto es LA FUENTE MÁS CONFIABLE porque la
    #    entrega directamente el anunciante/la red, no un tercero.
    # 2) requisites-mx.json (datos verificados a mano vía búsqueda web).
    # 3) null → el front-end muestra "Razón social en verificación".
    api_legal_info = (offer.get("legal_info") or "").strip()
    if api_legal_info:
        legal_name = api_legal_info
        legal_source = "api"
        requisites_verified = True
    elif req.get("legal"):
        legal_name = req.get("legal")
        legal_source = "requisites_file"
        requisites_verified = bool(req.get("verified"))
    else:
        legal_name = None
        legal_source = None
        requisites_verified = False

    return {
        "id": offer.get("id"),
        "name": name,
        "logo": offer.get("image"),
        "ref": offer.get("url"),
        "sum": first_credit_sum,
        "repeatSum": repeat_sum,
        "term": term,
        "termRaw": raw_term,
        "epc": epc_general,   # estadística de red (todos los webmasters), no personal
        "cr": cr_general,     # ídem — usar para un futuro orden "Recomendado"/"Top"
        "rateMin": rate_min if rate_min is not None else 0,
        "rateMax": rate_max if rate_max is not None else 0,
        "badge": badge_text,
        "badgeColor": badge_color,
        "hasZeroBadge": has_zero_badge,
        "goldBadgeText": (
            f"Primer préstamo al {first_pct}%*" if has_zero_badge and first_pct is not None
            else "Primer préstamo al 0.01%*" if has_zero_badge else None
        ),
        "legal": legal_name,
        "legalSource": legal_source,  # "api" | "requisites_file" | None — útil para auditar de dónde salió el dato
        "rfc": req.get("rfc"),
        "address": req.get("address"),
        "phone": req.get("phone"),
        "email": req.get("email"),
        "requisitesVerified": requisites_verified,
    }


def main():
    print("📡 Consultando la API de PDL-Profit (GEO: MX)...")
    raw_offers = fetch_offers()
    print(f"✅ Ofertas recibidas: {len(raw_offers)}")

    requisites = load_requisites()
    print(f"📋 Datos legales cargados para {len(requisites)} empresas")

    transformed = [transform_offer(o, requisites) for o in raw_offers]

    unverified = [o["name"] for o in transformed if not o["requisitesVerified"]]
    if unverified:
        print(f"⚠️  Sin razón social verificada: {', '.join(unverified)}")
        print("    Revisa requisites-mx.json antes de publicar el pie de página legal.")

    output = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "count": len(transformed),
        "displayTermRange": {"min": DISPLAY_TERM_MIN_DAYS, "max": DISPLAY_TERM_MAX_DAYS},
        "offers": transformed,
    }

    with open("mfo-live-data-mx.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"💾 Guardado mfo-live-data-mx.json ({len(transformed)} ofertas)")


if __name__ == "__main__":
    main()
