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
| Artistas | un archivo `.md` por artista en `src/contenido/artistas/` |
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
