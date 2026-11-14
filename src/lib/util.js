import sitio from '../datos/sitio.json';

/** Enlace de WhatsApp de la emisora con un mensaje ya escrito. */
export function wa(mensaje = '') {
  const base = `https://wa.me/${sitio.whatsapp}`;
  return mensaje ? `${base}?text=${encodeURIComponent(mensaje)}` : base;
}

const fmt = new Intl.DateTimeFormat('es-VE', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' });
export const fechaLarga = (d) => fmt.format(d);

export const NOMBRES_CATEGORIA = {
  agricultura: 'Agricultura',
  cafe: 'Café',
  eventos: 'Eventos',
  deportes: 'Deportes',
  cultura: 'Cultura',
  ciudad: 'Ciudad',
};

/** Enlace al perfil de Instagram a partir del usuario ("lizcontigo", "@lizcontigo") o de un enlace completo. */
export function instagramUrl(valor) {
  if (!valor) return '';
  if (/^https?:\/\//.test(valor)) return valor;
  return `https://www.instagram.com/${valor.replace(/^@/, '')}/`;
}

/** Usuario de Instagram con @, a partir de un usuario o de un enlace. */
export function instagramUsuario(valor) {
  if (!valor) return '';
  const m = valor.match(/instagram\.com\/([^/?#]+)/);
  return '@' + (m ? m[1] : valor.replace(/^@/, ''));
}

/** Número de seguidores en corto: 8M, 840K, 17K, 950. */
export function seguidoresCorto(n) {
  if (!n && n !== 0) return '';
  if (n >= 1e6) return `${(n / 1e6).toFixed(n % 1e6 >= 1e5 ? 1 : 0).replace('.0', '')}M`;
  if (n >= 1e3) return `${Math.round(n / 1e3)}K`;
  return String(n);
}

/**
 * Orden de los artistas: primero por `orden` (si alguien lo fijó a mano), luego por seguidores
 * (de más a menos), luego por nombre.
 */
export function ordenarArtistas(artistas) {
  return artistas.slice().sort((a, b) =>
    a.data.orden - b.data.orden ||
    (b.data.seguidores ?? -1) - (a.data.seguidores ?? -1) ||
    a.data.nombre.localeCompare(b.data.nombre, 'es'));
}

/** Enlace principal de la ficha de un artista: su página dentro del sitio. */
export const paginaArtista = (a) => `/artistas/${a.id}/`;

/**
 * Artista de la semana. Si en `semanas` hay una entrada vigente hoy, manda esa; si no,
 * se elige uno de la lista por número de semana, de modo que todos pasen por turnos.
 */
export function artistaDeLaSemana(artistas, semanas = [], hoy = new Date()) {
  const dia = hoy.toISOString().slice(0, 10);
  const fijada = semanas.find((s) => s.artista && (!s.desde || s.desde <= dia) && (!s.hasta || s.hasta >= dia));
  if (fijada) {
    const a = artistas.find((x) => x.id === fijada.artista);
    if (a) return { artista: a, motivo: fijada.motivo ?? '', fijado: true, hasta: fijada.hasta ?? '' };
  }
  const candidatos = artistas.filter((a) => a.data.foto);
  if (!candidatos.length) return null;
  const semana = Math.floor((hoy - new Date(Date.UTC(2026, 0, 5))) / (7 * 864e5)); // semanas desde el lunes 5-ene-2026
  return { artista: candidatos[((semana % candidatos.length) + candidatos.length) % candidatos.length], motivo: '', fijado: false };
}
