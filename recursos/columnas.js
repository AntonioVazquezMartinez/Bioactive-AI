// El puente entre la estructura y las columnas de la matriz.
//
// **Qué resuelve.** El proyecto promete explicabilidad a nivel de subestructura
// —el requisito que la patrocinadora puso como no negociable— y hasta ahora eso
// se demostraba con una tabla de importancias. Aquí se ve: cada columna `fr_*`
// que esta molécula activa aparece con su cuenta, y al señalarla se resaltan los
// átomos que la producen.
//
// **Por defecto no hay que tocar nada**: la lista sale con las columnas activas
// de la molécula y la primera ya viene resaltada. Señalar o clicar es la capa de
// encima, no el estado inicial.
//
// **Lo que no se puede resaltar también se dice**, y es la mitad del mensaje: de
// las 151 columnas de la matriz, 50 son conteos `fr_*` con un patrón exacto, y
// las fisicoquímicas —TPSA, peso molecular, logP— son de la molécula entera. Un
// modelo que se apoya en TPSA explica distinto que uno que se apoya en
// `fr_lactam`.

(function () {
  let PATRONES = null;
  let cargando = null;

  async function patrones() {
    if (PATRONES) return PATRONES;
    if (!cargando) {
      cargando = fetch("recursos/patrones_fr.json")
        .then((r) => r.json())
        .then((d) => { PATRONES = d.patrones; return PATRONES; })
        .catch(() => { PATRONES = {}; return PATRONES; });
    }
    return cargando;
  }

  // Los átomos que casan con un SMARTS, como lista plana de índices.
  function atomosQueCasan(RDKit, mol, smarts) {
    let q = null;
    try {
      q = RDKit.get_qmol(smarts);
      if (!q || !q.is_valid || !q.is_valid()) return [];
      const crudo = mol.get_substruct_matches(q);
      const ms = JSON.parse(crudo || "[]");
      const vistos = new Set();
      ms.forEach((m) => (m.atoms || []).forEach((a) => vistos.add(a)));
      return [...vistos];
    } catch (_) {
      return [];
    } finally {
      if (q && q.delete) q.delete();
    }
  }

  function svgResaltado(mol, atomos) {
    if (!atomos.length) return mol.get_svg(420, 340);
    try {
      return mol.get_svg_with_highlights(JSON.stringify({
        atoms: atomos,
        width: 420, height: 340,
        highlightColour: [0.102, 0.620, 0.439],   // el verde categórico, #199e70
      }));
    } catch (_) {
      return mol.get_svg(420, 340);
    }
  }

  // La API pública: pinta la lista de columnas activas y devuelve una función
  // para repintar la molécula con una columna resaltada.
  window.puenteColumnas = async function (RDKit, smiles, destino, lienzo2d) {
    const P = await patrones();
    const mol = RDKit.get_mol(smiles);
    if (!mol || !mol.is_valid()) { if (mol) mol.delete(); return; }

    const activas = [];
    for (const [nombre, d] of Object.entries(P)) {
      const at = atomosQueCasan(RDKit, mol, d.smarts);
      if (at.length) activas.push({ nombre, atomos: at, ...d });
    }
    // Las que el proyecto usa primero, y dentro de ellas las de más átomos:
    // una columna que toca media molécula explica más que una que toca dos.
    activas.sort((a, b) =>
      (b.en_matriz === true) - (a.en_matriz === true) || b.atomos.length - a.atomos.length);

    const enMatriz = activas.filter((a) => a.en_matriz === true).length;
    const cab = document.createElement("p");
    cab.className = "vm-puente-cab";
    cab.innerHTML = activas.length
      ? `Esta molécula activa <strong>${activas.length}</strong> columnas de subestructura, ` +
        `<strong>${enMatriz}</strong> de ellas en la matriz de 151. Señala una para ver qué átomos la producen.`
      : "Esta molécula no activa ninguna columna <code>fr_*</code>. " +
        "Sus columnas son todas de propiedades globales, que no se pueden señalar en el dibujo.";

    const lista = document.createElement("div");
    lista.className = "vm-puente";
    activas.forEach((a, i) => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "vm-col" + (a.en_matriz === true ? " vm-col-usada" : "");
      b.innerHTML = `<code>${a.nombre}</code><span>${a.atomos.length} átomos</span>`;
      b.title = (a.describe || a.nombre) +
        (a.en_matriz === true ? " · llega a la matriz de trabajo"
         : a.en_matriz === false ? " · no sobrevive la selección" : "");
      const pintar = () => {
        lista.querySelectorAll(".vm-col").forEach((x) => x.classList.remove("vm-col-activa"));
        b.classList.add("vm-col-activa");
        const m = RDKit.get_mol(smiles);
        lienzo2d.innerHTML = svgResaltado(m, a.atomos);
        m.delete();
      };
      b.addEventListener("mouseenter", pintar);
      b.addEventListener("focus", pintar);
      b.addEventListener("click", pintar);
      lista.append(b);
      if (i === 0) setTimeout(pintar, 0);   // el estado por defecto ya enseña algo
    });

    const nota = document.createElement("p");
    nota.className = "vm-puente-nota";
    nota.innerHTML =
      "De las <strong>151</strong> columnas de la matriz, <strong>50</strong> son conteos " +
      "<code>fr_*</code> como estos y se pueden señalar exacto. Las fisicoquímicas " +
      "—TPSA, peso molecular, logP— son de la molécula entera y <strong>no se pueden " +
      "señalar</strong>: un modelo que se apoya en ellas explica distinto que uno que se " +
      "apoya en una subestructura.";

    destino.replaceChildren(cab, lista, nota);
    mol.delete();
  };
})();
