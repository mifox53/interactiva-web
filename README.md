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
| Texto de "Nosotros" | `src/datos/sitio.json` → `nosotros` |
| Planes y formulario de anunciantes | `src/pages/anunciate.astro` |
| Colores y estilos | `src/estilos/global.css` |

Los archivos `_plantilla.md` son modelos para copiar; no se publican.

## Reglas del contenido

- El nombre se escribe siempre **iNteractiva 89.7 FM**.
- Noticias: solo agricultura, café, eventos, deportes, cultura y ciudad. **Nada de política.**
  Resumen con palabras propias y enlace a la fuente. Fotos propias o con permiso.
- Una noticia o evento con `borrador: true` no aparece en el sitio. Se publica al cambiarlo a `false`.
- Lo pagado lleva `patrocinado: true` y sale con la etiqueta "Patrocinado".

## Artistas

Cada artista es un archivo `.md` en `src/contenido/artistas/` (modelo: `_plantilla.md`). Campos:
`nombre`, `tipo` (local/internacional), `genero`, `foto`, `saludo` (enlace a su video de saludo),
`instagram` (usuario sin @), `seguidores` (número), `orden` (solo para forzar a alguien arriba) y
`destacado`. El texto debajo del `---` es una biografía corta opcional.

- **Orden**: por `orden` si se fijó; si no, de más a menos `seguidores`; luego por nombre.
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

## Patrocinantes

Cada patrocinante tiene:

- `espacios`: dónde aparece (`vip`, `premium`, `franja`, `directorio`).
- `desde` / `hasta` (formato `2026-12-31`): entra y sale solo en esas fechas. Vacío = sin límite.
- `lema`, `direccion`, `video` (opcionales): se muestran en la ficha del directorio.
- `activo`: `false` lo saca sin borrarlo.

Si un espacio `vip` o `premium` tiene varios patrocinantes, rotan cada `rotacionSegundos`.
Si no tiene ninguno vigente, muestra "Espacio disponible".

Para contar clics por patrocinante: crear una cuenta en goatcounter.com y poner el código
de la cuenta en `sitio.json` → `analitica.goatcounter`.

## Publicación (Render, sitio estático)

- Build Command: `npm install && npm run build`
- Publish Directory: `dist`

## Trabajar en local

```
npm install
npm run dev
```

`respaldo/index-anterior.html` es la página anterior, guardada como referencia.
