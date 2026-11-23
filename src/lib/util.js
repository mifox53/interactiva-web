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
  musica: 'Música',
  turismo: 'Turismo',
  ciudad: 'Ciudad',
  'clima-y-vias': 'Clima y vías',
};

export const NOMBRES_REGION = {
  merida: 'Mérida',
  andes: 'Andes',
  capital: 'Caracas y Miranda',
  centro: 'Centro',
  occidente: 'Occidente',
  oriente: 'Oriente',
  llanos: 'Llanos',
  guayana: 'Guayana',
  nacional: 'Venezuela',
};

/** Etiqueta de lugar de una noticia: "Cumaná, Sucre" si se indicó, o el nombre de la región. */
export const lugarNoticia = (d) => d.lugar || NOMBRES_REGION[d.region] || 'Mérida';

/**
 * Noticias para la portada: Mérida primero y luego variedad de regiones.
 * Toma hasta 2 de Mérida y completa con una por región; si faltan, rellena con las más recientes.
 */
export function elegirNoticias(lista, total = 5) {
  const orden = [...lista].sort((a, b) => Number(b.data.destacada) - Number(a.data.destacada) || b.data.fecha - a.data.fecha);
  const elegidas = [];
  const tomar = (n) => { if (elegidas.length < total && !elegidas.includes(n)) elegidas.push(n); };
  orden.filter((n) => n.data.region === 'merida').slice(0, 2).forEach(tomar);
  const vistas = new Set(['merida']);
  for (const n of orden) if (!vistas.has(n.data.region)) { vistas.add(n.data.region); tomar(n); }
  orden.forEach(tomar);
  // La primera (grande) es la destacada o la más reciente de Mérida; las demás, de la más nueva a la más vieja
  const [primera, ...resto] = elegidas;
  return primera ? [primera, ...resto.sort((a, b) => b.data.fecha - a.data.fecha)] : [];
}

/** "Semana del 16 al 22 de noviembre" para la semana (lunes a domingo) de una fecha. */
export function semanaDe(fecha) {
  const d = new Date(fecha);
  const dia = (d.getUTCDay() + 6) % 7; // 0 = lunes
  const lunes = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate() - dia));
  const domingo = new Date(lunes.getTime() + 6 * 86400000);
  const mes = (x) => x.toLocaleDateString('es-VE', { month: 'long', timeZone: 'UTC' });
  const ini = lunes.getUTCMonth() === domingo.getUTCMonth() ? `${lunes.getUTCDate()}` : `${lunes.getUTCDate()} de ${mes(lunes)}`;
  return `Semana del ${ini} al ${domingo.getUTCDate()} de ${mes(domingo)}`;
}

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
 * Orden de los artistas: primero por `orden` (si alguien lo fijó a mano), luego los que tienen foto,
 * luego por seguidores (de más a menos) y por nombre. Así los que aún no tienen foto quedan al final.
 */
export function ordenarArtistas(artistas) {
  return artistas.slice().sort((a, b) =>
    a.data.orden - b.data.orden ||
    (b.data.foto ? 1 : 0) - (a.data.foto ? 1 : 0) ||
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
