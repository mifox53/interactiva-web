# Guía para Claude — iNteractiva 89.7 FM

Sitio estático en Astro. Idioma del sitio y de los mensajes de commit: español.

- El nombre de la emisora se escribe siempre exactamente `iNteractiva 89.7 FM` y sale de
  `src/datos/sitio.json`. No escribirlo a mano en componentes ni aplicarle `text-transform`.
- El logo se dibuja solo en `src/componentes/Logo.astro`.
- Contenido editable: `src/datos/*.json` y `src/contenido/{noticias,artistas,eventos}/*.md`
  (esquemas en `src/content.config.ts`). Ver README.md para el detalle.
- Noticias: categorías permitidas en `content.config.ts`; nada de política. Redacción propia,
  con `fuenteNombre` y `fuenteUrl`. Crear siempre con `borrador: true` salvo que Miguel pida publicar.
- No inventar noticias, artistas, eventos, horarios ni patrocinantes. Los artistas salen de lo que
  publica la emisora (Instagram @interactiva89.7fm) o de lo que pase Miguel; `seguidores` es la cifra
  de Instagram al momento de revisarla.
- Imágenes en `public/img/`, optimizadas (webp o jpg, menos de 200 KB).
- Antes de entregar: `npm run build` sin errores.
- Trabajar en una rama y no tocar `main` sin que Miguel lo pida: `main` es lo que publica Render.
