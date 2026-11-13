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
