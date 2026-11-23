#!/bin/bash
# Hace que Caddy sirva la carpeta /var/www/feed en https://interactiva.duckdns.org/feed/
# (titulares, vitrina, oyentes) sin tocar lo demás: la radio sigue yendo a Icecast.
#
# Uso en el VPS (se puede repetir sin problema):
#   bash caddy-feed.sh
#
# Qué hace:
#   1. Si el Caddyfile ya tiene «handle_path /feed/*», no cambia nada.
#   2. Si no, guarda una copia (/etc/caddy/Caddyfile.antes-feed) y agrega el bloque de /feed/
#      justo después de la línea «interactiva.duckdns.org {».
#   3. Valida la configuración nueva. Si no es válida, vuelve a dejar la anterior.
#   4. Recarga Caddy (sin cortar la transmisión) y comprueba el feed y la radio.
set -euo pipefail

CF=/etc/caddy/Caddyfile
mkdir -p /var/www/feed

if grep -q 'handle_path /feed/\*' "$CF"; then
  echo "Caddy ya tenía /feed/ configurado: no cambié nada."
else
  cp "$CF" "$CF.antes-feed"
  python3 -I - "$CF" <<'PY'
import re
import sys

ruta = sys.argv[1]
with open(ruta, encoding="utf-8") as f:
    lineas = f.read().split("\n")
sitio = re.compile(r"\s*(https?://)?interactiva\.duckdns\.org(:\d+)?\s*\{\s*$")
donde = [i for i, l in enumerate(lineas) if sitio.match(l)]
if len(donde) != 1:
    sys.exit("No encontré una sola línea «interactiva.duckdns.org {» en el Caddyfile: no cambié nada.")
bloque = [
    "\t# Archivos que publica el VPS (titulares, vitrina, oyentes)",
    "\thandle_path /feed/* {",
    "\t\troot * /var/www/feed",
    '\t\theader Access-Control-Allow-Origin "*"',
    '\t\theader Cache-Control "public, max-age=300"',
    "\t\tfile_server",
    "\t}",
]
lineas[donde[0] + 1:donde[0] + 1] = bloque
with open(ruta, "w", encoding="utf-8") as f:
    f.write("\n".join(lineas))
PY
  if ! caddy validate --config "$CF" --adapter caddyfile > /tmp/caddy-validar.log 2>&1; then
    cp "$CF.antes-feed" "$CF"
    echo "La configuración nueva no pasó la validación: dejé el Caddyfile como estaba."
    tail -n 5 /tmp/caddy-validar.log
    exit 1
  fi
  systemctl reload caddy
  echo "Listo: Caddy ahora sirve /feed/ (copia del archivo anterior en $CF.antes-feed)."
fi

sleep 2
curl -s -o /dev/null -w 'feed de titulares: %{http_code} (200 = bien)\n' https://interactiva.duckdns.org/feed/noticias.json
curl -s -o /dev/null -w 'radio (Icecast): %{http_code} (200 = bien)\n' https://interactiva.duckdns.org/status-json.xsl
