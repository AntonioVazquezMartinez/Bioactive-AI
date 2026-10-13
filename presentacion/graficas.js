/* Gráficas interactivas de la presentación.
 *
 * Sin dependencias: SVG dibujado a mano. Una librería de gráficas obligaría a
 * fijar una versión de un CDN y a lidiar con el redimensionado de `canvas`
 * dentro de reveal.js, donde las diapositivas ocultas tienen ancho cero. El SVG
 * con `viewBox` escala solo y se puede dibujar aunque la diapositiva no se vea.
 *
 * Los datos vienen de `datos.js`, que genera `scripts/cifras_presentacion.py`
 * desde los archivos de la patrocinadora. Aquí no hay ninguna cifra escrita a
 * mano: si una gráfica muestra un número, salió de ahí.
 */

const PAL = {
  texto: "#e8edf3",
  tenue: "#9aa8b8",
  rejilla: "#3a4654",
  positivo: "#5b9bd5",   // BBB+, la clase mayoritaria
  negativo: "#e8954a",   // BBB−, la minoritaria
  natural: "#4caf7d",
  resto: "#8fb3dd",
  alerta: "#d64541",
  apagado: "#49566605",
};

const NS = "http://www.w3.org/2000/svg";

/** Crea un elemento SVG con atributos e hijos, para no repetir setAttribute. */
function h(tag, attrs = {}, ...kids) {
  const e = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v !== null && v !== undefined) e.setAttribute(k, v);
  }
  for (const kid of kids.flat()) {
    if (kid !== null && kid !== undefined) {
      e.appendChild(typeof kid === "string" ? document.createTextNode(kid) : kid);
    }
  }
  return e;
}

function lienzo(w, hgt) {
  return h("svg", {
    viewBox: `0 0 ${w} ${hgt}`,
    preserveAspectRatio: "xMidYMid meet",
    style: "width:100%;height:auto;overflow:visible",
  });
}

const num = (n) => n.toLocaleString("es-MX");

/** Coeficiente de correlación de Matthews desde la matriz de confusión. */
function mcc(tp, fn, fp, tn) {
  const den = Math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn));
  return den ? (tp * tn - fp * fn) / den : 0;
}

// ---------------------------------------------------------------------------
// 1 · Filtrar a A+B empeora el desbalance
// ---------------------------------------------------------------------------
function grupos(destino, D) {
  const W = 760, H = 300, izq = 48, abajo = 52, arriba = 28;
  const svg = lienzo(W, H);
  const gs = D.grupos;
  const maxN = Math.max(...gs.map((g) => g.n));
  const ancho = (W - izq - 24) / gs.length;
  const alto = H - abajo - arriba;
  let soloAB = false;

  const barras = [];
  gs.forEach((g, i) => {
    const x = izq + i * ancho + ancho * 0.18;
    const w = ancho * 0.64;
    const hTot = (g.n / maxN) * alto;
    const hNeg = (g.neg / g.n) * hTot;
    const grupo = h("g", { style: "transition:opacity .45s" });
    const pos = h("rect", {
      x, y: arriba + alto - hTot, width: w, height: hTot - hNeg,
      fill: PAL.positivo, rx: 2,
    });
    const neg = h("rect", {
      x, y: arriba + alto - hNeg, width: w, height: hNeg,
      fill: PAL.negativo, rx: 2,
    });
    grupo.append(
      pos, neg,
      h("text", {
        x: x + w / 2, y: H - abajo + 22, "text-anchor": "middle",
        fill: PAL.texto, "font-size": 19, "font-weight": 700,
      }, g.grupo),
      h("text", {
        x: x + w / 2, y: H - abajo + 40, "text-anchor": "middle",
        fill: PAL.tenue, "font-size": 13,
      }, num(g.n)),
      h("text", {
        x: x + w / 2, y: arriba + alto - hTot - 8, "text-anchor": "middle",
        fill: PAL.tenue, "font-size": 13,
      }, `${Math.round((100 * g.neg) / g.n)}% BBB−`),
    );
    svg.appendChild(grupo);
    barras.push({ g, grupo });
  });

  svg.appendChild(h("line", {
    x1: izq, y1: arriba + alto, x2: W - 16, y2: arriba + alto,
    stroke: PAL.rejilla, "stroke-width": 1.5,
  }));

  const lectura = document.createElement("div");
  lectura.className = "lectura";
  const boton = document.createElement("button");
  boton.className = "bio-boton";

  function pinta() {
    const d = soloAB ? D.filtrado_ab.ab : D.filtrado_ab.completo;
    barras.forEach(({ g, grupo }) => {
      grupo.style.opacity = soloAB && (g.grupo === "C" || g.grupo === "D") ? 0.16 : 1;
    });
    lectura.innerHTML =
      `<span class="cifra">${num(d.n)}</span> compuestos · ` +
      `clase minoritaria <span class="cifra ${soloAB ? "mala" : ""}">${d.pct_minoritaria.toFixed(1)}%</span>`;
    boton.textContent = soloAB ? "↺ Volver al conjunto completo" : "Filtrar a A+B, como recomendaba la investigación";
    boton.classList.toggle("activo", soloAB);
  }
  boton.onclick = () => { soloAB = !soloAB; pinta(); };
  pinta();

  destino.append(svg, lectura, boton);
}

// ---------------------------------------------------------------------------
// 2 · La brecha natural/sintético existe en B y C, no en A
// ---------------------------------------------------------------------------
function naturales(destino, D) {
  const W = 760, H = 320, izq = 56, arriba = 34, abajo = 76;
  const svg = lienzo(W, H);
  const gs = D.naturales.filter((g) => ["A", "B", "C"].includes(g.grupo));
  const alto = H - arriba - abajo;
  const ancho = (W - izq - 40) / gs.length;
  const y = (pct) => arriba + alto - (pct / 100) * alto;

  [0, 25, 50, 75, 100].forEach((t) => {
    svg.append(
      h("line", { x1: izq, y1: y(t), x2: W - 24, y2: y(t), stroke: PAL.rejilla, "stroke-width": 1 }),
      h("text", { x: izq - 10, y: y(t) + 5, "text-anchor": "end", fill: PAL.tenue, "font-size": 13 }, `${t}%`),
    );
  });

  gs.forEach((g, i) => {
    const x0 = izq + i * ancho + ancho * 0.14;
    const w = ancho * 0.3;
    const sinBrecha = g.ic[0] <= 0 && g.ic[1] >= 0;
    [["resto", g.res_pct, g.res_n, PAL.resto], ["natural", g.nat_pct, g.nat_n, PAL.natural]]
      .forEach(([etiq, pct, n, color], j) => {
        const x = x0 + j * (w + 10);
        svg.append(
          h("rect", { x, y: y(pct), width: w, height: arriba + alto - y(pct), fill: color, rx: 3 }),
          h("text", {
            x: x + w / 2, y: y(pct) - 8, "text-anchor": "middle",
            fill: PAL.texto, "font-size": 15, "font-weight": 700,
          }, `${pct}`),
          h("text", {
            x: x + w / 2, y: arriba + alto + 18, "text-anchor": "middle",
            fill: PAL.tenue, "font-size": 11,
          }, num(n)),
        );
      });
    const cx = x0 + w + 5;
    svg.append(
      h("text", {
        x: cx, y: arriba + alto + 42, "text-anchor": "middle",
        fill: PAL.texto, "font-size": 17, "font-weight": 700,
      }, `Grupo ${g.grupo}`),
      h("text", {
        x: cx, y: arriba + alto + 62, "text-anchor": "middle",
        fill: sinBrecha ? PAL.natural : PAL.alerta, "font-size": 14, "font-weight": 700,
      }, `${g.dif > 0 ? "+" : ""}${g.dif} pts  [${g.ic[0]}, ${g.ic[1]}]`),
      h("text", {
        x: cx, y: arriba - 12, "text-anchor": "middle",
        fill: sinBrecha ? PAL.natural : PAL.alerta, "font-size": 13,
      }, sinBrecha ? "sin brecha" : "brecha"),
    );
  });

  const leyenda = document.createElement("div");
  leyenda.className = "lectura";
  leyenda.innerHTML =
    `<span class="punto" style="background:${PAL.resto}"></span> resto &nbsp;&nbsp;` +
    `<span class="punto" style="background:${PAL.natural}"></span> naturales &nbsp;&nbsp;·&nbsp;&nbsp;` +
    `% BBB+ dentro de cada grupo de B3DB. El grupo A es el que trae <strong>logBB medido</strong>.`;
  destino.append(svg, leyenda);
}

// ---------------------------------------------------------------------------
// 3 · El umbral de TPSA no es una constante, y además es plano
// ---------------------------------------------------------------------------
function tpsa(destino, D) {
  const W = 760, H = 290, izq = 52, der = 20, arriba = 22, abajo = 42;
  const T = D.tpsa;
  const nombres = {
    completo: "Conjunto completo", ab: "Solo A+B",
    a: "Solo grupo A", entrenamiento: "Solo entrenamiento",
  };
  let cual = "completo";
  let corte = T.optimos.completo.corte;

  const svg = lienzo(W, H);
  const capa = h("g");
  svg.appendChild(capa);
  const alto = H - arriba - abajo, ancho = W - izq - der;
  const px = (c) => izq + (c / 200) * ancho;
  const py = (j) => arriba + alto - (j / 0.6) * alto;

  const lectura = document.createElement("div");
  lectura.className = "lectura";
  const control = document.createElement("input");
  Object.assign(control, { type: "range", min: 0, max: 200, step: 1, className: "bio-rango" });
  const pestanas = document.createElement("div");
  pestanas.className = "bio-pestanas";

  function serieJ(nombre) {
    return T.series[nombre].map(([tp, fn, fp, tn]) => {
      const sens = tp + fn ? tp / (tp + fn) : 0;
      const esp = tn + fp ? tn / (tn + fp) : 0;
      return sens + esp - 1;
    });
  }

  function pinta() {
    capa.textContent = "";
    const js = serieJ(cual);
    const opt = T.optimos[cual];

    [0, 0.2, 0.4, 0.6].forEach((t) => capa.append(
      h("line", { x1: izq, y1: py(t), x2: W - der, y2: py(t), stroke: PAL.rejilla, "stroke-width": 1 }),
      h("text", { x: izq - 8, y: py(t) + 4, "text-anchor": "end", fill: PAL.tenue, "font-size": 12 }, t.toFixed(1)),
    ));
    [0, 50, 100, 150, 200].forEach((c) => capa.appendChild(
      h("text", { x: px(c), y: H - abajo + 20, "text-anchor": "middle", fill: PAL.tenue, "font-size": 12 }, `${c}`),
    ));

    // la meseta: todos los cortes que no se distinguen del mejor
    const [m0, m1] = opt.meseta;
    capa.appendChild(h("rect", {
      x: px(m0), y: arriba, width: px(m1) - px(m0), height: alto,
      fill: PAL.positivo, opacity: 0.14,
    }));
    capa.appendChild(h("text", {
      x: (px(m0) + px(m1)) / 2, y: arriba + 14, "text-anchor": "middle",
      fill: PAL.positivo, "font-size": 12,
    }, `indistinguible: ${m0}–${m1} Å²`));

    capa.appendChild(h("path", {
      d: js.map((j, i) => `${i ? "L" : "M"}${px(T.cortes[i]).toFixed(1)},${py(j).toFixed(1)}`).join(""),
      fill: "none", stroke: PAL.resto, "stroke-width": 2.5,
    }));

    const j = js[corte];
    capa.append(
      h("line", { x1: px(corte), y1: arriba, x2: px(corte), y2: arriba + alto, stroke: PAL.negativo, "stroke-width": 2 }),
      h("circle", { cx: px(corte), cy: py(j), r: 6, fill: PAL.negativo }),
    );

    const [tp, fn, fp, tn] = T.series[cual][corte];
    const sens = tp + fn ? tp / (tp + fn) : 0;
    const esp = tn + fp ? tn / (tn + fp) : 0;
    lectura.innerHTML =
      `TPSA &lt; <span class="cifra">${corte}</span> Å² ⇒ BBB+ &nbsp;·&nbsp; ` +
      `n = ${num(T.n[cual])} <br>` +
      `sensibilidad <strong>${(100 * sens).toFixed(1)}%</strong> &nbsp; ` +
      `especificidad <strong>${(100 * esp).toFixed(1)}%</strong> &nbsp; ` +
      `J <strong>${j.toFixed(3)}</strong> &nbsp; MCC <strong>${mcc(tp, fn, fp, tn).toFixed(3)}</strong>`;
    control.value = corte;
    [...pestanas.children].forEach((b) => b.classList.toggle("activo", b.dataset.k === cual));
  }

  Object.keys(nombres).forEach((k) => {
    const b = document.createElement("button");
    b.className = "bio-boton chico";
    b.dataset.k = k;
    b.textContent = `${nombres[k]} · ${T.optimos[k].corte} Å²`;
    b.onclick = () => { cual = k; corte = T.optimos[k].corte; pinta(); };
    pestanas.appendChild(b);
  });
  control.oninput = () => { corte = +control.value; pinta(); };
  pinta();

  destino.append(pestanas, svg, control, lectura);
}

// ---------------------------------------------------------------------------
// 4 · Las dos fases casi no se tocan, y la asimetría es el punto
// ---------------------------------------------------------------------------
function etapas(destino, D) {
  const W = 760, H = 210, izq = 160, der = 190, arriba = 24;
  const svg = lienzo(W, H);
  const E = D.etapas;
  const ancho = W - izq - der;
  const filas = [["Fase 2 · actividad", E.actividad], ["Fase 1 · permeabilidad", E.permeabilidad]];

  filas.forEach(([etiq, n], i) => {
    const y = arriba + i * 86;
    const w = (n / E.actividad) * ancho;
    const wc = Math.max((E.ambos / E.actividad) * ancho, 3);
    const pct = (100 * E.ambos) / n;
    svg.append(
      h("text", { x: izq - 16, y: y + 27, "text-anchor": "end", fill: PAL.texto, "font-size": 17 }, etiq),
      h("rect", { x: izq, y, width: w, height: 40, fill: PAL.resto, opacity: 0.35, rx: 3 }),
      h("rect", { x: izq, y, width: wc, height: 40, fill: PAL.alerta, rx: 3 }),
      h("text", { x: izq + w + 14, y: y + 26, fill: PAL.tenue, "font-size": 15 },
        `${num(n)} esqueletos`),
      // el porcentaje va debajo, no al lado: en la barra chica se encimaría
      h("text", { x: izq, y: y + 60, fill: PAL.alerta, "font-size": 14, "font-weight": 700 },
        `${pct.toFixed(1)}% de esta fase`),
    );
  });

  const pie = document.createElement("div");
  pie.className = "lectura";
  pie.innerHTML =
    `<span class="punto" style="background:${PAL.alerta}"></span> los <strong>${num(E.ambos)}</strong> ` +
    `esqueletos con medición en los dos conjuntos. La misma cifra es el <strong>1.0%</strong> de una fase ` +
    `y el <strong>25.7%</strong> de la otra: esa asimetría es el problema. Para el 99% restante, la ` +
    `permeabilidad sería una predicción sin verificar.`;
  destino.append(svg, pie);
}

// ---------------------------------------------------------------------------
// 5 · Dónde cortar «activo»: una sola decisión, con sus dos consecuencias
// ---------------------------------------------------------------------------
function etiquetado(destino, D) {
  const A = D.actividad;
  const caja = document.createElement("div");
  caja.className = "bio-cortes";
  let elegido = "10";

  function pinta() {
    const c = A.cortes[elegido];
    const b = A.balance[elegido];
    caja.innerHTML = "";
    const botones = document.createElement("div");
    botones.className = "bio-pestanas";
    [["10", "Cortar en 10 µM  (pChEMBL ≥ 5)"], ["1", "Cortar en 1 µM  (pChEMBL ≥ 6)"]]
      .forEach(([k, txt]) => {
        const b2 = document.createElement("button");
        b2.className = "bio-boton" + (k === elegido ? " activo" : "");
        b2.textContent = txt;
        b2.onclick = () => { elegido = k; pinta(); };
        botones.appendChild(b2);
      });

    const rejilla = document.createElement("div");
    rejilla.className = "bio-rejilla";
    const tarjeta = (titulo, valor, nota, alerta) =>
      `<div class="bio-tarjeta${alerta ? " alerta" : ""}">
         <div class="t">${titulo}</div>
         <div class="v">${valor}</div>
         <div class="n">${nota}</div>
       </div>`;
    rejilla.innerHTML =
      tarjeta("Censurados que sirven de negativo", num(c.seguros),
              `${num(c.ambiguos)} quedan ambiguos`, false) +
      tarjeta("Activos por registro", `${b.pct_activos}%`,
              `razón de clases ${b.razon}`, false) +
      tarjeta("De una sola referencia de ChEMBL", `${c.pct_una_referencia}%`,
              `${num(c.de_una_referencia)} filas, todas de ${A.referencia_dominante}`,
              c.pct_una_referencia >= 60);

    caja.append(botones, rejilla);
    const pie = document.createElement("p");
    pie.className = "lectura";
    pie.innerHTML = elegido === "10"
      ? `Con este corte <strong>tres de cada cinco negativos del conjunto salen de un solo experimento</strong>. Ninguna partición arregla eso: si ese experimento tiene un sesgo, el modelo lo aprende como si fuera biología.`
      : `Más exigente con los activos y, por la misma regla de censura, más generoso con los negativos: recupera <strong>${num(A.cortes["1"].seguros - A.cortes["10"].seguros)}</strong> censurados más y deja el conjunto casi balanceado.`;
    caja.appendChild(pie);
  }
  pinta();
  destino.appendChild(caja);
}

// ---------------------------------------------------------------------------

const GRAFICAS = { grupos, naturales, tpsa, etapas, etiquetado };

function dibujar() {
  if (!window.DATOS) return;
  document.querySelectorAll("[data-grafica]").forEach((nodo) => {
    if (nodo.dataset.lista) return;
    const fn = GRAFICAS[nodo.dataset.grafica];
    if (!fn) return;
    try {
      fn(nodo, window.DATOS);
      nodo.dataset.lista = "1";
    } catch (e) {
      nodo.textContent = "No se pudo dibujar esta gráfica.";
      console.error("[bioactive]", nodo.dataset.grafica, e);
    }
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", dibujar);
} else {
  dibujar();
}
window.addEventListener("load", dibujar);
