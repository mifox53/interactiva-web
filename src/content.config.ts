import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

// Categorías permitidas para noticias. Política queda fuera a propósito.
export const CATEGORIAS = ['agricultura', 'cafe', 'eventos', 'deportes', 'cultura', 'ciudad'] as const;

const noticias = defineCollection({
  loader: glob({ pattern: '**/[^_]*.md', base: './src/contenido/noticias' }),
  schema: z.object({
    titulo: z.string(),
    fecha: z.coerce.date(),
    categoria: z.enum(CATEGORIAS),
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
    tipo: z.enum(['local', 'internacional']),
    foto: z.string().optional(),
    destacado: z.boolean().default(false),
    orden: z.number().default(100),
    instagram: z.string().optional(),
    enlace: z.string().optional(),
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
