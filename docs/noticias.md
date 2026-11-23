# Noticias: «Venezuela ahora»

La sección tiene dos partes:

1. **Titulares de las regiones (automáticos).** Un programa en el VPS lee cada 3 horas los feeds
   de medios venezolanos, filtra lo que no va y publica titular, medio, fecha y enlace. No pasa
   por nadie. Ver `vps/noticias-feed/README.md`.
2. **Destacadas de Mérida (de la emisora).** Cada lunes, la tarea programada escribe 2 o 3
   noticias de Mérida con palabras propias, siguiendo esta guía, y Miguel las aprueba.

Esta guía es para las destacadas y para cualquiera que agregue noticias a mano. Las reglas de
«Qué no va» son las mismas que aplica el filtro automático (`vps/noticias-feed/filtros.json`).

## Destacadas de Mérida

- **Cuándo:** cada lunes, con lo mejor de la semana anterior (lunes a domingo).
- **Cuántas:** 2 o 3, todas de Mérida (`region: merida`). `destacada: true` solo en la mejor:
  es la que sale en grande en la portada.
- **Temas permitidos** (campo `categoria`): agricultura, café, cultura, música, turismo, eventos,
  deportes, ciudad y clima y vías.
- **Nada de política ni de religión.** Si una noticia necesita un político, un partido, un
  conflicto o un tema religioso para entenderse, no va.

### Qué no va

- Gobierno, oposición, partidos, elecciones nacionales o regionales, candidatos, sanciones,
  negociaciones, presos políticos, declaraciones de dirigentes.
- Protestas, paros, marchas y denuncias contra autoridades (aunque sean por servicios).
- Sucesos: crímenes, accidentes con víctimas, detenciones, violencia.
- Economía política: tipo de cambio, inflación, salarios, precios regulados.
- Noticias de salud con diagnósticos o cifras sensibles.
- **Religión:** vírgenes, santos, iglesias, misas, procesiones, fiestas patronales, Navidad,
  Semana Santa ni ningún otro tema religioso (pedido expreso de Miguel).

### Clima y vías: qué sí y qué no

Sí, porque es información útil para la gente:

- Pronósticos de lluvia del Inameh que afecten a la región.
- Carreteras cerradas, derrumbes, pasos restringidos y reaperturas.
- Cortes de luz o agua **programados**, con zonas y horarios.
- Estado de calles y semáforos, con un consejo práctico al final.

No: quejas contra un funcionario, protestas por los servicios, cifras de damnificados usadas para
culpar a alguien. Se cuenta el dato práctico, sin buscar culpables.

## Regiones (campo `region`) y lugar (campo `lugar`)

| `region` | Estados | Ejemplo de `lugar` |
|---|---|---|
| `merida` | Mérida | "Mérida", "El Vigía" |
| `andes` | Táchira, Trujillo | "San Cristóbal, Táchira" |
| `capital` | Distrito Capital, Miranda, La Guaira | "Caracas" |
| `centro` | Aragua, Carabobo, Yaracuy | "Valencia, Carabobo" |
| `occidente` | Zulia, Lara, Falcón | "Maracaibo, Zulia" |
| `oriente` | Sucre, Anzoátegui, Monagas, Nueva Esparta | "Cumaná, Sucre" |
| `llanos` | Barinas, Apure, Portuguesa, Guárico, Cojedes | "Barinas" |
| `guayana` | Bolívar, Amazonas, Delta Amacuro | "Ciudad Guayana, Bolívar" |
| `nacional` | Lo que toca a todo el país (LVBP, selecciones) | "Caracas" (donde ocurrió) |

Si la noticia es de un merideño que compite fuera (por ejemplo, en unos juegos nacionales), va
como `merida` y el lugar del evento se cuenta en el texto.

## Fuentes

Siempre el medio original, nunca un agregador. Antes de usar una noticia, abrir la nota y
comprobar cada dato.

**Para Mérida y los Andes**

- Diario de Los Andes: https://diariodelosandes.com/secciones/merida/ (también tiene Táchira y
  Trujillo). Es parte de la Alianza Nacional de Medios.
- Diario Frontera (Mérida).

**Para el resto del país**

- El Diario: https://eldiario.com (tiene etiquetas por ciudad, como /etiqueta/cumana/ o
  /etiqueta/merida/). También es parte de la Alianza Nacional de Medios.
- Los otros medios de la Alianza Nacional de Medios: El Carabobeño (centro), Correo del Caroní
  (Guayana), El Tequeño (Miranda), VPItv y La TV Calle.
- Crónica Uno: https://cronica.uno (Caracas y regiones; buenas historias de comunidad).
- Radio Fe y Alegría Noticias: red de emisoras en varias regiones, con periodistas propios.
- Calletacarigua.com: Carúpano y el estado Sucre.
- El Pitazo: cobertura regional; se desbloqueó en Venezuela en septiembre de 2026.

**Para descubrir qué pasa en una ciudad**

Búsqueda de Google Noticias en español de Venezuela, solo para encontrar notas (el enlace de la
noticia siempre va al medio original):

```
https://news.google.com/rss/search?q=Cuman%C3%A1&hl=es-419&gl=VE&ceid=VE:es-419
```

Cambiar `q=` por la ciudad o el tema (Maracaibo, Barquisimeto, "Isla de Margarita", Inameh,
LVBP…). Los resultados cambian según cómo se escriba la búsqueda.

**Evitar**

- Medios bloqueados en Venezuela: el lector no podría abrir el enlace. En septiembre de 2026 seguían
  bloqueados, entre otros, La Patilla, El Nacional y Armando.info, y en noviembre VE sin Filtro
  contaba unos 140 dominios bloqueados. Si una noticia solo está en un medio bloqueado, buscarla en
  otro o dejarla.
- Medios con línea política marcada, de cualquier lado: usarlos solo para deportes o datos de
  agenda, y solo si no hay otra fuente.
- Notas de opinión, columnas y blogs personales.

## Cómo se escribe

- **Título propio**, no el del medio. Corto y claro.
- **Resumen** (`resumen`): una o dos frases con lo esencial, con palabras propias.
- **Texto**: uno o dos párrafos cortos, con palabras propias. Al final puede ir un comentario de
  la emisora (un dato útil, una felicitación), sin opinar de política.
- No copiar frases del medio. Citas textuales solo si son muy cortas y hacen falta.
- No inventar ni completar datos: si la nota no dice la hora, el lugar o la cifra, no se pone.
- **Sin fotos de los medios.** Las tarjetas sin foto muestran la ciudad sobre el color de su
  región. Solo fotos propias o con permiso (`imagen` y `creditoImagen`).
- `fecha`: la fecha en que el medio publicó la nota.
- `fuenteNombre` y `fuenteUrl`: el medio y el enlace exacto a la nota.

## Archivo de cada noticia

Un archivo por noticia en `src/contenido/noticias/`, con nombre `AAAA-MM-DD-tema-corto.md`
(modelo: `_plantilla.md`):

```
---
titulo: "Título propio"
fecha: 2026-11-21
categoria: turismo
region: merida
lugar: "Mérida"
resumen: "Una o dos frases propias."
fuenteNombre: "Diario de Los Andes"
fuenteUrl: "https://..."
destacada: false
borrador: true
---

Texto con palabras propias.
```

`borrador: true` siempre al crearla. La noticia aparece en el sitio cuando se cambia a `false`.

## Flujo de cada semana (destacadas)

1. Crear la rama `noticias-AAAA-MM-DD` (fecha del lunes) desde `main`.
2. Buscar en las fuentes de Mérida, elegir 2 o 3 noticias según esta guía y verificar cada dato
   en la nota original.
3. Escribir los archivos con `borrador: true`.
4. `npm run build` sin errores y subir la rama.
5. Mandar a Miguel la lista (título, región y fuente de cada una) para que apruebe.
6. Cuando Miguel diga «publica»: cambiar `borrador` a `false` en las aprobadas, volver a compilar
   y pasar la rama a `main`.

Las noticias de semanas anteriores se quedan en `/noticias/`. En la portada sale en grande la
destacada más reciente, y al lado los titulares automáticos (Mérida primero). Si el VPS no
responde, al lado se ven las noticias de la emisora.
