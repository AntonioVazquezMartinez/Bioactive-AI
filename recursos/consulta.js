/* La página de consulta: formulario sin servidor.
 *
 * El sitio es estático, así que no hay a dónde enviar. Lo que hace esta página
 * es **estructurar** la respuesta, no transportarla: al final arma un texto en
 * Markdown que la patrocinadora copia a un correo o descarga, y que el equipo
 * pega tal cual en el acta y en la bitácora de decisiones. El valor está en que
 * llegue ordenada y con las opciones ya nombradas, no en ahorrarle el correo.
 *
 * Lo que escribe se guarda en el navegador para que no lo pierda si cierra la
 * pestaña. Es una comodidad y nada más: no sale de su máquina, no nos llega, y
 * si el navegador lo bloquea la página sigue funcionando igual.
 */

const CLAVE = "bioactive-consulta-v1";

/** Lee el borrador guardado. Puede fallar en ventana privada: no importa. */
function borrador() {
  try {
    return JSON.parse(localStorage.getItem(CLAVE) || "{}");
  } catch {
    return {};
  }
}

function guardar(datos) {
  try {
    localStorage.setItem(CLAVE, JSON.stringify(datos));
  } catch {
    /* sin almacenamiento: la página funciona igual, solo no recuerda */
  }
}

const estado = borrador();
const preguntas = [];

function construir(nodo) {
  const id = nodo.dataset.id;
  const opciones = (nodo.dataset.opciones || "").split("|").filter(Boolean);
  estado[id] = estado[id] || { opcion: null, extra: "", nota: "" };
  preguntas.push({ id, titulo: nodo.dataset.titulo || id });

  const caja = document.createElement("div");
  caja.className = "bio-pregunta-caja";

  const grupo = document.createElement("div");
  grupo.className = "bio-opciones";
  opciones.forEach((texto) => {
    const etiqueta = document.createElement("label");
    const radio = document.createElement("input");
    radio.type = "radio";
    radio.name = `op-${id}`;
    radio.value = texto;
    radio.checked = estado[id].opcion === texto;
    radio.onchange = () => { estado[id].opcion = texto; guardar(estado); pintarSalida(); };
    etiqueta.append(radio, document.createTextNode(" " + texto));
    grupo.appendChild(etiqueta);
  });
  caja.appendChild(grupo);

  if (nodo.dataset.extra) {
    const p = document.createElement("p");
    p.className = "bio-extra";
    p.textContent = nodo.dataset.extra;
    const campo = document.createElement("textarea");
    campo.rows = 2;
    campo.value = estado[id].extra;
    campo.placeholder = "Su respuesta…";
    campo.oninput = () => { estado[id].extra = campo.value; guardar(estado); pintarSalida(); };
    caja.append(p, campo);
  }

  const nota = document.createElement("textarea");
  nota.rows = 3;
  nota.value = estado[id].nota;
  nota.placeholder = "Comentarios, matices, o «no lo sé»…";
  nota.oninput = () => { estado[id].nota = nota.value; guardar(estado); pintarSalida(); };
  caja.appendChild(nota);

  nodo.appendChild(caja);
}

/** El texto que se lleva: Markdown, para pegarlo en el acta sin reformatear. */
function texto() {
  const hoy = new Date().toISOString().slice(0, 10);
  const lineas = [
    "# Respuestas de la patrocinadora",
    "",
    `**Fecha:** ${hoy}`,
    "",
  ];
  let contestadas = 0;
  preguntas.forEach((p, i) => {
    const r = estado[p.id] || {};
    const vacia = !r.opcion && !(r.extra || "").trim() && !(r.nota || "").trim();
    if (!vacia) contestadas += 1;
    lineas.push(`## ${i + 1} · ${p.titulo}`, "");
    lineas.push(r.opcion ? `**Respuesta:** ${r.opcion}` : "**Respuesta:** (sin responder)");
    if ((r.extra || "").trim()) lineas.push("", (r.extra || "").trim());
    if ((r.nota || "").trim()) lineas.push("", `**Notas:** ${(r.nota || "").trim()}`);
    lineas.push("");
  });
  lineas.push("---", "",
    `${contestadas} de ${preguntas.length} con respuesta. ` +
    "Generado desde la página de consulta del proyecto Bioactive AI.");
  return lineas.join("\n");
}

let salida, resumen;

function pintarSalida() {
  if (!salida) return;
  salida.value = texto();
  const n = preguntas.filter((p) => {
    const r = estado[p.id] || {};
    return r.opcion || (r.extra || "").trim() || (r.nota || "").trim();
  }).length;
  resumen.textContent = `${n} de ${preguntas.length} con respuesta`;
  resumen.className = "bio-resumen" + (n === preguntas.length ? " completo" : "");
}

function construirSalida(destino) {
  resumen = document.createElement("p");
  resumen.className = "bio-resumen";

  salida = document.createElement("textarea");
  salida.className = "bio-salida";
  salida.rows = 12;
  salida.readOnly = true;

  const botones = document.createElement("div");
  botones.className = "bio-acciones";

  const copiar = document.createElement("button");
  copiar.className = "bio-boton activo";
  copiar.textContent = "Copiar las respuestas";
  copiar.onclick = async () => {
    try {
      await navigator.clipboard.writeText(texto());
      copiar.textContent = "✓ Copiado";
    } catch {
      salida.select();
      copiar.textContent = "Selecciónelo y copie con Ctrl+C";
    }
    setTimeout(() => { copiar.textContent = "Copiar las respuestas"; }, 2500);
  };

  const bajar = document.createElement("button");
  bajar.className = "bio-boton";
  bajar.textContent = "Descargar como archivo";
  bajar.onclick = () => {
    const url = URL.createObjectURL(new Blob([texto()], { type: "text/markdown" }));
    const a = document.createElement("a");
    a.href = url;
    a.download = `respuestas-patrocinadora-${new Date().toISOString().slice(0, 10)}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const limpiar = document.createElement("button");
  limpiar.className = "bio-boton";
  limpiar.textContent = "Borrar todo";
  limpiar.onclick = () => {
    if (!confirm("¿Borrar todas las respuestas de esta página?")) return;
    preguntas.forEach((p) => { estado[p.id] = { opcion: null, extra: "", nota: "" }; });
    guardar(estado);
    document.querySelectorAll(".bio-pregunta-caja input[type=radio]").forEach((r) => { r.checked = false; });
    document.querySelectorAll(".bio-pregunta-caja textarea").forEach((t) => { t.value = ""; });
    pintarSalida();
  };

  botones.append(copiar, bajar, limpiar);
  destino.append(resumen, salida, botones);
}

function iniciar() {
  document.querySelectorAll(".bio-pregunta[data-id]").forEach(construir);
  const destino = document.getElementById("bio-salida");
  if (destino) construirSalida(destino);
  pintarSalida();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", iniciar);
} else {
  iniciar();
}
