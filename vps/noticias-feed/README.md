# Titulares automáticos («Venezuela ahora»)

Un programa en el VPS que, cada 3 horas, lee los feeds RSS de medios venezolanos, descarta lo que
no va (política, sucesos, religión, economía política) y deja los titulares en
`https://interactiva.duckdns.org/feed/noticias.json`. La página los muestra sola, con Mérida
primero. No cuesta nada: usa el mismo VPS y la misma carpeta `/feed/` que la Vitrina.

Qué se publica de cada nota: **el titular tal como lo escribió el medio, el nombre del medio, la
fecha y el enlace**. Nada de resúmenes ni fotos: al tocar el titular, el lector va a la nota en el
sitio del medio.

## Archivos

| Archivo | Para qué |
|---|---|
| `actualizar_noticias.py` | El programa (solo Python 3, sin instalar nada) |
| `fuentes.json` | Los feeds que lee. Para quitar uno: `"activo": false` |
| `filtros.json` | Palabras que bloquean, temas permitidos y lugares para saber la región |
| `noticias-feed.service` / `.timer` | Lo corren cada 3 horas |
| `noticias-feed.env` | Opciones (días hacia atrás, máximos) |

## Instalar

Desde la carpeta del repositorio en tu PC:

```bash
scp vps/noticias-feed/* root@64.176.5.192:/tmp/
```

En el VPS:

```bash
ssh root@64.176.5.192

mkdir -p /opt/noticias-feed /etc/noticias-feed /var/www/feed
mv /tmp/actualizar_noticias.py /tmp/fuentes.json /tmp/filtros.json /opt/noticias-feed/
mv /tmp/noticias-feed.service /tmp/noticias-feed.timer /etc/systemd/system/
mv /tmp/noticias-feed.env /etc/noticias-feed.env
touch /etc/noticias-feed/bloqueadas.txt
rm -f /tmp/README.md

# 1) Prueba: muestra qué publicaría y qué descarta (y por qué), sin escribir nada
python3 -I /opt/noticias-feed/actualizar_noticias.py --probar

# 2) Si se ve bien, activarlo
systemctl daemon-reload
systemctl start noticias-feed.service
systemctl enable --now noticias-feed.timer
```

Ver el resultado: `https://interactiva.duckdns.org/feed/noticias.json`. La página lo toma sola:
en la portada, la sección «Venezuela ahora» muestra los titulares en vez de la lista de la semana.

En la prueba, las fuentes con ✗ no respondieron (dirección del feed cambiada o sitio caído). Hay
que corregir su `feed` en `fuentes.json` o poner `"activo": false`. Las 10 fuentes respondieron en
la primera prueba (23 de noviembre de 2026).

## Esconder un titular que se coló

Dos formas:

1. **Al momento, en el VPS:** agregar el enlace de la nota en una línea de
   `/etc/noticias-feed/bloqueadas.txt` y correr `systemctl start noticias-feed.service`.
   También se puede poner una palabra (sin `http`) para bloquear todo titular que la tenga.
2. **Desde la página:** agregar el enlace en `src/datos/titulares.json` → `bloquear`. Se esconde
   cuando Render vuelva a publicar el sitio.

Si una palabra deja pasar cosas que no van, agrégala a `bloquear` en `filtros.json` y vuelve a
copiar el archivo al VPS (`scp vps/noticias-feed/filtros.json root@64.176.5.192:/opt/noticias-feed/`).

## Actualizar el programa o el filtro

Cuando cambien `filtros.json`, `fuentes.json` o el programa en el repositorio, en PowerShell:

```
ssh root@64.176.5.192 'set -e; B=https://raw.githubusercontent.com/mifox53/interactiva-web/main/vps/noticias-feed; cd /opt/noticias-feed; for f in actualizar_noticias.py fuentes.json filtros.json; do curl -fsSLO $B/$f; done; python3 -I actualizar_noticias.py --probar; systemctl start noticias-feed.service; echo LISTO'
```

Muestra la prueba y deja publicados los titulares nuevos al momento.

## Reglas de uso de las fuentes

- Solo titular, medio, fecha y enlace. Nunca copiar el texto de la nota ni sus fotos.
- Si un medio pide que no lo incluyamos: `"activo": false` en `fuentes.json` y listo.
- Lo ideal es pedir permiso por escrito a los medios (Alianza Nacional de Medios, Diario de Los
  Andes); a ellos les conviene porque les mandamos lectores.

## Si algo falla

```bash
journalctl -u noticias-feed -n 50 --no-pager
```
