# Vitrina de Instagram en el VPS

Frank publica los videos de emprendedores y empresas en Instagram (vía Meta, como siempre) y en
TikTok aparte. Este script, en el VPS, lee cada 30 minutos los últimos videos del Instagram de la
emisora y los deja en `https://interactiva.duckdns.org/feed/vitrina.json`. La web los muestra sola
en la sección **Vitrina** (portada y `/vitrina/`). Nadie tiene que tocar la web.

## 1. Requisitos en Instagram

- La cuenta de Instagram de la emisora debe ser **profesional** (Empresa o Creador).
  Instagram → Configuración → Tipo de cuenta y herramientas → Cambiar a cuenta profesional.

## 2. Sacar el token (una sola vez, ~15 minutos, con Frank)

1. Entrar a https://developers.facebook.com con una cuenta de Facebook → **Mis apps → Crear app**.
2. Caso de uso: **Administrar mensajes y contenido en Instagram** (o tipo *Business*). Nombre: `Vitrina iNteractiva`.
3. En la app: **Instagram → Configuración de la API con inicio de sesión de Instagram**.
4. En **Roles de la app → Roles → Evaluadores de Instagram**, agregar el usuario de Instagram de la
   emisora. Frank acepta la invitación en Instagram: Configuración → Apps y sitios web → Invitaciones de evaluador.
5. Volver a **Generar tokens de acceso → Agregar cuenta**, iniciar sesión con el Instagram de la
   emisora y copiar el token que aparece (empieza por `IG...`). Ese token dura 60 días; el script
   lo renueva solo cada semana.

La app puede quedarse en **modo desarrollo**: solo lee la cuenta de la emisora, no hace falta
revisión de Meta. Permiso necesario: `instagram_business_basic`.

## 3. Instalar en el VPS

Desde la carpeta del repositorio en tu PC:

```bash
scp vps/instagram-feed/actualizar_vitrina.py vps/instagram-feed/instagram-vitrina.* root@64.176.5.192:/tmp/
```

En el VPS:

```bash
ssh root@64.176.5.192

mkdir -p /opt/instagram-vitrina /var/lib/instagram-vitrina /var/www/feed
mv /tmp/actualizar_vitrina.py /opt/instagram-vitrina/
mv /tmp/instagram-vitrina.service /tmp/instagram-vitrina.timer /etc/systemd/system/
mv /tmp/instagram-vitrina.env /etc/instagram-vitrina.env

# Pegar el token (una sola línea) y guardar: Ctrl+O, Enter, Ctrl+X
nano /var/lib/instagram-vitrina/token
chmod 600 /var/lib/instagram-vitrina/token

systemctl daemon-reload
systemctl start instagram-vitrina.service      # primera corrida a mano
journalctl -u instagram-vitrina -n 20 --no-pager   # debe decir "N publicaciones guardadas"
systemctl enable --now instagram-vitrina.timer
```

## 4. Publicar el JSON con Caddy

Editar `/etc/caddy/Caddyfile` para que `/feed/` se sirva desde la carpeta y todo lo demás siga
yendo a Icecast. Si hoy dice algo como:

```
interactiva.duckdns.org {
    reverse_proxy localhost:8000
}
```

dejarlo así (lo que hoy está dentro del bloque va dentro de `handle { … }`, tal cual):

```
interactiva.duckdns.org {
    handle_path /feed/* {
        root * /var/www/feed
        header Access-Control-Allow-Origin "*"
        header Cache-Control "public, max-age=300"
        file_server
    }
    handle {
        reverse_proxy localhost:8000
    }
}
```

```bash
caddy validate --config /etc/caddy/Caddyfile && systemctl reload caddy
curl -s https://interactiva.duckdns.org/feed/vitrina.json | head -c 400
```

Comprobar también que la radio sigue sonando en `https://interactiva.duckdns.org/live`.

## Ajustes

En `/etc/instagram-vitrina.env`:

- `HASHTAG=interactivapublicidad` → en la web solo salen los posts que lleven `#interactivapublicidad`.
  Vacío = salen todos los videos.
- `SOLO_VIDEOS=0` → incluir también fotos.
- `MAXIMO=24` → cuántos se guardan.

Después de cambiar algo: `systemctl start instagram-vitrina.service`.

## Si algo falla

- `journalctl -u instagram-vitrina -n 50 --no-pager` muestra el error.
- Si el token se venció (más de 60 días sin renovarse, por ejemplo con el VPS apagado), repetir el paso 2
  y pegar el token nuevo en `/var/lib/instagram-vitrina/token`.
- Mientras haya un error, la web sigue mostrando la última lista buena.
