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

// **Los colores salen de `recursos/paleta.json`**, repartidos por
// `scripts/paleta.py` a `recursos/paleta.js`, que esta página carga antes.
// Vivían duplicados aquí y en `animaciones/comun.py`, y tres se habían
// desviado: el azul, el verde y el naranja.
//
// Se toman los pasos de modo oscuro porque el mazo va sobre fondo oscuro.
// `resto` desaparece como color propio: no era una serie sino una tinta de
// apoyo, y por eso fallaba el piso de croma —0.072, que se lee como gris—.
const _P = (window.PALETA || {}).oscuro || {};
const PAL = {
  texto: _P.texto,
  tenue: _P.tenue,
  rejilla: _P.rejilla,
  positivo: _P.positivo,   // BBB+, la clase mayoritaria
  negativo: _P.negativo,   // BBB−, la minoritaria
  natural: _P.natural,
  resto: _P.secundaria,    // trazo de apoyo, no una identidad
  alerta: _P.alerta,       // estado reservado: nunca como «serie 4»
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

function lienzo(w, hgt, titulo) {
  const s = h("svg", {
    viewBox: `0 0 ${w} ${hgt}`,
    preserveAspectRatio: "xMidYMid meet",
    style: "width:100%;height:auto;overflow:visible",
    role: "img",
    "aria-label": titulo || "gráfica",
  });
  if (titulo) s.appendChild(h("title", {}, titulo));
  return s;
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
  const svg = lienzo(W, H, "Tamaño y reparto de clases de cada grupo A–D de B3DB");
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
  const W = 760, H = 262, izq = 56, arriba = 24, abajo = 66;
  const svg = lienzo(W, H, "Porcentaje de compuestos que cruzan la barrera, naturales contra el resto, dentro de cada grupo");
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
      }, sinBrecha ? "sin brecha detectable" : "brecha"),
    );
  });

  const leyenda = document.createElement("div");
  leyenda.className = "lectura";
  const d = D.naturales.find((g) => g.grupo === "D");
  leyenda.innerHTML =
    `<span class="punto" style="background:${PAL.resto}"></span> resto &nbsp;&nbsp;` +
    `<span class="punto" style="background:${PAL.natural}"></span> naturales &nbsp;&nbsp;·&nbsp;&nbsp;` +
    `% BBB+ dentro de cada grupo de B3DB. El grupo A es el que trae <strong>logBB medido</strong>, ` +
    `y en él la brecha queda <strong>acotada a unos ±5 puntos</strong>, no demostrada en cero. ` +
    (d ? `El grupo D se omite: con ${d.res_n} y ${d.nat_n} compuestos no permite concluir.` : "");
  destino.append(svg, leyenda);
}

// ---------------------------------------------------------------------------
// 3 · El umbral de TPSA no es una constante, y además es plano
// ---------------------------------------------------------------------------
function tpsa(destino, D) {
  const W = 760, H = 248, izq = 52, der = 20, arriba = 20, abajo = 38;
  const T = D.tpsa;
  const nombres = {
    completo: "Conjunto completo", ab: "Solo A+B",
    a: "Solo grupo A", entrenamiento: "Solo entrenamiento",
  };
  let cual = "completo";
  let corte = T.optimos.completo.corte;

  const svg = lienzo(W, H, "Índice J de Youden según el corte de TPSA");
  const capa = h("g");
  svg.appendChild(capa);
  const alto = H - arriba - abajo, ancho = W - izq - der;
  const px = (c) => izq + (c / 200) * ancho;
  const py = (j) => arriba + alto - (j / 0.6) * alto;

  const lectura = document.createElement("div");
  lectura.className = "lectura";
  const control = document.createElement("input");
  Object.assign(control, { type: "range", min: 0, max: 200, step: 1, className: "bio-rango" });
  control.setAttribute("aria-label", "Corte de TPSA en Å²");
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

    // Los cortes que el bootstrap no distingue del mejor. Se pintan uno por uno
    // y no como una banda de extremo a extremo: casi nunca son contiguos, y una
    // banda llena afirmaría de los huecos lo que la medición no dice.
    const [m0, m1] = opt.meseta;
    capa.appendChild(h("rect", {
      x: px(m0), y: arriba, width: px(m1) - px(m0), height: alto,
      fill: PAL.positivo, opacity: 0.06,
    }));
    const paso = px(1) - px(0);
    (opt.cortes_meseta || []).forEach((c) => capa.appendChild(h("rect", {
      x: px(c) - paso / 2, y: arriba, width: Math.max(paso, 1.2), height: alto,
      fill: PAL.positivo, opacity: 0.22,
    })));
    capa.appendChild(h("text", {
      x: (px(m0) + px(m1)) / 2, y: arriba + 13, "text-anchor": "middle",
      fill: PAL.positivo, "font-size": 11,
    }, `${(opt.cortes_meseta || []).length} cortes entre ${m0} y ${m1} Å² no se distinguen del mejor`));

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
  const svg = lienzo(W, H, "Tamaño de las dos fases y los esqueletos que comparten");
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
  const pct2 = (100 * E.ambos) / E.actividad, pct1 = (100 * E.ambos) / E.permeabilidad;
  pie.innerHTML =
    `<span class="punto" style="background:${PAL.alerta}"></span> los <strong>${num(E.ambos)}</strong> ` +
    `esqueletos con medición en los dos conjuntos. La misma cifra es el ` +
    `<strong>${pct2.toFixed(1)}%</strong> de una fase y el <strong>${pct1.toFixed(1)}%</strong> de la ` +
    `otra: esa asimetría es el problema. Para el resto, la permeabilidad sería una predicción sin verificar.`;
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
// 6 · El archivo que recibimos no es el que describe el diccionario (2.6)
// ---------------------------------------------------------------------------
function archivo(destino, D) {
  const W = 760, H = 150, izq = 150, der = 150;
  const A = D.actividad;
  const svg = lienzo(W, H, "Registros que describe el diccionario contra los que recibimos");
  const ancho = W - izq - der;
  const falta = A.registros_diccionario - A.registros;
  const wRecibido = (A.registros / A.registros_diccionario) * ancho;

  svg.append(
    h("text", { x: izq - 14, y: 38, "text-anchor": "end", fill: PAL.texto, "font-size": 16 }, "Diccionario"),
    h("rect", { x: izq, y: 14, width: ancho, height: 34, fill: PAL.resto, opacity: 0.35, rx: 3 }),
    h("text", { x: izq + ancho + 12, y: 37, fill: PAL.tenue, "font-size": 15 }, `${num(A.registros_diccionario)}`),

    h("text", { x: izq - 14, y: 100, "text-anchor": "end", fill: PAL.texto, "font-size": 16 }, "Lo que recibimos"),
    h("rect", { x: izq, y: 76, width: wRecibido, height: 34, fill: PAL.resto, opacity: 0.55, rx: 3 }),
    h("rect", {
      x: izq + wRecibido, y: 76, width: ancho - wRecibido, height: 34,
      fill: PAL.alerta, opacity: 0.75, rx: 3,
    }),
    h("text", { x: izq + ancho + 12, y: 99, fill: PAL.tenue, "font-size": 15 }, `${num(A.registros)}`),
    h("text", {
      x: izq + wRecibido + (ancho - wRecibido) / 2, y: 130, "text-anchor": "middle",
      fill: PAL.alerta, "font-size": 14, "font-weight": 700,
    }, `faltan ${num(falta)}`),
  );

  const pie = document.createElement("div");
  pie.className = "lectura";
  pie.innerHTML =
    `El archivo se llama <code>…_Entrenamiento.csv</code> y trae el <strong>` +
    `${((100 * A.registros) / A.registros_diccionario).toFixed(1)}%</strong> de lo que describe el ` +
    `diccionario. Si esos ${num(falta)} son una prueba ya apartada, <strong>no construimos otra</strong>; ` +
    `si se separaron al azar, hay compuestos casi idénticos a los dos lados y no sirve como evaluación ` +
    `estructural.`;
  destino.append(svg, pie);
}

// ---------------------------------------------------------------------------
// 7 · Cuatro de las 39 dianas no tienen con qué entrenar (2.1)
// ---------------------------------------------------------------------------
function dianas(destino, D) {
  const lista = D.actividad.dianas;
  const vacias = lista.filter((d) => d.declaradas < 10);
  const resto = lista.filter((d) => d.declaradas >= 10);
  const caja = document.createElement("div");

  const tabla = document.createElement("table");
  tabla.className = "bio-tabla";
  tabla.innerHTML =
    "<thead><tr><th>Gen</th><th>Diana</th><th>Registros</th></tr></thead><tbody>" +
    vacias.map((d) => `<tr class="mala"><td><code>${d.gen}</code></td><td>${d.diana}</td>` +
      `<td class="n">${d.declaradas}</td></tr>`).join("") +
    `<tr class="tenue"><td colspan="2">las otras ${resto.length}, de menor a mayor</td>` +
    `<td class="n">${num(resto[0].declaradas)} – ${num(resto[resto.length - 1].declaradas)}</td></tr>` +
    "</tbody>";

  const pie = document.createElement("p");
  pie.className = "lectura";
  pie.innerHTML =
    `Las 39 dianas las curó la patrocinadora a mano desde la farmacología conocida. ` +
    `<strong>Cuatro no tienen con qué entrenar.</strong> Las cifras son las que declara su propio ` +
    `archivo de dianas, sobre el conjunto completo; en el que recibimos son algo menores.`;
  caja.append(tabla, pie);
  destino.appendChild(caja);
}

// ---------------------------------------------------------------------------
// 8 · Los volúmenes por enfermedad difieren en tres órdenes (2.2)
// ---------------------------------------------------------------------------
function enfermedades(destino, D) {
  const es = D.actividad.enfermedades;
  const W = 760, H = 30 + es.length * 23, izq = 190, der = 96;
  const svg = lienzo(W, H, "Registros disponibles por enfermedad");
  const ancho = W - izq - der;
  const max = es[0].n;

  es.forEach((e, i) => {
    const y = 14 + i * 23;
    const w = Math.max((e.n / max) * ancho, 1.5);
    const pocos = e.n < 500;
    svg.append(
      h("text", { x: izq - 12, y: y + 13, "text-anchor": "end", fill: PAL.texto, "font-size": 14 }, e.nombre),
      h("rect", { x: izq, y, width: w, height: 17, fill: pocos ? PAL.alerta : PAL.resto, opacity: pocos ? 0.95 : 0.6, rx: 2 }),
      h("text", { x: izq + w + 8, y: y + 13, fill: pocos ? PAL.alerta : PAL.tenue, "font-size": 13 }, num(e.n)),
    );
  });

  const pie = document.createElement("div");
  pie.className = "lectura";
  pie.innerHTML =
    // **El alcance son cinco categorías, y está ratificado (2.1).** El pie decía
    // que el multitarea era «la única forma de incluir» las de abajo, lo que
    // prometía justo lo que esa decisión dejó fuera. El multitarea incluye las
    // dianas pequeñas **dentro** de las cinco, no otras enfermedades.
    `A escala real. Alzheimer tiene <strong>${num(es[0].n)}</strong> registros y ELA ` +
    `<strong>${num(es[es.length - 1].n)}</strong>: tres órdenes de magnitud. Las cinco de arriba son ` +
    `el alcance del proyecto; el resto se dibuja para situarlas y queda fuera por decisión ratificada. ` +
    `Dentro de esas cinco, las dianas con pocos datos entran por el modelo multitarea.`;
  destino.append(svg, pie);
}

// ---------------------------------------------------------------------------
// 9 · Qué error cuesta más, con la única regla que hoy está medida (C.5)
// ---------------------------------------------------------------------------
function costo(destino, D) {
  const T = D.tpsa;
  // **Entrenamiento, no el conjunto completo.** La serie `completo` incluye la
  // partición de prueba reservada, que no se mira para nada que se decida ni se
  // muestre. Contarla aquí no cambiaba la forma de la curva, pero ponía en
  // público un recuento sobre filas apartadas.
  const serie = T.series.entrenamiento;
  // la lista crece con el corte: más candidatos marcados, menos precisión
  const puntos = T.cortes.map((c) => {
    const [tp, fn, fp] = serie[c];
    return { corte: c, lista: tp + fp, aciertos: tp, fallidos: fp, perdidos: fn };
  }).filter((p) => p.lista >= 20);

  // arranca en el corte de la regla publicada (67 Å²), que es el que aparece en el
  // resto del mazo y en el visualizador, para que se reconozca de dónde viene
  let i = Math.max(0, puntos.findIndex((p) => p.corte >= 67));
  const caja = document.createElement("div");
  const control = document.createElement("input");
  Object.assign(control, { type: "range", min: 0, max: puntos.length - 1, step: 1, className: "bio-rango" });
  control.setAttribute("aria-label", "Qué tan larga es la lista de candidatos");
  const rejilla = document.createElement("div");
  const pie = document.createElement("p");
  pie.className = "lectura";

  function pinta() {
    const p = puntos[i];
    const prec = (100 * p.aciertos) / p.lista;
    const exh = (100 * p.aciertos) / (p.aciertos + p.perdidos);
    rejilla.className = "bio-rejilla";
    rejilla.innerHTML =
      `<div class="bio-tarjeta"><div class="t">La lista que recibe el laboratorio</div>
         <div class="v">${num(p.lista)}</div><div class="n">compuestos marcados</div></div>` +
      `<div class="bio-tarjeta"><div class="t">De esos, sí cruzan la barrera</div>
         <div class="v">${num(p.aciertos)}</div><div class="n">precisión ${prec.toFixed(0)}%</div></div>` +
      `<div class="bio-tarjeta alerta"><div class="t">Ensayos que no darán nada</div>
         <div class="v">${num(p.fallidos)}</div><div class="n">y ${num(p.perdidos)} reales quedan fuera (${(100 - exh).toFixed(0)}% perdido)</div></div>`;
    pie.innerHTML =
      `Con el corte en <strong>TPSA &lt; ${p.corte} Å²</strong>. Es la única regla que el proyecto tiene ` +
      `medida hoy, no el modelo final, pero la forma del dilema es la misma: <strong>acortar la lista sube ` +
      `la precisión y deja fuera más candidatos reales</strong>. Dónde conviene pararse depende de qué ` +
      `cuesta más en su laboratorio, y eso no lo decide la estadística.`;
    control.value = i;
  }
  control.oninput = () => { i = +control.value; pinta(); };
  pinta();
  caja.append(rejilla, control, pie);
  destino.appendChild(caja);
}

// ---------------------------------------------------------------------------
// 10 · Escalar no cambia el acierto; cambia que el modelo converja (1.5)
// ---------------------------------------------------------------------------
function escalado(destino, D) {
  const E = (D.experimentos || {}).escalado;
  if (!E) { destino.textContent = "Faltan los resultados del experimento de escalado."; return; }
  const W = 760, H = 250;
  const svg = lienzo(W, H, "MCC e iteraciones de cada transformación de escalado");
  const log = E.filter((f) => f.modelo === "LogReg");
  const rf = E.filter((f) => f.modelo === "RF");
  const orden = ["sin escalar", "estandarización", "min-max", "Yeo-Johnson"];
  const por = (lista, k) => orden.map((o) => lista.find((f) => f.transformacion === o) || {})[k];

  // panel izquierdo: el MCC, que apenas se mueve
  const izq = 120, anchoP = 230, arriba = 46, alto = H - arriba - 54;
  const maxMCC = 0.75;
  svg.appendChild(h("text", { x: izq, y: 22, fill: PAL.texto, "font-size": 15, "font-weight": 700 },
    "MCC medio · 15 evaluaciones"));
  orden.forEach((o, i) => {
    const y = arriba + i * (alto / 4);
    const l = log.find((f) => f.transformacion === o) || {};
    const r = rf.find((f) => f.transformacion === o) || {};
    svg.append(
      h("text", { x: izq - 10, y: y + 20, "text-anchor": "end", fill: PAL.texto, "font-size": 13 }, o),
      h("rect", { x: izq, y: y + 2, width: (l.mcc / maxMCC) * anchoP, height: 12, fill: PAL.resto, rx: 2 }),
      h("rect", { x: izq, y: y + 17, width: (r.mcc / maxMCC) * anchoP, height: 12, fill: PAL.natural, rx: 2 }),
      h("text", { x: izq + anchoP + 8, y: y + 13, fill: PAL.tenue, "font-size": 12 }, l.mcc?.toFixed(3)),
      h("text", { x: izq + anchoP + 8, y: y + 28, fill: PAL.tenue, "font-size": 12 }, r.mcc?.toFixed(3)),
    );
  });

  // panel derecho: las iteraciones de la regresión logística, que sí se mueven
  const izq2 = izq + anchoP + 110, anchoI = 150;
  const maxIt = Math.max(...log.map((f) => f.iteraciones || 0));
  svg.appendChild(h("text", { x: izq2, y: 22, fill: PAL.texto, "font-size": 15, "font-weight": 700 },
    "Iteraciones hasta converger"));
  orden.forEach((o, i) => {
    const y = arriba + i * (alto / 4);
    const l = log.find((f) => f.transformacion === o) || {};
    const falla = l.sin_converger > 0;
    svg.append(
      h("rect", { x: izq2, y: y + 6, width: Math.max((l.iteraciones / maxIt) * anchoI, 2), height: 18,
                  fill: falla ? PAL.alerta : PAL.resto, rx: 2 }),
      h("text", { x: izq2 + anchoI + 8, y: y + 20, fill: falla ? PAL.alerta : PAL.tenue,
                  "font-size": 12, "font-weight": falla ? 700 : 400 },
        falla ? `${num(l.iteraciones)} · no converge` : num(l.iteraciones)),
    );
  });

  const pie = document.createElement("div");
  pie.className = "lectura";
  const malo = log.find((f) => f.sin_converger > 0) || {};
  pie.innerHTML =
    `<span class="punto" style="background:${PAL.resto}"></span> regresión logística &nbsp;` +
    `<span class="punto" style="background:${PAL.natural}"></span> Random Forest &nbsp;·&nbsp; ` +
    `El acierto apenas distingue las cuatro. Lo que sí distingue es que <strong>sin escalar la ` +
    `regresión logística agota sus ${num(malo.iteraciones || 0)} iteraciones y avisa de no haber ` +
    `convergido en los ${malo.sin_converger} pliegues</strong>; su ${malo.mcc?.toFixed(3)} no es un ` +
    `desempeño, es donde se rindió el optimizador. Esa, y no el MCC, es la razón para escalar.`;
  destino.append(svg, pie);
}

// ---------------------------------------------------------------------------
// 11 · Cuánto vocabulario de Sort & Slice hace falta (1.7)
// ---------------------------------------------------------------------------
function vocabulario(destino, D) {
  const V = (D.experimentos || {}).vocabulario;
  if (!V) { destino.textContent = "Faltan los resultados del experimento de vocabulario."; return; }
  const W = 760, H = 300, izq = 56, der = 110, arriba = 20;
  const altoA = 150, hueco = 42, altoB = 54;
  const svg = lienzo(W, H, "Desempeño y cobertura según el tamaño del vocabulario");
  const Ls = [...new Set(V.puntos.map((p) => p.L))].sort((a, b) => a - b);
  const x = (L) => izq + (Math.log2(L) - Math.log2(Ls[0])) /
    (Math.log2(Ls[Ls.length - 1]) - Math.log2(Ls[0])) * (W - izq - der);
  // La escala sale de las bandas, no de un rango escrito a mano. El error estándar
  // corregido cambió de tamaño una vez —pasó a ser 2.2 veces el ingenuo y no 1.1,
  // al contar las 15 evaluaciones y no los 5 pliegues— y con el rango fijo las
  // bandas se salieron del marco sin que nada avisara.
  const extremos = V.puntos.flatMap((p) => [p.mcc - p.ee, p.mcc + p.ee]);
  const lo = Math.floor(Math.min(...extremos) * 40) / 40;
  const hi = Math.ceil(Math.max(...extremos) * 40) / 40;
  const y = (v) => arriba + altoA - ((v - lo) / (hi - lo)) * altoA;
  const colores = { LogReg: PAL.resto, RF: PAL.natural, XGB: PAL.negativo };

  const marcas = [];
  for (let v = Math.ceil(lo * 20) / 20; v <= hi + 1e-9; v += 0.05) {
    marcas.push(Math.round(v * 100) / 100);
  }
  marcas.forEach((v) => svg.append(
    h("line", { x1: izq, y1: y(v), x2: W - der, y2: y(v), stroke: PAL.rejilla, "stroke-width": 1 }),
    h("text", { x: izq - 8, y: y(v) + 4, "text-anchor": "end", fill: PAL.tenue, "font-size": 11 }, v.toFixed(2)),
  ));

  const etiquetas = [];
  Object.keys(colores).forEach((m) => {
    const ps = V.puntos.filter((p) => p.modelo === m).sort((a, b) => a.L - b.L);
    if (!ps.length) return;
    // banda de ±1 error estándar corregido: la medición casi no distingue tamaños
    const arriba_ = ps.map((p) => `${x(p.L).toFixed(1)},${y(p.mcc + p.ee).toFixed(1)}`);
    const abajo = ps.slice().reverse().map((p) => `${x(p.L).toFixed(1)},${y(p.mcc - p.ee).toFixed(1)}`);
    svg.appendChild(h("polygon", { points: [...arriba_, ...abajo].join(" "), fill: colores[m], opacity: 0.12 }));
    svg.appendChild(h("path", {
      d: ps.map((p, i) => `${i ? "L" : "M"}${x(p.L).toFixed(1)},${y(p.mcc).toFixed(1)}`).join(""),
      fill: "none", stroke: colores[m], "stroke-width": 2.2,
    }));
    const ult = ps[ps.length - 1];
    etiquetas.push({ m, x: x(ult.L) + 8, y: y(ult.mcc) + 4 });
  });
  // Los tres modelos terminan casi al mismo MCC, así que sus nombres se encimarían.
  // Se separan verticalmente lo mínimo para que se lean, conservando el orden.
  etiquetas.sort((a, b) => a.y - b.y);
  etiquetas.forEach((e, i) => {
    if (i && e.y - etiquetas[i - 1].y < 15) e.y = etiquetas[i - 1].y + 15;
    svg.appendChild(h("text", { x: e.x, y: e.y, fill: colores[e.m], "font-size": 12 }, e.m));
  });

  // franja de cobertura, abajo y con su propia escala
  const yB = arriba + altoA + hueco;
  svg.appendChild(h("text", { x: izq, y: yB - 10, fill: PAL.tenue, "font-size": 12 },
    "Cobertura del vocabulario · entrenamiento y validación"));
  V.cobertura.forEach((c) => {
    svg.append(
      h("rect", { x: x(c.L) - 11, y: yB + altoB * (1 - c.entrenamiento), width: 10,
                  height: altoB * c.entrenamiento, fill: PAL.resto, opacity: 0.55, rx: 1 }),
      h("rect", { x: x(c.L) + 1, y: yB + altoB * (1 - c.validacion), width: 10,
                  height: altoB * c.validacion, fill: PAL.negativo, opacity: 0.75, rx: 1 }),
    );
  });
  Ls.forEach((L) => svg.appendChild(h("text", {
    x: x(L), y: yB + altoB + 18, "text-anchor": "middle", fill: PAL.tenue, "font-size": 12,
  }, L === 2048 ? "2048" : `${L}`)));

  const dosmil = V.cobertura.find((c) => c.L === 2048) || {};
  const pie = document.createElement("div");
  pie.className = "lectura";
  pie.innerHTML =
    `De ${num(V.vocabulario_total)} subestructuras distintas en el entrenamiento, L se queda con las ` +
    `más frecuentes. <strong>Las bandas son ±1 error estándar corregido</strong> por la dependencia ` +
    `entre pliegues: se tocan en todo el rango medido, así que por sí solas no distinguen tamaños. La ` +
    `comparación pareada, que es la que decide, sí separa a L = 64 en Random Forest (t ≈ 3) y a ningún ` +
    `otro. Con L = 2048 la cobertura es ${(100 * dosmil.entrenamiento).toFixed(1)}% en entrenamiento y ` +
    `${(100 * dosmil.validacion).toFixed(1)}% en validación; esa brecha crece con L, porque el ` +
    `vocabulario se aprende solo del entrenamiento.`;
  destino.append(svg, pie);
}

// ---------------------------------------------------------------------------

const GRAFICAS = { grupos, naturales, tpsa, etapas, etiquetado,
                   archivo, dianas, enfermedades, costo,
                   escalado, vocabulario };

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
