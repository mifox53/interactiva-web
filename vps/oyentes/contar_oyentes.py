#!/usr/bin/env python3
"""
Oyentes de iNteractiva: cuenta cuántas personas escuchan la radio por internet.

Lee los registros de conexiones al stream y deja un resumen en un JSON público
(/var/www/feed/oyentes.json, que Caddy sirve en /feed/oyentes.json). Ese resumen
es el que se usa para poner la cifra de oyentes en el kit para anunciantes.

Corre en el VPS cada hora (oyentes.timer). Solo usa la librería estándar de Python 3.
Configuración opcional en /etc/oyentes.env.

De dónde salen los datos:
- Caddy (las conexiones por https://interactiva.duckdns.org/live, que es lo que usa la
  página web): registro JSON en /var/log/caddy/radio.log. Hay que activarlo en el Caddyfile
  (ver README.md).
- Icecast (las conexiones directas al puerto 8000, por ejemplo desde apps de radio):
  /var/log/icecast2/access.log. Las que llegan desde 127.0.0.1 se ignoran, porque son las
  mismas que ya contó Caddy.

Qué cuenta:
- Una "sesión" es una conexión al stream de al menos MIN_SEGUNDOS (por defecto 30 s).
- "Oyentes distintos" se cuentan por dirección IP. Es una aproximación: una casa con varios
  equipos cuenta como uno, y un celular que cambia de red puede contar dos veces.
- Una conexión se registra cuando termina, así que quien está escuchando ahora mismo
  aparece en el resumen cuando se desconecta.
"""
import glob
import gzip
import json
import math
import os
import re
import tempfile
from collections import defaultdict
from datetime import datetime, timedelta, timezone

LOG_CADDY = os.environ.get("LOG_CADDY", "/var/log/caddy/radio*.log*")
LOG_ICECAST = os.environ.get("LOG_ICECAST", "/var/log/icecast2/access.log*")
SALIDA = os.environ.get("SALIDA", "/var/www/feed/oyentes.json")
MONTAJE = os.environ.get("MONTAJE", "/live")
MIN_SEGUNDOS = float(os.environ.get("MIN_SEGUNDOS", "30"))
# Venezuela no cambia de hora: UTC-4 todo el año.
ZONA = timezone(timedelta(hours=float(os.environ.get("ZONA_HORARIA_HORAS", "-4"))))
LOCALES = {"127.0.0.1", "::1", "localhost"}
ROBOTS = re.compile(r"bot|spider|crawl|curl|wget|python|uptime|monitor|check", re.I)

# Formato de access.log de Icecast: combined + duración en segundos al final.
LINEA_ICECAST = re.compile(
    r'^(?P<ip>\S+) \S+ \S+ \[(?P<fecha>[^\]]+)\] "(?P<metodo>\S+) (?P<ruta>\S+)[^"]*" '
    r'(?P<estado>\d{3}) \S+ "[^"]*" "(?P<agente>[^"]*)" (?P<duracion>\d+)'
)


def abrir(ruta):
    return gzip.open(ruta, "rt", encoding="utf-8", errors="replace") if ruta.endswith(".gz") \
        else open(ruta, encoding="utf-8", errors="replace")


def es_montaje(uri):
    ruta = uri.split("?", 1)[0].rstrip("/")
    return ruta == MONTAJE.rstrip("/")


def sesiones_caddy():
    for ruta in sorted(glob.glob(LOG_CADDY)):
        try:
            archivo = abrir(ruta)
        except OSError:
            continue
        with archivo:
            for linea in archivo:
                try:
                    d = json.loads(linea)
                except ValueError:
                    continue
                req = d.get("request") or {}
                if req.get("method") != "GET" or not es_montaje(req.get("uri", "")):
                    continue
                if d.get("status", 200) not in (200, 0):
                    continue
                agente = " ".join((req.get("headers") or {}).get("User-Agent", []))
                if ROBOTS.search(agente):
                    continue
                duracion = float(d.get("duration") or 0)
                fin = float(d.get("ts") or 0)
                ip = req.get("client_ip") or req.get("remote_ip") or ""
                if ip and fin:
                    yield ip, fin - duracion, fin, duracion


def sesiones_icecast():
    for ruta in sorted(glob.glob(LOG_ICECAST)):
        try:
            archivo = abrir(ruta)
        except OSError:
            continue
        with archivo:
            for linea in archivo:
                m = LINEA_ICECAST.match(linea)
                if not m or m["ip"] in LOCALES or m["metodo"] != "GET" or m["estado"] != "200":
                    continue
                if not es_montaje(m["ruta"]) or ROBOTS.search(m["agente"]):
                    continue
                try:
                    fin = datetime.strptime(m["fecha"], "%d/%b/%Y:%H:%M:%S %z").timestamp()
                except ValueError:
                    continue
                duracion = float(m["duracion"])
                yield m["ip"], fin - duracion, fin, duracion


def pico_simultaneo(sesiones):
    """Mayor cantidad de conexiones abiertas a la vez, y cuándo ocurrió."""
    marcas = []
    for _, ini, fin, _ in sesiones:
        marcas.append((ini, 1))
        marcas.append((fin, -1))
    marcas.sort(key=lambda x: (x[0], x[1]))
    actual = mejor = 0
    cuando = None
    for t, paso in marcas:
        actual += paso
        if actual > mejor:
            mejor, cuando = actual, t
    return mejor, cuando


def resumen(sesiones, desde, hasta):
    elegidas = [s for s in sesiones if desde <= s[2] < hasta]
    if not elegidas:
        return {"oyentes_distintos": 0, "sesiones": 0, "horas_escuchadas": 0,
                "minutos_por_sesion": 0, "pico_simultaneo": 0, "pico_fecha": None,
                "promedio_oyentes_diarios": 0}
    por_dia = defaultdict(set)
    for ip, _, fin, _ in elegidas:
        por_dia[datetime.fromtimestamp(fin, ZONA).date()].add(ip)
    # Si la radio empezó a registrar hace menos días que el periodo, se promedia solo sobre los días con registro.
    inicio = max(desde, min(s[2] for s in elegidas))
    dias = max(1, math.ceil((hasta - inicio) / 86400))
    segundos = sum(s[3] for s in elegidas)
    pico, cuando = pico_simultaneo(elegidas)
    return {
        "oyentes_distintos": len({s[0] for s in elegidas}),
        "sesiones": len(elegidas),
        "horas_escuchadas": round(segundos / 3600, 1),
        "minutos_por_sesion": round(segundos / 60 / len(elegidas), 1),
        "pico_simultaneo": pico,
        "pico_fecha": datetime.fromtimestamp(cuando, ZONA).isoformat(timespec="minutes") if cuando else None,
        "promedio_oyentes_diarios": round(sum(len(v) for v in por_dia.values()) / dias, 1),
    }


def main():
    ahora = datetime.now(ZONA)
    todas = [s for s in list(sesiones_caddy()) + list(sesiones_icecast()) if s[3] >= MIN_SEGUNDOS]

    # Día por día, los últimos 30 días (hora de Venezuela)
    hoy = ahora.date()
    diario = []
    for i in range(29, -1, -1):
        dia = hoy - timedelta(days=i)
        ini = datetime(dia.year, dia.month, dia.day, tzinfo=ZONA).timestamp()
        r = resumen(todas, ini, ini + 86400)
        diario.append({"fecha": dia.isoformat(), "oyentes": r["oyentes_distintos"], "horas": r["horas_escuchadas"]})

    fin = ahora.timestamp()
    datos = {
        "generado": ahora.isoformat(timespec="minutes"),
        "primer_registro": datetime.fromtimestamp(min(s[2] for s in todas), ZONA).date().isoformat() if todas else None,
        "ultimos_30_dias": resumen(todas, fin - 30 * 86400, fin),
        "ultimos_7_dias": resumen(todas, fin - 7 * 86400, fin),
        "por_dia": diario,
        "nota": f"Conexiones de al menos {int(MIN_SEGUNDOS)} s al stream {MONTAJE}. "
                "Oyentes distintos contados por dirección IP (aproximado).",
    }

    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(SALIDA), prefix=".oyentes-")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
    os.chmod(tmp, 0o644)
    os.replace(tmp, SALIDA)
    r = datos["ultimos_30_dias"]
    print(f"Últimos 30 días: {r['oyentes_distintos']} oyentes distintos, {r['horas_escuchadas']} h escuchadas, "
          f"pico de {r['pico_simultaneo']} a la vez.")


if __name__ == "__main__":
    main()
