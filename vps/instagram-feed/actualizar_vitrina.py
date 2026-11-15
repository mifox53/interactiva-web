#!/usr/bin/env python3
"""
Vitrina de iNteractiva: lee los últimos videos del Instagram de la emisora
y los deja en un JSON público que la página web muestra sola.

Corre en el VPS cada 30 minutos (instagram-vitrina.timer). Solo usa la
librería estándar de Python 3. Configuración en /etc/instagram-vitrina.env.

- Token: /var/lib/instagram-vitrina/token (se renueva solo cada 7 días;
  un token de Instagram dura 60 días si no se renueva).
- Salida: /var/www/feed/vitrina.json (Caddy la sirve en /feed/vitrina.json).
- Si Instagram falla, deja el JSON anterior intacto: la web nunca se queda vacía por un error.
"""
import json
import os
import sys
import tempfile
import time
import urllib.parse
import urllib.request

API = "https://graph.instagram.com"
TOKEN_ARCHIVO = os.environ.get("TOKEN_ARCHIVO", "/var/lib/instagram-vitrina/token")
SALIDA = os.environ.get("SALIDA", "/var/www/feed/vitrina.json")
# Si se pone un hashtag (sin #), solo salen en la web las publicaciones que lo lleven.
HASHTAG = os.environ.get("HASHTAG", "").strip().lstrip("#").lower()
# 1 = solo videos/reels; 0 = también fotos y carruseles.
SOLO_VIDEOS = os.environ.get("SOLO_VIDEOS", "1") == "1"
MAXIMO = int(os.environ.get("MAXIMO", "24"))
RENOVAR_CADA = 7 * 24 * 3600


def pedir(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)


def leer_token():
    with open(TOKEN_ARCHIVO, encoding="utf-8") as f:
        return f.read().strip()


def guardar_atomico(ruta, texto, modo=0o644):
    carpeta = os.path.dirname(ruta)
    os.makedirs(carpeta, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=carpeta)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(texto)
    os.chmod(tmp, modo)
    os.replace(tmp, ruta)


def renovar_si_toca(token):
    """Renueva el token de larga duración (debe tener al menos 24 h). Devuelve el token vigente."""
    edad = time.time() - os.path.getmtime(TOKEN_ARCHIVO)
    if edad < RENOVAR_CADA:
        return token
    q = urllib.parse.urlencode({"grant_type": "ig_refresh_token", "access_token": token})
    try:
        nuevo = pedir(f"{API}/refresh_access_token?{q}")["access_token"]
    except Exception as e:  # si falla, se sigue con el actual y se reintenta en la próxima corrida
        print(f"Aviso: no se pudo renovar el token: {e}", file=sys.stderr)
        return token
    guardar_atomico(TOKEN_ARCHIVO, nuevo + "\n", 0o600)
    print("Token renovado.")
    return nuevo


def lleva_hashtag(texto):
    if not HASHTAG:
        return True
    palabras = {p.strip(".,;:!¡?¿()").lower() for p in texto.split()}
    return f"#{HASHTAG}" in palabras


def main():
    token = renovar_si_toca(leer_token())
    campos = "id,caption,media_type,media_product_type,media_url,thumbnail_url,permalink,timestamp"
    url = f"{API}/me/media?" + urllib.parse.urlencode({"fields": campos, "limit": 50, "access_token": token})

    publicaciones = []
    paginas = 0
    while url and len(publicaciones) < MAXIMO and paginas < 4:
        datos = pedir(url)
        paginas += 1
        for m in datos.get("data", []):
            es_video = m.get("media_type") == "VIDEO"
            if SOLO_VIDEOS and not es_video:
                continue
            texto = m.get("caption") or ""
            if not lleva_hashtag(texto):
                continue
            publicaciones.append({
                "id": m["id"],
                "tipo": "video" if es_video else "imagen",
                "video": m.get("media_url") if es_video else "",
                "imagen": m.get("thumbnail_url") if es_video else m.get("media_url"),
                "enlace": m.get("permalink"),
                "texto": texto,
                "fecha": m.get("timestamp"),
            })
            if len(publicaciones) >= MAXIMO:
                break
        url = datos.get("paging", {}).get("next")

    salida = {
        "actualizado": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "publicaciones": publicaciones,
    }
    guardar_atomico(SALIDA, json.dumps(salida, ensure_ascii=False))
    print(f"{len(publicaciones)} publicaciones guardadas en {SALIDA}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
