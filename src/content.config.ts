import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

// Categorías permitidas para noticias. Política queda fuera a propósito (ver docs/noticias.md).
export const CATEGORIAS = [
  'agricultura', 'cafe', 'eventos', 'deportes', 'cultura', 'musica', 'turismo', 'ciudad', 'clima-y-vias',
] as const;

// Regiones de Venezuela para agrupar las noticias. Mérida va aparte porque es la casa.
// andes: Táchira, Trujillo · capital: Caracas, Miranda, La Guaira · centro: Aragua, Carabobo, Yaracuy
// occidente: Zulia, Lara, Falcón · oriente: Sucre, Anzoátegui, Monagas, Nueva Esparta
// llanos: Barinas, Apure, Portuguesa, Guárico, Cojedes · guayana: Bolívar, Amazonas, Delta Amacuro
// nacional: lo que toca a todo el país (por ejemplo, la temporada de béisbol)
export const REGIONES = [
  'merida', 'andes', 'capital', 'centro', 'occidente', 'oriente', 'llanos', 'guayana', 'nacional',
] as const;

const noticias = defineCollection({
  loader: glob({ pattern: '**/[^_]*.md', base: './src/contenido/noticias' }),
  schema: z.object({
    titulo: z.string(),
    fecha: z.coerce.date(),
    categoria: z.enum(CATEGORIAS),
    // Región y lugar: "oriente" + "Cumaná, Sucre". Si no se indica, la noticia es de Mérida.
    region: z.enum(REGIONES).default('merida'),
    lugar: z.string().optional(),
    resumen: z.string(),
    fuenteNombre: z.string(),
    fuenteUrl: z.string().url(),
    imagen: z.string().optional(),
    creditoImagen: z.string().optional(),
    destacada: z.boolean().default(false),
    // borrador: true = no se publica hasta que se apruebe
    borrador: z.boolean().default(true),
  }),
});

const artistas = defineCollection({
  loader: glob({ pattern: '**/[^_]*.md', base: './src/contenido/artistas' }),
  schema: z.object({
    nombre: z.string(),
    tipo: z.enum(['local', 'internacional']).optional(),
    // Género musical, libre: "Salsa", "Merengue", "Música llanera"... Sirve para filtrar en /artistas/
    genero: z.string().optional(),
    foto: z.string().optional(),
    // Enlace al video de saludo del artista (por ejemplo, la publicación en Instagram)
    saludo: z.string().url().optional(),
    destacado: z.boolean().default(false),
    // Orden en las listas: menor primero. Si no se indica, se ordena por seguidores.
    orden: z.number().default(100),
    // Usuario de Instagram sin @ (por ejemplo "lizcontigo") o el enlace completo
    instagram: z.string().optional(),
    // Seguidores en Instagram al momento de revisarlo (número entero, por ejemplo 272000)
    seguidores: z.number().int().nonnegative().optional(),
    enlace: z.string().optional(),
    // Fotos adicionales del artista (rutas en /img/artistas/...). Opcional: si no hay, no se muestra nada.
    galeria: z.array(z.string()).default([]),
    // Último lanzamiento (sencillo, video, álbum). Opcional: solo los artistas que lo tengan muestran el bloque.
    lanzamiento: z.object({
      titulo: z.string(),
      portada: z.string().optional(),
      fecha: z.coerce.date().optional(),
      texto: z.string().optional(),
      spotify: z.string().url().optional(),
      youtube: z.string().url().optional(),
      apple: z.string().url().optional(),
    }).optional(),
  }),
});

const eventos = defineCollection({
  loader: glob({ pattern: '**/[^_]*.md', base: './src/contenido/eventos' }),
  schema: z.object({
    titulo: z.string(),
    tipo: z.enum(['evento', 'saludo']),
    fecha: z.coerce.date(),
    // Los eventos dejan de mostrarse después de su fecha; los saludos, después de "hasta"
    hasta: z.coerce.date().optional(),
    lugar: z.string().optional(),
    artista: z.string().optional(),
    imagen: z.string().optional(),
    enlace: z.string().optional(),
    patrocinado: z.boolean().default(false),
    borrador: z.boolean().default(true),
  }),
});

export const collections = { noticias, artistas, eventos };
