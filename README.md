# iNteractiva 89.7 FM — sitio web

Sitio de la emisora, hecho con [Astro](https://astro.build). El diseño está separado del contenido:
para cambiar algo casi siempre se toca **un solo archivo pequeño**.

## Dónde se cambia cada cosa

| Quiero cambiar… | Archivo |
|---|---|
| Nombre, lema, slogan, logo, WhatsApp, correo, redes, reproductor | `src/datos/sitio.json` |
| El archivo del logo | `public/img/logo.webp` (o cambiar la ruta en `sitio.json`) |
| Patrocinantes: agregar, quitar, rotar, fechas, espacio que ocupan | `src/datos/patrocinantes.json` |
| Programación | `src/datos/programacion.json` |
| Noticias | un archivo `.md` por noticia en `src/contenido/noticias/` |
| Artistas | un archivo `.md` por artista en `src/contenido/artistas/` (ver sección Artistas) |
| Artista de la semana | `src/datos/artista-semana.json` |
| Eventos y saludos | un archivo `.md` por evento en `src/contenido/eventos/` |
| Vitrina (videos de emprendedores) | se llena sola desde Instagram; ver sección Vitrina |
| Texto de "Nosotros" | `src/datos/sitio.json` → `nosotros` |
| Marca de agua de la portada (dibujo de fondo y foto con su letrero, con fechas) | `src/datos/marca-agua.json` |
| Planes y formulario de anunciantes | `src/pages/anunciate.astro` |
| Kit para anunciantes: cifras, paquetes y precios (página `/anunciantes/`) | `src/datos/kit.json` |
| Analítica (visitas y clics) | `src/datos/sitio.json` → `analitica.goatcounter` |
| Colores y estilos | `src/estilos/global.css` |

Los archivos `_plantilla.md` son modelos para copiar; no se publican.

## Reglas del contenido

- El nombre se escribe siempre **iNteractiva 89.7 FM**.
- Noticias («Venezuela ahora»): Mérida primero y lo mejor de las regiones. Temas: agricultura, café,
  cultura, música, turismo, eventos, deportes, ciudad y clima y vías. **Nada de política ni de
  religión.** Resumen con palabras propias y enlace a la fuente. Fotos propias o con permiso.
  Titulares automáticos de las regiones: `vps/noticias-feed/README.md` (bloquear uno:
  `src/datos/titulares.json`). Destacadas semanales, fuentes y criterios: `docs/noticias.md`.
- Una noticia o evento con `borrador: true` no aparece en el sitio. Se publica al cambiarlo a `false`.
- Lo pagado lleva `patrocinado: true` y sale con la etiqueta "Patrocinado".

## Artistas

Cada artista es un archivo `.md` en `src/contenido/artistas/` (modelo: `_plantilla.md`). Campos:
`nombre`, `tipo` (local/internacional), `genero`, `foto`, `saludo` (enlace a su video de saludo),
`instagram` (usuario sin @), `seguidores` (número), `orden` (solo para forzar a alguien arriba) y
`destacado`. El texto debajo del `---` es una biografía corta opcional.

- **Orden**: por `orden` si se fijó; luego los que tienen foto; luego de más a menos `seguidores`;
  luego por nombre. Hoy tienen `orden` fijo los 11 primeros, en este orden: Liz, Reynaldo Armas,
  Jessi Uribe & El Carteluo, Oscar D'León, Grupo Niche, Guaco, Rummy Olivo, Magic Juan, Miguel Moly,
  Scarlett Linares y Los Melódicos. Para mover a alguien arriba, dale un `orden` menor; para sacarlo
  de la lista fija, bórrale la línea `orden`. Los artistas sin foto quedan siempre de últimos.
- **Portada (arriba)**: 4 artistas con foto, al azar, cambian cada 10 minutos (`MINUTOS` en `src/pages/index.astro`).
- **Artista de la semana**: bloque grande en la sección Artistas de la portada. Se fija en
  `src/datos/artista-semana.json` (artista, desde, hasta, motivo). Si no hay ninguno vigente, rota solo
  cada semana por turnos entre los artistas con foto.
- **Sección Artistas de la portada**: muestra como máximo 8 (`EN_PORTADA`), primero los que tienen foto.
- **Galería completa** `/artistas/`: todos, con filtros por tipo y género. Géneros usados:
  Salsa, Merengue, Llanera y criolla, Rock, Pop y balada, Urbano, Tropical, Flamenco.
- **Página por artista** `/artistas/<archivo>/`: foto, saludo, Instagram, seguidores, biografía y sus
  eventos de la agenda (los eventos se enlazan por el campo `artista` con el mismo nombre). Ese enlace
  es el que cada artista puede compartir en sus redes.

Las fotos van en `public/img/artistas/`, verticales y de menos de 200 KB. Un artista sin foto aparece en
la galería con un fondo de color, pero no entra en la portada hasta tener foto.

## Vitrina

Videos de emprendedores y empresas que la emisora publica en Instagram. **No se edita en la web**:
el VPS lee el Instagram cada 30 minutos y deja la lista en `sitio.json` → `vitrina.feed`
(`https://interactiva.duckdns.org/feed/vitrina.json`). La portada muestra `vitrina.enPortada`
videos y `/vitrina/` muestra todos. Si la lista no está disponible, sale "Muy pronto".
Instalación, token y filtro por hashtag: `vps/instagram-feed/README.md`.

## Patrocinantes

Cada patrocinante tiene:

- `espacios`: dónde aparece (`vip`, `premium`, `franja`, `directorio`).
- `desde` / `hasta` (formato `2026-12-31`): entra y sale solo en esas fechas. Vacío = sin límite.
- `lema`, `direccion`, `video` (opcionales): se muestran en la ficha del directorio.
- `activo`: `false` lo saca sin borrarlo.

Si un espacio `vip` o `premium` tiene varios patrocinantes, rotan cada `rotacionSegundos`.
Si no tiene ninguno vigente, muestra "Espacio disponible".

Cuántas personas hicieron clic en cada patrocinante se ve en la analítica (ver abajo), como
`clic-patrocinante-<id>`. Sirve para mandarle a cada anunciante su informe del mes.

## Kit para anunciantes

La página `/anunciantes/` es la que Frank comparte con los negocios: cifras de alcance, artistas,
dónde aparece la marca y paquetes (VIP, Premium, Emprendedor, Evento), con botón de WhatsApp por
paquete y botón **Guardar en PDF** (sale en 2 páginas A4, en fondo blanco).

Todo se cambia en `src/datos/kit.json`:

- `cifras`: cada una con `valor`, `texto`, `fuente` y `fecha`. Si `valor` está vacío, no se muestra.
  Al actualizar una cifra, cambiar también su `fecha`. Las visitas salen de la analítica y los
  oyentes de `https://interactiva.duckdns.org/feed/oyentes.json` (ver `vps/oyentes/README.md`).
- `paquetes`: qué incluye cada uno, duración y `precio`. Sin precio dice "Consultar".
- Los artistas que salen son los 8 primeros con foto, en el mismo orden de la portada.

## Analítica

Con [GoatCounter](https://www.goatcounter.com) (gratis, sin cookies, no hace falta aviso de cookies).
Se activa poniendo el código de la cuenta en `sitio.json` → `analitica.goatcounter`
(si la cuenta es `interactiva.goatcounter.com`, el código es `interactiva`). Cuenta:

- Visitas a cada página.
- `clic-patrocinante-<id>`: clics en el logo o la ficha de cada patrocinante.
- `clic-whatsapp`: clics en botones de WhatsApp (incluye el formulario de Anúnciate).
- `escuchar-en-vivo`: personas que empezaron a escuchar la radio desde la página (una vez por visita).

Mientras el código esté vacío no se carga nada. La radio por internet tiene su propio conteo de
oyentes en el VPS: `vps/oyentes/README.md`.

## Publicación (Render, sitio estático)

- Build Command: `npm install && npm run build`
- Publish Directory: `dist`

## Trabajar en local

```
npm install
npm run dev
```

`respaldo/index-anterior.html` es la página anterior, guardada como referencia.
