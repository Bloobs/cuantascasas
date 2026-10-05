#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CUENTACASAS - Monitor de oferta de vivienda en alquiler por provincias
----------------------------------------------------------------------
Extrae el número total de anuncios de alquiler en Idealista, Fotocasa,
Pisos.com y Habitaclia para las 52 provincias españolas.
"""

import json
import os
import random
import re
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup

try:
    from camoufox.sync_api import Camoufox
except ImportError:
    print("[!] Error: Camoufox no está instalado. Ejecuta: pip install camoufox")
    sys.exit(1)

try:
    from curl_cffi import requests
except ImportError:
    print("[!] Error: curl_cffi no está instalado. Ejecuta: pip install curl_cffi")
    sys.exit(1)

# ==============================================================================
# CONFIGURACIÓN DE MAPEO DE SLUGS
# ==============================================================================

PROVINCIAS_MAP = {
    "Álava": {
        "idealista": "alava",
        "fotocasa": "araba-alava-provincia",
        "pisos": "alava_araba",
        "habitaclia": "araba-alava-provincia",
    },
    "Albacete": {
        "idealista": "albacete-provincia",
        "fotocasa": "albacete-provincia",
        "pisos": "albacete",
        "habitaclia": "albacete-provincia",
    },
    "Alicante": {
        "idealista": "alicante",
        "fotocasa": "alicante-provincia",
        "pisos": "alicante_alacant",
        "habitaclia": "alicante-provincia",
    },
    "Almería": {
        "idealista": "almeria-provincia",
        "fotocasa": "almeria-provincia",
        "pisos": "almeria",
        "habitaclia": "almeria-provincia",
    },
    "Ávila": {
        "idealista": "avila-provincia",
        "fotocasa": "avila-provincia",
        "pisos": "avila",
        "habitaclia": "avila-provincia",
    },
    "Badajoz": {
        "idealista": "badajoz-provincia",
        "fotocasa": "badajoz-provincia",
        "pisos": "badajoz",
        "habitaclia": "badajoz-provincia",
    },
    "Baleares": {
        "idealista": "balears-illes",
        "fotocasa": "illes-balears-provincia",
        "pisos": "illes_balears",
        "habitaclia": "illes-balears-provincia",
    },
    "Barcelona": {
        "idealista": "barcelona-provincia",
        "fotocasa": "barcelona-provincia",
        "pisos": "barcelona",
        "habitaclia": "barcelona-provincia",
    },
    "Burgos": {
        "idealista": "burgos-provincia",
        "fotocasa": "burgos-provincia",
        "pisos": "burgos",
        "habitaclia": "burgos-provincia",
    },
    "Cáceres": {
        "idealista": "caceres-provincia",
        "fotocasa": "caceres-provincia",
        "pisos": "caceres",
        "habitaclia": "caceres-provincia",
    },
    "Cádiz": {
        "idealista": "cadiz-provincia",
        "fotocasa": "cadiz-provincia",
        "pisos": "cadiz",
        "habitaclia": "cadiz-provincia",
    },
    "Castellón": {
        "idealista": "castellon",
        "fotocasa": "castellon-provincia",
        "pisos": "castellon_castello",
        "habitaclia": "castellon-provincia",
    },
    "Ciudad Real": {
        "idealista": "ciudad-real-provincia",
        "fotocasa": "ciudad-real-provincia",
        "pisos": "ciudad_real",
        "habitaclia": "ciudad-real-provincia",
    },
    "Córdoba": {
        "idealista": "cordoba-provincia",
        "fotocasa": "cordoba-provincia",
        "pisos": "cordoba",
        "habitaclia": "cordoba-provincia",
    },
    "A Coruña": {
        "idealista": "a-coruna-provincia",
        "fotocasa": "a-coruna-provincia",
        "pisos": "a_coruna",
        "habitaclia": "a-coruna-provincia",
    },
    "Cuenca": {
        "idealista": "cuenca-provincia",
        "fotocasa": "cuenca-provincia",
        "pisos": "cuenca",
        "habitaclia": "cuenca-provincia",
    },
    "Girona": {
        "idealista": "girona-provincia",
        "fotocasa": "girona-provincia",
        "pisos": "girona",
        "habitaclia": "girona-provincia",
    },
    "Granada": {
        "idealista": "granada-provincia",
        "fotocasa": "granada-provincia",
        "pisos": "granada",
        "habitaclia": "granada-provincia",
    },
    "Guadalajara": {
        "idealista": "guadalajara-provincia",
        "fotocasa": "guadalajara-provincia",
        "pisos": "guadalajara",
        "habitaclia": "guadalajara-provincia",
    },
    "Guipúzcoa": {
        "idealista": "guipuzcoa",
        "fotocasa": "gipuzkoa-provincia",
        "pisos": "guipuzcoa_gipuzkoa",
        "habitaclia": "gipuzkoa-provincia",
    },
    "Huelva": {
        "idealista": "huelva-provincia",
        "fotocasa": "huelva-provincia",
        "pisos": "huelva",
        "habitaclia": "huelva-provincia",
    },
    "Huesca": {
        "idealista": "huesca-provincia",
        "fotocasa": "huesca-provincia",
        "pisos": "huesca",
        "habitaclia": "huesca-provincia",
    },
    "Jaén": {
        "idealista": "jaen-provincia",
        "fotocasa": "jaen-provincia",
        "pisos": "jaen",
        "habitaclia": "jaen-provincia",
    },
    "León": {
        "idealista": "leon-provincia",
        "fotocasa": "leon-provincia",
        "pisos": "leon",
        "habitaclia": "leon-provincia",
    },
    "Lleida": {
        "idealista": "lleida-provincia",
        "fotocasa": "lleida-provincia",
        "pisos": "lleida",
        "habitaclia": "lleida-provincia",
    },
    "La Rioja": {
        "idealista": "la-rioja",
        "fotocasa": "la-rioja-provincia",
        "pisos": "la_rioja",
        "habitaclia": "la-rioja-provincia",
    },
    "Lugo": {
        "idealista": "lugo-provincia",
        "fotocasa": "lugo-provincia",
        "pisos": "lugo",
        "habitaclia": "lugo-provincia",
    },
    "Madrid": {
        "idealista": "madrid-provincia",
        "fotocasa": "madrid-provincia",
        "pisos": "madrid",
        "habitaclia": "madrid-provincia",
    },
    "Málaga": {
        "idealista": "malaga-provincia",
        "fotocasa": "malaga-provincia",
        "pisos": "malaga",
        "habitaclia": "malaga-provincia",
    },
    "Murcia": {
        "idealista": "murcia-provincia",
        "fotocasa": "murcia-provincia",
        "pisos": "murcia",
        "habitaclia": "murcia-provincia",
    },
    "Navarra": {
        "idealista": "navarra",
        "fotocasa": "navarra-provincia",
        "pisos": "navarra",
        "habitaclia": "navarra-provincia",
    },
    "Ourense": {
        "idealista": "ourense-provincia",
        "fotocasa": "ourense-provincia",
        "pisos": "ourense",
        "habitaclia": "ourense-provincia",
    },
    "Asturias": {
        "idealista": "asturias",
        "fotocasa": "asturias-provincia",
        "pisos": "asturias",
        "habitaclia": "asturias-provincia",
    },
    "Palencia": {
        "idealista": "palencia-provincia",
        "fotocasa": "palencia-provincia",
        "pisos": "palencia",
        "habitaclia": "palencia-provincia",
    },
    "Las Palmas": {
        "idealista": "las-palmas",
        "fotocasa": "las-palmas-provincia",
        "pisos": "las_palmas",
        "habitaclia": "las-palmas-provincia",
    },
    "Pontevedra": {
        "idealista": "pontevedra-provincia",
        "fotocasa": "pontevedra-provincia",
        "pisos": "pontevedra",
        "habitaclia": "pontevedra-provincia",
    },
    "Salamanca": {
        "idealista": "salamanca-provincia",
        "fotocasa": "salamanca-provincia",
        "pisos": "salamanca",
        "habitaclia": "salamanca-provincia",
    },
    "Santa Cruz de Tenerife": {
        "idealista": "santa-cruz-de-tenerife-provincia",
        "fotocasa": "santa-cruz-de-tenerife-provincia",
        "pisos": "santa_cruz_de_tenerife",
        "habitaclia": "santa-cruz-de-tenerife-provincia",
    },
    "Cantabria": {
        "idealista": "cantabria",
        "fotocasa": "cantabria-provincia",
        "pisos": "cantabria",
        "habitaclia": "cantabria-provincia",
    },
    "Segovia": {
        "idealista": "segovia-provincia",
        "fotocasa": "segovia-provincia",
        "pisos": "segovia",
        "habitaclia": "segovia-provincia",
    },
    "Sevilla": {
        "idealista": "sevilla-provincia",
        "fotocasa": "sevilla-provincia",
        "pisos": "sevilla",
        "habitaclia": "sevilla-provincia",
    },
    "Soria": {
        "idealista": "soria-provincia",
        "fotocasa": "soria-provincia",
        "pisos": "soria",
        "habitaclia": "soria-provincia",
    },
    "Tarragona": {
        "idealista": "tarragona-provincia",
        "fotocasa": "tarragona-provincia",
        "pisos": "tarragona",
        "habitaclia": "tarragona-provincia",
    },
    "Teruel": {
        "idealista": "teruel-provincia",
        "fotocasa": "teruel-provincia",
        "pisos": "teruel",
        "habitaclia": "teruel-provincia",
    },
    "Toledo": {
        "idealista": "toledo-provincia",
        "fotocasa": "toledo-provincia",
        "pisos": "toledo",
        "habitaclia": "toledo-provincia",
    },
    "Valencia": {
        "idealista": "valencia-provincia",
        "fotocasa": "valencia-provincia",
        "pisos": "valencia",
        "habitaclia": "valencia-provincia",
    },
    "Valladolid": {
        "idealista": "valladolid-provincia",
        "fotocasa": "valladolid-provincia",
        "pisos": "valladolid",
        "habitaclia": "valladolid-provincia",
    },
    "Vizcaya": {
        "idealista": "vizcaya",
        "fotocasa": "bizkaia-provincia",
        "pisos": "vizcaya_bizkaia",
        "habitaclia": "bizkaia-provincia",
    },
    "Zamora": {
        "idealista": "zamora-provincia",
        "fotocasa": "zamora-provincia",
        "pisos": "zamora",
        "habitaclia": "zamora-provincia",
    },
    "Zaragoza": {
        "idealista": "zaragoza-provincia",
        "fotocasa": "zaragoza-provincia",
        "pisos": "zaragoza",
        "habitaclia": "zaragoza-provincia",
    },
    "Ceuta": {
        "idealista": "ceuta-provincia",
        "fotocasa": "ceuta-provincia",
        "pisos": "ceuta",
        "habitaclia": "ceuta-provincia",
    },
    "Melilla": {
        "idealista": "melilla-provincia",
        "fotocasa": "melilla-provincia",
        "pisos": "melilla",
        "habitaclia": "melilla-provincia",
    },
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Referer": "https://www.google.com/",
}

# ==============================================================================
# FUNCIONES AUXILIARES
# ==============================================================================

def parse_number(text: str) -> int:
    """Extrae el primer número entero quitando puntos de millar y espacios."""
    if not text:
        return 0
    cleaned = str(text).replace("\xa0", " ").replace("&nbsp;", " ")
    numbers = re.findall(r"\d[\d\.]*", cleaned)
    if numbers:
        raw = numbers[0].replace(".", "")
        return int(raw) if raw.isdigit() else 0
    return 0


def resultado_valido(total: int, estado: str) -> bool:
    """Acepta un cero solo si la fuente confirmó una respuesta correcta."""
    return total != 0 or estado.startswith("OK")


def fetch_idealista(page, slug: str) -> tuple[int, str]:
    """Consulta Idealista usando Camoufox."""
    url = f"https://www.idealista.com/alquiler-viviendas/{slug}/"
    try:
        response = page.goto(url, wait_until="domcontentloaded", timeout=25000)
        status = response.status if response else 0

        if status == 403:
            return 0, "Bloqueo (HTTP 403)"
        if status == 404:
            return 0, "HTTP 404"

        title_element = page.query_selector("h1#total-results, h1.main-title, h1")
        if title_element:
            val = parse_number(title_element.inner_text())
            if val > 0:
                return val, "OK (H1)"

        return 0, "No localizado"
    except Exception as e:
        return 0, f"Error ({str(e)[:20]})"


def fetch_fotocasa(session, slug: str) -> tuple[int, str]:
    """Consulta Fotocasa usando la URL con /todas-las-zonas/l e inspeccionando JSON."""
    url = f"https://www.fotocasa.es/es/alquiler/viviendas/{slug}/todas-las-zonas/l"
    try:
        res = session.get(url, headers=HEADERS, impersonate="chrome120", timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            h1 = soup.find("h1")
            if h1 and parse_number(h1.text) > 0:
                return parse_number(h1.text), "OK (H1)"

            script_tag = soup.find("script", id="__NEXT_DATA__")
            if script_tag and script_tag.string:
                match = re.search(r'"totalResults":(\d+)', script_tag.string)
                if match:
                    return int(match.group(1)), "OK (NEXT_DATA)"
            return 0, "No localizado"
        return 0, f"HTTP {res.status_code}"
    except Exception as e:
        return 0, f"Error ({str(e)[:20]})"


def fetch_pisos_com(session, slug: str) -> tuple[int, str]:
    """Consulta Pisos.com con curl_cffi."""
    url = f"https://www.pisos.com/alquiler/pisos-{slug}/"
    try:
        res = session.get(url, headers=HEADERS, impersonate="chrome120", timeout=15)
        if res.status_code == 200:
            match = re.search(r"([\d\.]+)\s*resultados", res.text, re.IGNORECASE)
            if match:
                val = parse_number(match.group(1))
                if val > 0:
                    return val, "OK (Regex resultados)"

            soup = BeautifulSoup(res.text, "html.parser")
            elem = soup.select_one('[class*="title"]')
            if elem:
                val = parse_number(elem.text)
                if val > 0:
                    return val, "OK (DOM Class Title)"

            return 0, "No localizado en HTML"
        return 0, f"HTTP {res.status_code}"
    except Exception as e:
        return 0, f"Error ({str(e)[:20]})"


def fetch_habitaclia(session, slug_path: str) -> tuple[int, str]:
    """Consulta Habitaclia con curl_cffi utilizando el slug de provincia."""
    url = f"https://www.habitaclia.com/alquiler/viviendas/{slug_path}/s"
    try:
        res = session.get(url, headers=HEADERS, impersonate="chrome120", timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            h1 = soup.find("h1")
            if h1:
                val = parse_number(h1.text)
                if val > 0:
                    return val, "OK (H1)"

            match = re.search(
                r"([\d\.]+)\s*(?:casas|viviendas|pisos)", res.text, re.IGNORECASE
            )
            if match:
                val = parse_number(match.group(1))
                if val > 0:
                    return val, "OK (Regex)"
            return 0, "No localizado"
        return 0, f"HTTP {res.status_code}"
    except Exception as e:
        return 0, f"Error ({str(e)[:20]})"


def realizar_warmup_idealista(page):
    """
    Simula comportamiento humano realista para calentar la huella en Idealista.
    """
    print("\n [Idealista] Inicializando sesión y realizando warm-up humano...")
    page.goto("https://www.idealista.com/", wait_until="domcontentloaded", timeout=30000)
    time.sleep(random.uniform(2.0, 4.0))

    try:
        cookie_btn = page.query_selector("#didomi-notice-agree-button")
        if cookie_btn and cookie_btn.is_visible():
            print("   [Warm-up] Aceptando banner de cookies...")
            cookie_btn.click()
            time.sleep(random.uniform(1.5, 3.0))
    except Exception:
        pass

    try:
        page.mouse.move(random.randint(100, 500), random.randint(100, 500))
        page.evaluate(f"window.scrollBy(0, {random.randint(200, 500)});")
        time.sleep(random.uniform(1.5, 2.5))
        page.evaluate("window.scrollTo(0, 0);")
        time.sleep(random.uniform(1.0, 2.0))
    except Exception:
        pass

    print("   [Warm-up] Sesión lista.")

# ==============================================================================
# BUCLE PRINCIPAL DE EJECUCIÓN
# ==============================================================================

def cargar_historico(archivo_json: Path) -> dict:
    """Carga el histórico sin sustituirlo silenciosamente si está dañado."""
    try:
        with archivo_json.open("r", encoding="utf-8") as f:
            historico = json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as error:
        raise ValueError(f"El archivo {archivo_json} no contiene un JSON válido.") from error

    if not isinstance(historico, dict):
        raise ValueError(f"El archivo {archivo_json} debe contener un objeto JSON.")
    return historico


def guardar_historico(archivo_json: Path, historico: dict) -> None:
    """Guarda el histórico de forma atómica para no dejarlo truncado."""
    archivo_temporal = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=archivo_json.parent,
            prefix=f".{archivo_json.name}.",
            suffix=".tmp",
            delete=False,
        ) as f:
            archivo_temporal = Path(f.name)
            json.dump(historico, f, ensure_ascii=False, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(archivo_temporal, archivo_json)
    except OSError:
        if archivo_temporal is not None:
            archivo_temporal.unlink(missing_ok=True)
        raise


def main():
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    print("=" * 60)
    print(f" EJECUCIÓN CUENTACASAS - FECHA: {fecha_hoy}")
    print("=" * 60)

    resultados_totales = {}
    resultados_invalidos = []

    with Camoufox(
        headless=True,
        humanize=True
    ) as browser:
        
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="es-ES"
        )
        page = context.new_page()

        realizar_warmup_idealista(page)

        with requests.Session() as session:
            session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            })

            for idx, (provincia, slugs) in enumerate(PROVINCIAS_MAP.items(), start=1):
                print(f"\n=== [{idx:02d}] {provincia} ===")

                # 1. Idealista
                time.sleep(random.uniform(3.5, 6.5))
                i_total, i_estado = fetch_idealista(page, slugs["idealista"])

                # Si se detecta bloqueo, recargar pestaña, hacer warm-up y REINTENTAR la provincia
                if "403" in i_estado or "Bloqueo" in i_estado or "Captcha" in i_estado:
                    print("   [!] Bloqueo detectado en Idealista. Reiniciando pestaña y aplicando pausa de enfriamiento...")
                    time.sleep(random.uniform(12.0, 18.0))
                    
                    try:
                        page.close()
                    except Exception:
                        pass
                    
                    page = context.new_page()
                    realizar_warmup_idealista(page)

                    # REINTENTO TRAS RECUPERACIÓN
                    print(f"   [Idealista] Reintentando consulta para {provincia}...")
                    i_total, i_estado = fetch_idealista(page, slugs["idealista"])

                # 2. Fotocasa
                f_total, f_estado = fetch_fotocasa(session, slugs["fotocasa"])
                time.sleep(random.uniform(1.0, 2.0))

                # 3. Pisos.com
                p_total, p_estado = fetch_pisos_com(session, slugs["pisos"])
                time.sleep(random.uniform(1.0, 2.0))

                # 4. Habitaclia
                h_total, h_estado = fetch_habitaclia(session, slugs["habitaclia"])
                time.sleep(random.uniform(1.0, 2.0))

                resultados_portales = {
                    "idealista": (i_total, i_estado),
                    "fotocasa": (f_total, f_estado),
                    "pisos": (p_total, p_estado),
                    "habitaclia": (h_total, h_estado),
                }
                invalidos = [
                    f"{portal}=0 ({estado})"
                    for portal, (total, estado) in resultados_portales.items()
                    if not resultado_valido(total, estado)
                ]
                if invalidos:
                    resultados_invalidos.append(f"{provincia}: " + ", ".join(invalidos))
                    print(f"  [!] Datos no válidos; no se actualizará esta ejecución: {', '.join(invalidos)}")
                    continue

                # Estimación de oferta única
                max_oferta = max(i_total, f_total, p_total, h_total)
                oferta_estimada = int(max_oferta * 1.15) if max_oferta > 0 else 0

                # ASIGNACIÓN DIRECTA A LA ESTRUCTURA QUE SE GUARDA
                resultados_totales[provincia] = {
                    "idealista": i_total,
                    "fotocasa": f_total,
                    "pisos": p_total,
                    "habitaclia": h_total,
                    "oferta_estimada": oferta_estimada,
                }

                # IMPRESIÓN DIRECTA DESDE EL DICCIONARIO
                print(f"  [Idealista]  Total: {resultados_totales[provincia]['idealista']:<6} | Estado: {i_estado}")
                print(f"  [Fotocasa]   Total: {resultados_totales[provincia]['fotocasa']:<6} | Estado: {f_estado}")
                print(f"  [Pisos.com]  Total: {resultados_totales[provincia]['pisos']:<6} | Estado: {p_estado}")
                print(f"  [Habitaclia] Total: {resultados_totales[provincia]['habitaclia']:<6} | Estado: {h_estado}")
                print(f"  ---> Oferta única estimada: {resultados_totales[provincia]['oferta_estimada']}")

    if resultados_invalidos:
        print("\n[!] No se actualiza el JSON porque hay resultados con valor 0 y estado no OK:")
        for incidencia in resultados_invalidos:
            print(f"    - {incidencia}")
        raise SystemExit(2)

    # Guardar en JSON acumulativo
    archivo_json = Path(__file__).resolve().with_name("housing_counts.json")
    try:
        historico = cargar_historico(archivo_json)
        # Un diccionario por fecha garantiza un único registro diario:
        # una ejecución adicional del mismo día actualiza esa fecha.
        historico[fecha_hoy] = resultados_totales
        guardar_historico(archivo_json, historico)

        print("\n" + "=" * 60)
        print(f" Proceso finalizado. Datos de hoy ({fecha_hoy}) guardados.")
        print(f" Archivo actualizado: '{archivo_json}'.")
        print("=" * 60)
    except (OSError, ValueError) as error:
        print(f"\n[!] No se ha actualizado el JSON: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()