#!/usr/bin/env python3
"""
Titulares automáticos de iNteractiva («Venezuela ahora»).

Cada 3 horas lee los feeds RSS de fuentes.json, descarta lo que no va (política, sucesos,
religión, economía política: ver filtros.json), detecta la región de cada titular y deja la
lista en /var/www/feed/noticias.json, que Caddy sirve en /feed/noticias.json y la página lee sola.

Solo se publica el titular tal como lo escribió el medio, el nombre del medio, la fecha y el
enlace a la nota: ni resúmenes ni fotos. El lector siempre termina en el sitio del medio.

Uso:
  python3 actualizar_noticias.py            actualiza el JSON
  python3 actualizar_noticias.py --probar   muestra qué publicaría y qué descarta, sin escribir

Configuración opcional en /etc/noticias-feed.env (ver noticias-feed.env).
Para esconder un titular al momento: poner su enlace (o una palabra) en una línea de
/etc/noticias-feed/bloqueadas.txt. También se puede esconder desde la página:
src/datos/titulares.json → bloquear.
Solo usa la librería estándar de Python 3.
"""
import email.utils
import html
import json
import os
import re
import sys
import tempfile
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

CARPETA = os.path.dirname(os.path.abspath(__file__))
FUENTES = os.environ.get("FUENTES", os.path.join(CARPETA, "fuentes.json"))
FILTROS = os.environ.get("FILTROS", os.path.join(CARPETA, "filtros.json"))
BLOQUEADAS = os.environ.get("BLOQUEADAS", "/etc/noticias-feed/bloqueadas.txt")
SALIDA = os.environ.get("SALIDA", "/var/www/feed/noticias.json")
DIAS = int(os.environ.get("DIAS", "7"))
MAX_TOTAL = int(os.environ.get("MAX_TOTAL", "40"))
MAX_POR_FUENTE = int(os.environ.get("MAX_POR_FUENTE", "8"))
AGENTE = "iNteractiva-titulares/1.0 (+https://interactiva.com.ve)"
ZONA = timezone(timedelta(hours=-4))  # Venezuela

NS = {"atom": "http://www.w3.org/2005/Atom", "dc": "http://purl.org/dc/elements/1.1/"}


def normal(texto):
    """minúsculas, sin acentos, espacios simples (la ñ queda como n)."""
    t = unicodedata.normalize("NFD", texto or "")
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", t.lower()).strip()


def sin_html(texto):
    return re.sub(r"<[^>]+>", " ", html.unescape(texto or ""))


def patron(lista):
    """Una expresión que detecta cualquiera de las palabras como comienzo de palabra."""
    partes = sorted({normal(p) for p in lista if p.strip()}, key=len, reverse=True)
    if not partes:
        return None
    return re.compile(r"(?<![a-z0-9])(" + "|".join(re.escape(p) for p in partes) + ")")


def cargar_bloqueadas():
    try:
        with open(BLOQUEADAS, encoding="utf-8") as f:
            lineas = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    except OSError:
        return set(), None
    enlaces = {l for l in lineas if l.startswith("http")}
    palabras = [l for l in lineas if not l.startswith("http")]
    return enlaces, patron(palabras)


def descargar(url):
    req = urllib.request.Request(url, headers={"User-Agent": AGENTE, "Accept": "application/rss+xml, application/xml, text/xml"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read()


def fecha_de(texto):
    if not texto:
        return None
    try:
        d = email.utils.parsedate_to_datetime(texto)
    except (TypeError, ValueError):
        try:
            d = datetime.fromisoformat(texto.strip().replace("Z", "+00:00"))
        except ValueError:
            return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def leer_feed(datos):
    """Devuelve [{titulo, enlace, fecha, categorias, texto}] de un RSS 2.0 o Atom."""
    raiz = ET.fromstring(datos)
    items = []
    for it in raiz.iter("item"):
        items.append({
            "titulo": html.unescape((it.findtext("title") or "").strip()),
            "enlace": (it.findtext("link") or "").strip(),
            "fecha": fecha_de(it.findtext("pubDate") or it.findtext("dc:date", namespaces=NS)),
            "categorias": [c.text.strip() for c in it.findall("category") if c.text],
            "texto": sin_html(it.findtext("description")),
        })
    for it in raiz.iter("{%s}entry" % NS["atom"]):
        enlace = it.find("atom:link[@rel='alternate']", NS)
        if enlace is None:
            enlace = it.find("atom:link", NS)
        items.append({
            "titulo": html.unescape((it.findtext("atom:title", namespaces=NS) or "").strip()),
            "enlace": enlace.get("href", "").strip() if enlace is not None else "",
            "fecha": fecha_de(it.findtext("atom:published", namespaces=NS) or it.findtext("atom:updated", namespaces=NS)),
            "categorias": [c.get("term", "") for c in it.findall("atom:category", NS)],
            "texto": sin_html(it.findtext("atom:summary", namespaces=NS)),
        })
    return items


class Filtro:
    def __init__(self, reglas):
        self.bloquear = patron(reglas["bloquear"])
        self.regex = [re.compile(r) for r in reglas.get("bloquear_regex", [])]
        self.secciones = {normal(s) for s in reglas.get("secciones_bloqueadas", [])}
        self.temas = [(cat, patron(palabras)) for cat, palabras in reglas["temas"].items()]
        # lugares: (region, nombre visible, patrón), en el orden del archivo (nacional primero)
        self.lugares = []
        for region, nombres in reglas["lugares"].items():
            for nombre in nombres:
                self.lugares.append((region, nombre, patron([nombre])))

    def motivo_descarte(self, item, ignorar=()):
        cats = {normal(c) for c in item["categorias"]} - {normal(c) for c in ignorar}
        if cats & self.secciones:
            return "sección: " + ", ".join(sorted(cats & self.secciones))
        titulo = normal(item["titulo"])
        for r in self.regex:
            if r.search(titulo):
                return "forma de declaración u opinión"
        todo = normal(" ".join([item["titulo"], item["texto"], " ".join(item["categorias"])]))
        m = self.bloquear.search(todo) if self.bloquear else None
        if m:
            return "palabra: " + m.group(1)
        return None

    def tema(self, item):
        cuerpo = normal(" ".join([item["titulo"], " ".join(item["categorias"])]))
        for cat, p in self.temas:
            if p and p.search(cuerpo):
                return cat
        return None

    def lugar(self, item, region_fuente):
        """Busca primero en el titular, luego en las categorías y por último en el resumen."""
        for texto in (item["titulo"], " ".join(item["categorias"]), item["texto"][:400]):
            t = normal(texto)
            for region, nombre, p in self.lugares:
                if p.search(t):
                    return region, ("" if region == "nacional" else nombre)
        return region_fuente, ""


def main():
    probar = "--probar" in sys.argv
    with open(FUENTES, encoding="utf-8") as f:
        fuentes = [x for x in json.load(f)["fuentes"] if x.get("activo", True)]
    with open(FILTROS, encoding="utf-8") as f:
        filtro = Filtro(json.load(f))
    enlaces_bloqueados, palabras_bloqueadas = cargar_bloqueadas()

    ahora = datetime.now(timezone.utc)
    limite = ahora - timedelta(days=DIAS)
    elegidos, vistos_enlace, vistos_titulo = [], set(), set()
    resumen = []

    for fuente in fuentes:
        nombre, url = fuente["nombre"], fuente["feed"]
        try:
            items = leer_feed(descargar(url))
        except Exception as e:  # una fuente caída no detiene a las demás
            resumen.append(f"  ✗ {nombre} ({url}): {e.__class__.__name__}: {e}")
            continue
        tomados, descartes = 0, []
        for item in sorted(items, key=lambda i: i["fecha"] or limite, reverse=True):
            if not item["titulo"] or not item["enlace"].startswith("http"):
                continue
            if not item["fecha"] or item["fecha"] < limite:
                continue
            clave_titulo = normal(item["titulo"])[:70]
            if item["enlace"] in vistos_enlace or clave_titulo in vistos_titulo:
                continue
            motivo = filtro.motivo_descarte(item, fuente.get("ignorar_secciones", []))
            if not motivo and item["enlace"] in enlaces_bloqueados:
                motivo = "bloqueado a mano"
            if not motivo and palabras_bloqueadas and palabras_bloqueadas.search(normal(item["titulo"])):
                motivo = "palabra bloqueada a mano"
            categoria = filtro.tema(item)
            if not motivo and not categoria:
                if fuente.get("seguro"):
                    categoria = fuente.get("categoria", "cultura")
                else:
                    motivo = "sin tema permitido"
            if motivo:
                descartes.append((item["titulo"], motivo))
                continue
            if tomados >= MAX_POR_FUENTE:
                continue
            region, lugar = filtro.lugar(item, fuente.get("region", "nacional"))
            elegidos.append({
                "titulo": item["titulo"],
                "enlace": item["enlace"],
                "fuente": nombre,
                "fecha": item["fecha"].astimezone(ZONA).isoformat(timespec="minutes"),
                "region": region,
                "lugar": lugar,
                "categoria": categoria,
            })
            vistos_enlace.add(item["enlace"])
            vistos_titulo.add(clave_titulo)
            tomados += 1
        resumen.append(f"  ✓ {nombre} ({url}): {len(items)} en el feed, {tomados} publicados, {len(descartes)} descartados")
        if probar:
            for titulo, motivo in descartes[:15]:
                resumen.append(f"      descartado [{motivo}] {titulo}")

    elegidos.sort(key=lambda x: x["fecha"], reverse=True)
    elegidos = elegidos[:MAX_TOTAL]

    print(f"Titulares: {len(elegidos)} publicados de {len(fuentes)} fuentes")
    print("\n".join(resumen))
    if probar:
        print("\nLo que se publicaría:")
        for e in elegidos:
            print(f"  [{e['region']}/{e['categoria']}] {e['titulo']} — {e['fuente']} {e['fecha'][:10]} {e['lugar']}")
        return

    datos = {"generado": ahora.astimezone(ZONA).isoformat(timespec="minutes"), "titulares": elegidos}
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(SALIDA), prefix=".noticias-")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
    os.chmod(tmp, 0o644)
    os.replace(tmp, SALIDA)


if __name__ == "__main__":
    main()
