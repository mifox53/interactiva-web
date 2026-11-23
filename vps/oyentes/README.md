# Oyentes del stream en el VPS

Cuenta cuántas personas escuchan la radio por internet y deja el resumen en
`https://interactiva.duckdns.org/feed/oyentes.json`, actualizado cada hora. Es la cifra de
oyentes que va en el kit para anunciantes (`src/datos/kit.json`).

Qué trae el resumen (últimos 30 y últimos 7 días):

| Campo | Qué es |
|---|---|
| `oyentes_distintos` | Personas distintas que escucharon, contadas por dirección IP (aproximado) |
| `promedio_oyentes_diarios` | Oyentes distintos por día, en promedio |
| `horas_escuchadas` | Total de horas que se escuchó la radio, sumando a todos |
| `minutos_por_sesion` | Cuánto dura en promedio cada vez que alguien se conecta |
| `pico_simultaneo` | Máximo de personas escuchando a la vez, y cuándo (`pico_fecha`) |
| `por_dia` | Oyentes y horas de cada uno de los últimos 30 días |

Solo cuenta conexiones de 30 segundos o más, y no cuenta robots ni la conexión de BUTT.

## 1. Activar el registro de conexiones en Caddy

Icecast ve todas las conexiones de la página como si vinieran de `127.0.0.1` (porque pasan por
Caddy), así que el dato bueno lo tiene Caddy. Hay que pedirle que anote las conexiones a `/live`.

En `/etc/caddy/Caddyfile`, dentro del bloque `interactiva.duckdns.org { … }`, agregar arriba:

```
interactiva.duckdns.org {
    log {
        output file /var/log/caddy/radio.log {
            roll_size 20MiB
            roll_keep 10
            roll_keep_for 2160h
        }
    }
    @no_radio not path /live /live/*
    log_skip @no_radio

    handle_path /feed/* {
        … (lo que ya estaba)
    }
    handle {
        reverse_proxy localhost:8000
    }
}
```

`log_skip` hace que solo se anoten las conexiones a la radio (no cada consulta del título de la
canción). Guardar y aplicar:

```bash
mkdir -p /var/log/caddy && chown caddy:caddy /var/log/caddy
caddy validate --config /etc/caddy/Caddyfile && systemctl reload caddy
```

Si `caddy validate` se queja de `log_skip`, la versión de Caddy es anterior a la 2.8: cambiar
`log_skip @no_radio` por `skip_log @no_radio`.

Comprobar que la radio sigue sonando en `https://interactiva.duckdns.org/live`. Al cerrar el
reproductor, debe aparecer una línea en `/var/log/caddy/radio.log`.

## 2. Instalar el conteo

Desde la carpeta del repositorio en tu PC:

```bash
scp vps/oyentes/contar_oyentes.py vps/oyentes/oyentes.* root@64.176.5.192:/tmp/
```

En el VPS:

```bash
ssh root@64.176.5.192

mkdir -p /opt/oyentes /var/www/feed
mv /tmp/contar_oyentes.py /opt/oyentes/
mv /tmp/oyentes.service /tmp/oyentes.timer /etc/systemd/system/
mv /tmp/oyentes.env /etc/oyentes.env

systemctl daemon-reload
systemctl start oyentes.service                 # primera corrida a mano
journalctl -u oyentes -n 5 --no-pager           # debe decir "Últimos 30 días: …"
systemctl enable --now oyentes.timer
```

Ver el resultado: `https://interactiva.duckdns.org/feed/oyentes.json` (la carpeta `/feed/` ya la
sirve Caddy desde la instalación de la Vitrina).

## Cosas a tener en cuenta

- Las cifras empiezan a contar desde que se activa el paso 1. Los primeros días serán pocos datos;
  conviene esperar al menos un mes antes de ponerlas en el kit.
- Una conexión se anota cuando termina: quien está escuchando ahora aparece cuando se desconecta.
- Contar por IP es una aproximación: una casa con varios equipos cuenta como uno, y un celular
  que cambia de red puede contar dos veces.
- El oyente de la radio por FM (89.7) no pasa por aquí: esto es solo la radio por internet.
- Si algo falla: `journalctl -u oyentes -n 50 --no-pager`.
