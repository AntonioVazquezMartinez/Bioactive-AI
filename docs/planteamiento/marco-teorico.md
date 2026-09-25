# Marco teórico

> **Estado: borrador para revisión del equipo y los asesores.** Se construyó a partir de siete ramas de investigación documentadas en [`docs/referencias/`](../referencias/README.md), que conservan la evidencia completa y las advertencias de acceso. Las citas aparecen como claves BibTeX entre backticks para sustituirse mecánicamente al fijar el formato (APA, IEEE) que pida el Tec; la bibliografía está en [`bibliografia.bib`](../referencias/bibliografia.bib), con 207 entradas al 2026-09-23.
>
> **Antes de entregar:** verificar contra doi.org toda referencia marcada como de acceso parcial o sin acceso. Varias entradas tienen metadatos que nadie del equipo ha leído.

## Contenido

1. [La barrera hematoencefálica](#1-la-barrera-hematoencefálica)
2. [Enfermedades neurodegenerativas y dianas moleculares](#2-enfermedades-neurodegenerativas-y-dianas-moleculares)
3. [Productos naturales como fuente de compuestos bioactivos](#3-productos-naturales-como-fuente-de-compuestos-bioactivos)
4. [Fundamentos de la predicción computacional de actividad](#4-fundamentos-de-la-predicción-computacional-de-actividad)
5. [Representación molecular](#5-representación-molecular)
6. [Aprendizaje automático aplicado a permeabilidad BBB](#6-aprendizaje-automático-aplicado-a-permeabilidad-bbb)
7. [Explicabilidad en modelos moleculares](#7-explicabilidad-en-modelos-moleculares)
8. [Estado del arte y hueco identificado](#8-estado-del-arte-y-hueco-identificado)

---

## 1. La barrera hematoencefálica

### 1.1 Estructura y función

La barrera hematoencefálica no es una membrana pasiva sino una interfaz celular activa cuyo componente fundamental son las células endoteliales de los microvasos cerebrales. Estas difieren del endotelio periférico en cuatro propiedades documentadas `daneman2015bloodbrain`:

- Los vasos del sistema nervioso central son **continuos y no fenestrados**, a diferencia de los capilares periféricos, que con frecuencia permiten el paso relativamente libre de solutos.
- Presentan **tasas de transcitosis vesicular extremadamente bajas**, lo que restringe el movimiento transcelular mediado por vesículas. Esto se explica en parte por la casi ausencia de PLVAP en el endotelio sano y por niveles bajos de caveolina-1.
- Poseen **mayor densidad mitocondrial** que otras células endoteliales, interpretada como el requerimiento energético para sostener los gradientes iónicos del transporte activo.
- Son inusualmente delgadas: un 39% menos gruesas que las del músculo, con menos de un cuarto de micrón separando la superficie luminal de la parenquimatosa.

**Uniones estrechas.** Sellan el espacio paracelular entre células adyacentes. Se componen de proteínas transmembranales —claudinas, ocludina y moléculas de adhesión de unión— ancladas al citoesqueleto de actina mediante adaptadores citoplasmáticos como ZO-1 y ZO-2. La **claudina-5** es la isoforma predominante en el endotelio del SNC, y su ausencia genética en ratones produce una fuga selectiva por tamaño, lo que demuestra funcionalmente su papel determinante. Las uniones crean una barrera paracelular de alta resistencia, con selectividad por tamaño para moléculas sin carga de hasta 4 nm.

**Membrana basal.** Dos membranas rodean el tubo vascular: una interna, secretada por endotelio y pericitos y rica en laminina α4/α5, y una parenquimatosa externa, secretada por astrocitos y rica en laminina α1/α2.

**Pericitos.** Células murales embebidas en la membrana basal, unidas al endotelio mediante uniones de tipo *peg-and-socket*. Su cobertura del microvaso cerebral es la más alta de cualquier tejido: la razón endotelio:pericito en el SNC va de 1:1 a 3:1, frente a 100:1 en músculo esquelético. A diferencia de los periféricos, derivan embriológicamente de la cresta neural.

**Pies terminales de astrocitos.** Envuelven casi por completo el tubo vascular y expresan distroglicano, distrofina y acuaporina-4.

**La unidad neurovascular** es el concepto integrador: el fenotipo de barrera, aunque intrínseco al endotelio, es inducido y mantenido por sus interacciones con pericitos, astrocitos, microglía y neuronas.

**Resistencia eléctrica transendotelial.** La consecuencia funcional del sellado es una resistencia extraordinariamente alta. Butt, Jones y Abbott midieron con microelectrodos *in situ* en ratas su desarrollo ontogénico: **310 Ω·cm²** en fetos de 17–20 días, **1128 Ω·cm²** desde el día 21 de gestación, y **1462 Ω·cm²** en ratas maduras, con diferencia entre vasos arteriales (1490) y venosos (918). La disrupción experimental reduce la resistencia a 100–300 Ω·cm² `butt1990electrical`. Crone y Olesen reportaron ~1870 Ω·cm² en vénulas piales de rana `crone1982electrical`.

> **Advertencia:** la cifra de ~3–30 Ω·cm² para endotelio periférico, que suele citarse como contraste, solo se localizó en fuente secundaria. Preferir Butt et al. (1990) como fuente primaria.

**Función fisiológica.** La barrera excluye componentes neurotóxicos del plasma y regula activamente el intercambio de solutos `sweeney2019bloodbrain`. La justificación es directa: la señalización neuronal depende de una regulación estrecha de las concentraciones extracelulares de iones y neurotransmisores, incompatible con las fluctuaciones del compartimento sanguíneo `abbott2010structure`.

> **Vacío identificado:** no se localizó, en las fuentes consultadas, un desarrollo explícito de la justificación evolutiva de la barrera. Conviene cubrirlo con una fuente dedicada si el capítulo lo requiere.

### 1.2 Mecanismos de transporte

**Difusión transcelular pasiva.** Es la ruta más relevante para fármacos de molécula pequeña. Pardridge sintetiza las reglas empíricas: las moléculas pequeñas cruzan en cantidades farmacológicamente significativas si su masa molecular es menor a 400–500 Da y forman menos de 8–10 puentes de hidrógeno con el agua `pardridge2005bottleneck`. De forma más precisa, la permeación **cae 100 veces** cuando el peso aumenta de 300 a 450 Da, con una reducción de aproximadamente diez veces por cada puente de hidrógeno adicional `pardridge2012drugtransport`.

La relación no es simplemente proporcional a la lipofilicidad: la permeación cae 100 veces cuando el área superficial molecular aumenta de 52 Å² a 105 Å², indicando que el área molecular —no solo el coeficiente de partición— determina la difusión `fischer1998bloodbrain`. El ejemplo canónico es la conversión de morfina en heroína: al acetilar los hidroxilos y reducir la capacidad de formar puentes de hidrógeno, la penetración **aumenta 100 veces**. Es la reducción de polaridad, más que un aumento genérico de lipofilicidad, el determinante mecanístico.

**Transporte paracelular.** Prácticamente abolido en la barrera sana por el sellado de las uniones estrechas, lo que es consistente con los valores altos de resistencia.

**Transporte mediado por acarreadores.** Permite el paso de nutrientes polares mediante transportadores SLC específicos: GLUT1 para glucosa, MCT1 para lactato, LAT1 para aminoácidos neutros grandes. LAT1 tiene relevancia farmacológica directa: **la L-DOPA cruza la barrera explotando LAT1**, por ser ella misma un aminoácido neutro grande `pardridge2012drugtransport`. Existen además transportadores SLC de eflujo, de las familias OATP y OAT3, que trabajan coordinadamente con los transportadores ABC `kusuhara2005active`.

**Transcitosis mediada por receptor.** Transporta macromoléculas mediante unión a receptores luminales: receptor de transferrina, receptor de insulina y LRP1, este último implicado en el aclaramiento cerebro-sangre del péptido β-amiloide. Un detalle contraintuitivo: **la afinidad del ligando debe ajustarse, no maximizarse**, porque los formatos de alta afinidad atrapan el complejo en vías de reciclaje en vez de liberarlo del lado cerebral `pulgar2018transcytosis`. La aplicación clínica más avanzada es un anticuerpo anti-receptor de insulina fusionado a iduronidasa para síndrome de Hurler, el primer uso clínico de esta estrategia.

**Transcitosis adsortiva.** No depende de un receptor específico sino de interacciones electrostáticas entre moléculas catiónicas y la superficie de membrana, de carga neta negativa. Es no saturable, de menor afinidad y mayor capacidad que la anterior.

**Eflujo activo.** Es el mecanismo de mayor relevancia práctica para este proyecto. Explica por qué un compuesto que satisface las reglas fisicoquímicas de permeación pasiva puede, aun así, no alcanzar concentraciones terapéuticas. Los transportadores pertenecen a la superfamilia ABC y se localizan en la membrana luminal, bombeando de vuelta a la sangre los fármacos que ya entraron por difusión `loscher2005bloodbrain`.

La **glicoproteína-P** es cuantitativamente notable: en ratones carentes de ella, la penetración cerebral de sus sustratos **puede aumentar de 10 a 100 veces**. Su especificidad es amplia: anticancerígenos, antiepilépticos, antidepresivos, inhibidores de proteasa del VIH, opioides y corticosteroides. El caso de la morfina ilustra el vínculo con el efecto farmacodinámico: en ratones deficientes, el mayor acceso cerebral se asocia a mayor efecto analgésico.

**BCRP** comparte polaridad luminal y muestra compensación funcional: los ratones carentes de glicoproteína-P expresan alrededor del triple de BCRP. Las **MRP** tienen localización subcelular menos resuelta.

La consecuencia conceptual es central para este trabajo: *"un número muy significativo de moléculas liposolubles, entre ellas muchos fármacos útiles, tiene menor permeabilidad cerebral de la que predeciría su solubilidad en lípidos"* `loscher2005bloodbrain`. Difusión pasiva y eflujo compiten cinéticamente dentro de la misma célula, y el eflujo frecuentemente gana. El efecto neto se gobierna por la razón entre el aclaramiento por glicoproteína-P y la permeabilidad de la membrana — antecedente conceptual directo de la razón de eflujo moderna.

**Por eso un modelo que prediga el cruce de la barrera únicamente a partir de descriptores de permeabilidad pasiva derivados del SMILES resulta insuficiente sin incorporar, explícita o implícitamente, información sobre el reconocimiento del compuesto por glicoproteína-P, BCRP y MRP.**

De aquí se sigue además la decisión de etiquetado que adopta este trabajo: **la etiqueta BBB+/BBB− no se interpreta como propiedad intrínseca del compuesto**, sino como clase de permeabilidad bajo las condiciones de ensayo y la convención de umbral de la literatura fuente `spielvogel2025standardized`.

### 1.3 El fracaso del desarrollo de fármacos para el SNC

Es difícil encontrar un texto introductorio que no repita alguna variante de que "el 98% de las moléculas pequeñas y prácticamente el 100% de las grandes no cruzan la barrera". Dado que los asesores señalaron que este tipo de cifras se repiten sin atribución, se rastreó su origen.

La cifra alcanza su difusión más amplia en Pardridge (2005) `pardridge2005bottleneck`. El resumen la establece **sin cita asociada**. Al rastrear el cuerpo del texto en busca del sustento cuantitativo, este descansa en dos trabajos: uno reporta que de más de 7,000 fármacos de una base de química medicinal, solo el 5% trata el SNC `ghose1999knowledgebased`; el otro, que solo el 12% de los fármacos eran activos en el SNC `lipinski2000druglike`.

**Esto obliga a una advertencia metodológica.** Ninguno de los dos mide directamente la permeabilidad de la barrera en un panel definido de compuestos: ambos analizan qué fracción de los fármacos de bases comerciales tiene indicación clínica para el SNC. Es un indicador indirecto —la proporción de compuestos que llegaron a comercializarse como terapias del SNC—, no una medición experimental de cruce. Un compuesto puede no haberse convertido en fármaco del SNC por razones ajenas a su capacidad de cruzar. Además, el 100% atribuido a moléculas grandes **no tiene cita ni conjunto de datos asociado** en ningún punto del artículo.

Como verificación cruzada, en un trabajo posterior y más técnico del mismo autor **no se repiten las cifras textuales**; el argumento se reformula en términos cualitativos `pardridge2012drugtransport`.

**Recomendación:** presentar la cifra explícitamente como una aproximación de orden de magnitud, ampliamente repetida y atribuible a Pardridge (2005), pero fundamentada en datos indirectos y en un argumento fisicoquímico heurístico, no como una estadística derivada empíricamente de ensayos de permeabilidad.

### 1.4 Estrategias para favorecer el cruce

Que un compuesto se clasifique como BBB− no implica descartarlo: existe un repertorio consolidado de estrategias. Esta sección justifica una decisión de diseño del proyecto — **la etapa 1 no opera como filtro duro sobre la etapa 2**.

**Profármacos.** Derivados bioreversibles que adquieren las propiedades necesarias para cruzar y se reconvierten en el fármaco activo dentro del cerebro. Se estima que entre el 5 y el 7% de los fármacos aprobados en el mundo son profármacos `rautio2008prodrugs`. El caso paradigmático es la L-DOPA, que explota LAT1 y se convierte en dopamina por la dopa-descarboxilasa `lloyd1970parkinson`.

**Lipidización.** Modificación química para favorecer la difusión pasiva, con el ejemplo morfina→heroína como ilustración.

**Caballos de Troya moleculares.** Diseñar el fármaco, o conjugarlo con ligandos, para ser reconocido por los sistemas de transporte endógenos. Es particularmente relevante para macromoléculas sin otra vía de acceso `pardridge2006trojan`.

**Nanoacarreadores.** Nanopartículas recubiertas con polisorbato 80 adsorben apolipoproteína E, imitando partículas de LDL e interactuando con su receptor. Nanopartículas cargadas con doxorrubicina lograron cura del 40% en ratas con glioblastomas intracraneales `kreuter2001nanoparticulate, gulyaev1999significant`.

**Ultrasonido focalizado con microburbujas.** Abre transitoriamente la barrera sin modificar el fármaco, sin dañar el tejido circundante `hynynen2001noninvasive, mcdannold2005mri`.

**Administración intranasal.** Aprovecha la conexión anatómica directa entre mucosa olfatoria y SNC, evitando la circulación sistémica `lochhead2012intranasal`.

### 1.5 Medición experimental: qué significan realmente las etiquetas

Esta sección es de importancia directa para el proyecto: las etiquetas BBB+/BBB− que alimentarán el modelo provienen de una combinación heterogénea de los ensayos siguientes, cada uno de los cuales mide un aspecto distinto —y no siempre concordante— del fenómeno.

**logBB y la razón cerebro-plasma.** Es la razón logarítmica entre la concentración total de fármaco en tejido cerebral y en plasma. Sus limitaciones se exponen con contundencia: *"logBB simplemente proporciona una estimación in vivo de lipofilicidad más que estimaciones relevantes de distribución cerebral"* `hammarludenaes2008rate`. El problema de fondo es que la concentración total está confundida por la unión a proteínas plasmáticas y por la partición del fármaco a componentes del propio tejido cerebral: una concentración alta puede reflejar partición tisular inespecífica, no disponibilidad farmacológica. Cuantitativamente, entre fármacos activos en el SNC, Kp,uu difiere hasta ~150 veces mientras que logBB difiere **al menos 2,000 veces**: una varianza enorme y poco informativa, impulsada por artefactos de unión.

**Kp,uu — el coeficiente de partición de fracción libre.** Razón entre la concentración libre en el líquido intersticial cerebral y la libre en plasma. Es preferido porque es independiente de la unión a proteínas y ofrece una descripción directa de cómo la barrera maneja el fármaco: **Kp,uu = 1** indica equilibración pasiva, **< 1** dominancia de eflujo neto, **> 1** dominancia de influjo. Es *"probablemente el parámetro más relevante para predecir qué fármacos serán activos en el SNC"*. Una encuesta a la industria reporta que el 56% de las compañías usa un umbral de Kp,uu > 0.3–0.5 `loryan2022unbound`.

**Perfusión cerebral *in situ*.** Aísla el transporte a través de la barrera de la farmacocinética sistémica. En ratones carentes de glicoproteína-P, la captación cerebral de colchicina aumentó de dos a cuatro veces `dagenais2000development`. Es la aproximación *in vivo* más limpia disponible, aunque invasiva y de bajo rendimiento `takasato1984insitu, smith2024brain`.

**PAMPA-BBB.** Ensayo no celular basado en una membrana artificial de fosfolípidos, de alto rendimiento y bajo costo `di2003high`. Al carecer de maquinaria celular, **mide exclusivamente difusión pasiva y es ciego a transportadores**: un compuesto puede resultar PAMPA-positivo y comportarse como BBB-negativo *in vivo* si es sustrato de glicoproteína-P.

**MDCK-MDR1.** Línea celular transfectada para sobreexpresar glicoproteína-P humana. El estudio fundacional, con 93 fármacos comercializados, propone la regla práctica de que un fármaco debería tener permeabilidad pasiva mayor a 150 nm/s y no ser buen sustrato de glicoproteína-P, con razón de eflujo menor a 2.5 `mahardoan2002passive`.

**Discrepancias documentadas.** Este es el hallazgo más relevante de la sección: al comparar directamente los tres métodos, **PAMPA-BBB correlacionó significativamente con la perfusión cerebral *in situ*, mientras que MDR1-MDCKII no mostró correlación alguna** `di2009comparison`. Es contraintuitivo: la membrana artificial sin células predijo mejor que la línea celular con glicoproteína-P humana. La razón mecanística propuesta es que la membrana de MDCK tiene proporciones de fosfolípido a colesterol distintas de las del endotelio cerebral, mientras que la mezcla sintética de PAMPA se asemeja más.

Una comparación multi-laboratorio halló correlaciones modestas con el conjunto completo de compuestos, pero sustancialmente mejores al restringirse a compuestos de difusión puramente pasiva, y concluye que **es probable que se necesiten baterías de pruebas, no un único ensayo sustituto universal** `garberg2005invitro`. Otro trabajo abre afirmando sin ambigüedad que *"actualmente no existe un modelo estándar de la industria para penetración de fármacos en la BHE"* `hellinger2012comparison, lohmann2002predicting`.

**Implicación directa.** Dado que las etiquetas provienen de una mezcla de estos ensayos —PAMPA ciego al eflujo; MDCK-MDR1 sin correlación con perfusión; logBB confundido por partición y unión; Kp,uu conceptualmente más limpio pero el menos disponible en bases públicas—, **es previsible que el conjunto de entrenamiento contenga ruido de etiquetado no aleatorio, correlacionado con el tipo de ensayo de origen de cada compuesto**. Es una limitación que debe discutirse explícitamente, y motiva auditar la procedencia experimental de cada etiqueta en la medida de lo posible.

### 1.6 Reglas fisicoquímicas clásicas

El descriptor con mayor poder predictivo individual es el área de superficie polar topológica. La regla clásica sitúa el umbral cerca de 90 Å² `clark1999tpsa_bbb, ertl2000tpsa`. Umbrales específicos de SNC más detallados: TPSA ≤ 90 Å², logP óptimo entre 1.5 y 2.7, suma de heteroátomos N+O ≤ 5, HBD ≤ 3, peso molecular < 450 `pajouhesh2005`.

Sin embargo, Tiwari et al. rederivaron los umbrales sobre B3DB y encontraron que el óptimo está en **66.8 Å²** (AUC 0.746), calificando el valor tradicional de demasiado permisivo. Su regla de dos parámetros, **TPSA < 67 Å² y HBD ≤ 1**, alcanza 96.6% de precisión con especificidad de 0.852 `tiwari2026umbrales`.

Sobre ese mismo conjunto, la regla simple **supera a las compuestas clásicas**:

| Regla | AUC |
|---|---|
| TPSA < 67 Å² y HBD ≤ 1 | 0.720 |
| CNS MPO ≥ 4 | 0.625 |
| Veber | 0.566 |
| Lipinski | 0.546 |

El **score CNS MPO** combina seis parámetros —cLogP, cLogD a pH 7.4, peso molecular, TPSA, HBD y pKa del centro más básico— puntuados de 0 a 1 y sumados `wager2010cnsmpo`.

Estas reglas cumplen doble función: son descriptores de entrada y, sobre todo, el **criterio de verificación** de las explicaciones del modelo. Una atribución que contradiga la dominancia empírica de TPSA y HBD es señal de investigar el modelo antes de formular una interpretación biológica.

---

## 2. Enfermedades neurodegenerativas y dianas moleculares

### 2.1 Enfermedad de Alzheimer

**Procesamiento de APP.** La proteína precursora amiloide se procesa por dos vías competitivas. En la no amiloidogénica, la α-secretasa corta dentro del dominio de Aβ, impidiendo su formación. En la amiloidogénica, la β-secretasa (BACE1) corta primero generando el fragmento C99, procesado después por el complejo γ-secretasa en los sitios Val40 y Ala42, generando Aβ40 y Aβ42 `obrien2011amyloid`. Aβ42 es más hidrofóbico y agrega con mayor facilidad, por lo que aunque es la especie minoritaria se considera desproporcionadamente relevante.

**La hipótesis de la cascada amiloide** postula que la acumulación de Aβ es el evento primario que dirige la patogénesis, y que el resto del proceso —incluidos los ovillos de tau— resulta de un desequilibrio entre producción y aclaramiento `hardy2002amyloid`. Un matiz importante: la toxicidad no se atribuye hoy principalmente a las placas fibrilares insolubles sino a **oligómeros solubles difusibles**, que matan neuronas en cultivo a concentraciones nanomolares e inhiben la potenciación a largo plazo sin necesidad de fibrilación `lambert1998diffusible`.

**La hipótesis está seriamente cuestionada y el debate sigue abierto.** Varios fármacos dirigidos a reducir la producción o agregación de Aβ fracasaron en fase III, lo que obliga a revisar qué constituiría una prueba válida `karran2011amyloid`. De forma más contundente, Herrup argumenta que existe evidencia creciente incompatible con la estructura lineal de la hipótesis y propone abiertamente su rechazo `herrup2015case`.

**Tau.** La proteína asociada a microtúbulos se hiperfosforila y forma los ovillos neurofibrilares. **GSK-3β fosforila tau en ~85 sitios**, cubriendo la mayoría de los residuos hiperfosforilados en cerebro con Alzheimer; su sobreexpresión en ratones produce neurodegeneración dependiente de tau `sayas2021gsk3`. El ARNm de **CK1δ está sobreexpresado hasta 24 veces** en el hipocampo de cerebro con Alzheimer, correlacionado con la carga regional de patología tau, y su actividad es estimulada por Aβ, sugiriendo un nexo entre ambas patologías `yasojima2000casein`.

**Hipótesis colinérgica.** Estableció que existe disfunción colinérgica significativa en el SNC envejecido y demente, con relación a la pérdida de memoria `bartus1982cholinergic`. Es la base racional de los inhibidores de acetilcolinesterasa.

**Anticuerpos anti-amiloide: resultados honestos.** Dos monoclonales fueron aprobados recientemente y ambos ofrecen evidencia mixta que **no debe presentarse como validación definitiva**.

*Lecanemab* `vandyck2023lecanemab`: fase 3, 18 meses, 1,795 participantes. El cambio ajustado en CDR-SB (rango 0–18) fue 1.21 contra 1.66 con placebo, una **diferencia absoluta menor a medio punto en una escala de 18**. Reducción de carga amiloide de −59.1 centiloides. Seguridad: reacciones a la infusión en 26.4% y **ARIA-E en 12.6%**.

*Donanemab* `sims2023donanemab`: fase 3, 1,736 participantes, 76 semanas. En la población con tau baja/media, 35.1% de enlentecimiento del declive; en la **población completa**, más representativa de la práctica clínica, cae a **22.3%**. Seguridad: ARIA-E en **24.0%**, ARIA-H en **31.4%**, y **3 muertes atribuidas a ARIA grave**.

**Interpretación para el marco teórico:** ambos reducen de forma robusta la carga amiloide, lo cual es la evidencia biomarcadora más sólida de participación causal. Pero el beneficio clínico es modesto y el riesgo de ARIA no es trivial. Esto es consistente con —sin refutar ni validar limpiamente— la crítica de Herrup: el amiloide parece participar causalmente, pero removerlo no detiene la enfermedad de forma dramática.

### 2.2 Enfermedad de Parkinson

**α-sinucleína y cuerpos de Lewy.** Los cuerpos de Lewy se tiñen fuertemente con anticuerpos contra α-sinucleína, que se concluyó ser su componente principal `spillantini1997alpha`. El mismo año se identificó una mutación en el gen SNCA con herencia autosómica dominante, la primera mutación específica asociada a la enfermedad `polymeropoulos1997mutation`. Juntos establecieron que la agregación de α-sinucleína es genéticamente causal y patológicamente definitoria.

**Disfunción mitocondrial.** El hallazgo fundacional es la actividad deficiente del **complejo I** mitocondrial en la sustancia negra de pacientes fallecidos, un defecto idéntico al producido por MPTP, la neurotoxina que también causa parkinsonismo en humanos `schapira1989mitochondrial`. Conecta disfunción mitocondrial, estrés oxidativo y muerte selectiva de las neuronas dopaminérgicas, particularmente vulnerables por su alta demanda energética, su gran arborización axonal no mielinizada y la autooxidación de la dopamina.

**Formas genéticas.** Cuatro genes mayores convergen mecanísticamente:

- **Parkin**: causa el parkinsonismo juvenil autosómico recesivo; su proteína tiene similitud con ubiquitina y un motivo RING, sugiriendo participación en la vía proteolítica dependiente de ubiquitina `kitada1998mutations`.
- **PINK1**: se localiza en la mitocondria y ejerce un efecto protector que se pierde con las mutaciones `valente2004hereditary`. PINK1 y parkin actúan en la misma vía de control de calidad mitocondrial: PINK1 se acumula en mitocondrias despolarizadas y recluta a parkin.
- **LRRK2**: sus portadores muestran degeneración dopaminérgica con patologías sorprendentemente diversas, sugiriendo que puede ser central en varios trastornos distintos `zimprich2004mutations, paisanruiz2004cloning`. Es hoy diana de inhibidores en desarrollo clínico.
- **GBA**: el mayor estudio multicéntrico (5,691 pacientes, 4,898 controles) encontró un **odds ratio de 5.43** para cualquier mutación `sidransky2009multicenter`. Vincula la disfunción del sistema autofagia-lisosoma con la acumulación de α-sinucleína.

En conjunto apuntan a tres ejes: agregación de α-sinucleína, disfunción mitocondrial, y falla del sistema ubiquitina-proteasoma y autofagia-lisosoma.

### 2.3 Mecanismos compartidos

Son operacionalmente importantes porque son, en la práctica, lo que la mayoría de los ensayos de neuroprotección intentan modular.

**Estrés oxidativo y disfunción mitocondrial.** En todas las enfermedades neurodegenerativas mayores hay evidencia sólida de que la disfunción mitocondrial ocurre tempranamente y actúa causalmente `lin2006mitochondrial`.

**Neuroinflamación.** La activación de Aβ sobre el inflamasoma NLRP3 en microglía es fundamental para la maduración de IL-1β. Ratones carentes de NLRP3 o caspasa-1 con mutaciones familiares quedaron ampliamente protegidos de la pérdida de memoria espacial, con mayor aclaramiento de Aβ `heneka2013nlrp3`. Sobre COX-2 conviene una advertencia contra la simplificación: aunque se asocia con actividad proinflamatoria, también se expresa constitutivamente contribuyendo a actividad sináptica y consolidación de memoria, y la evidencia de un papel directo en neurodegeneración sigue siendo controvertida `minghetti2004cox2`. Respecto a iNOS, el exceso de óxido nítrico participa tanto en muerte celular como en reparación `heneka2001inos`.

**Excitotoxicidad.** El glutamato extracelular excesivo sobreactiva el receptor NMDA, causando sobrecarga de calcio que activa proteasas dañinas, en paralelo a generación de especies reactivas y disfunción mitocondrial. Es la base racional de la memantina.

**Falla de proteostasis.** Atraviesa transversalmente las secciones anteriores: la acumulación de Aβ, tau y α-sinucleína mal plegadas refleja en parte una falla del control de calidad proteico.

### 2.4 Qué significa "neuroprotección" como afirmación científica

Operacionalmente, es la afirmación de que una intervención reduce la muerte o disfunción neuronal causada por alguno de los mecanismos anteriores, demostrada normalmente en cultivo o en modelos animales. **El problema central es que casi nunca se traduce en beneficio clínico.**

La evidencia cuantitativa más citada: de **1,026 tratamientos neuroprotectores** identificados experimentalmente en ictus, solo 114 llegaron a ensayarse en humanos, y **ninguno mostró eficacia clínica establecida**. Los autores no encontraron evidencia de que los fármacos usados clínicamente fueran experimentalmente más efectivos que los probados solo en animales, concluyendo que existe un problema sistemático en cómo se seleccionan los fármacos que avanzan `ocollins2006experimental`.

El caso paradigmático es **NXY-059**, un atrapador de radicales libres. Tras un ensayo inicial prometedor, el confirmatorio con 3,306 pacientes no encontró ninguna diferencia frente a placebo `shuaib2007nxy059`, y el análisis agrupado con 5,028 pacientes confirmó la ineficacia `diener2008nxy059pooled`. Es ilustrativo precisamente porque **sí había mostrado neuroprotección robusta en modelos animales**: el fracaso no fue por falta de mecanismo plausible sino de traducción.

**Implicación directa para este trabajo.** Las conclusiones de un modelo que predice actividad neuroprotectora deben formularse con cautela epistemológica. El lenguaje apropiado es **"actividad neuroprotectora predicha según mecanismo molecular"**, nunca "compuesto neuroprotector" sin calificar. Esta tasa histórica de fracaso debe explicitarse como limitación reconocida del enfoque, no como nota al pie.

### 2.5 Dianas moleculares: racional y evidencia

ChEMBL no tiene categoría "SNC" ni de neurodegeneración: su jerarquía es curada a medida, de modo que la selección debe construirse manualmente.

| Diana | Racional | Evidencia clínica |
|---|---|---|
| **AChE / BuChE** | Hipótesis colinérgica; la inhibición aumenta acetilcolina sináptica | Base de donepezilo, rivastigmina y **galantamina**, esta última de origen natural |
| **MAO-B / MAO-A** | La MAO-B metaboliza dopamina; su inhibición reduce el catabolismo dopaminérgico | Selegilina: el ensayo DATATOP mostró retraso significativo del inicio de discapacidad (HR 0.50), ~9 meses de diferencia mediana `parkinsonstudygroup1993tocopherol` |
| **BACE1** | Bloquear la generación de Aβ en el primer paso | **Fracasó con daño.** Verubecestat se terminó por futilidad pese a reducir Aβ en LCR 63–81% `egan2018verubecestat`; en Alzheimer prodrómico la **dosis alta empeoró** el CDR-SB (2.02 contra 1.58, p=0.01) con mayor progresión a demencia (HR 1.38) `egan2019verubecestat` |
| **Receptor NMDA** | Bloquear la sobreestimulación glutamatérgica sin bloquear la transmisión fisiológica | Memantina: mejoría significativa en CIBIC-Plus, ADCS-ADLsev y Severe Impairment Battery `reisberg2003memantine` |
| **Adenosina A2A** | Mecanismo no dopaminérgico sobre la vía estriatal indirecta | Istradefilina: redujo el tiempo "off" en **1.8 horas** contra 0.6 con placebo `lewitt2008istradefylline`. Primer fármaco no dopaminérgico aprobado para Parkinson en dos décadas |
| **Sigma-1 / sigma-2** | Chaperona molecular que regula homeostasis de calcio y bioenergética mitocondrial | Aplicaciones emergentes, pero **sin ensayo de fase III definitivo** dirigido puramente por mecanismo sigma `pergolizzi2023sigma` |
| **GSK-3β / CK1δ** | Inhibir la hiperfosforilación de tau en origen | Evidencia sólida en modelos animales, **sin inhibidor aprobado ni éxito robusto en fase III** |
| **Nrf2 / KEAP1** | Factor de transcripción que activa genes antioxidantes | Función alterada en varias enfermedades; activadores protectores en modelos `dinkovakostova2018nrf2`. Sin validación clínica en neurodegeneración |
| **COX-2, iNOS, NLRP3** | Neuroinflamación | Dianas emergentes, **no validadas clínicamente** |

> **Advertencias:** BACE1 es el caso más claro de que reducir Aβ no solo no ayuda sino que puede empeorar el cuadro, posiblemente por efectos fuera de diana sobre otros sustratos fisiológicos. Y la lista no se contrastó diana por diana contra los identificadores vivos de ChEMBL; hay que verificar los `target_chembl_id` al implementar.

---

## 3. Productos naturales como fuente de compuestos bioactivos

### 3.1 El caso de éxito real: galantamina

La galantamina, alcaloide aislado de *Galanthus nivalis* y otras Amaryllidaceae, es el ejemplo más sólido de producto natural convertido en fármaco aprobado para Alzheimer: un inhibidor de acetilcolinesterasa con aprobación regulatoria plena. Su trayectoria va desde observaciones etnobotánicas en el Cáucaso, pasando por su uso en Europa del Este, hasta su introducción en mercados occidentales `heinrich2004galanthamine`.

**Es la prueba de concepto de que la ruta producto natural → diana validada → fármaco aprobado funciona. Pero es la excepción, no la norma.**

### 3.2 Casos con evidencia clínica débil o negativa

- **Huperzina A**: el ensayo de fase II (n=210) encontró que la dosis primaria **no mostró beneficio cognitivo** a 16 semanas. Clasificación de evidencia del propio estudio: Clase III `rafii2011huperzine`.
- **Ginkgo biloba**: el ensayo GuidAge (n=2,854, 5 años de seguimiento) dio HR 0.84 (IC95% 0.60–1.18; p=0.306), **no significativo**. El extracto a largo plazo no redujo el riesgo de progresión a Alzheimer `vellas2012guidage`.
- **Resveratrol**: el ensayo de fase 2 (n=119) encontró que penetra la barrera y altera algunos biomarcadores, pero **el volumen cerebral se redujo más que con placebo** —un hallazgo potencialmente adverso— sin beneficio clínico demostrado `turner2015resveratrol`.

### 3.3 El problema PAINS: por qué muchos hits son falsos positivos

Este es el punto metodológicamente más importante para la priorización de compuestos del proyecto.

Los filtros de subestructura para identificar **compuestos de interferencia pan-ensayo (PAINS)** identifican compuestos que aparecen como hits frecuentes no por actividad específica genuina sino por mecanismos de interferencia —reactividad covalente inespecífica, actividad redox, interferencia espectroscópica, agregación coloidal— y que no son detectados por los filtros convencionales `baell2010pains`.

**La curcumina es el caso mejor documentado.** Se clasifica tanto como PAINS como panacea metabólica inválida. Su falsa actividad probable ha llevado a **más de 120 ensayos clínicos**, de los cuales **ninguno controlado con placebo y doble ciego ha tenido éxito**. Los autores concluyen que es un compuesto inestable, químicamente reactivo, no biodisponible, y por tanto un candidato altamente improbable `nelson2017curcumin`.

El fenómeno no es exclusivo. Al minar sistemáticamente más de 80 años de literatura fitoquímica se encontró que **solo 39 compuestos concentran la mayoría de los reportes** de ocurrencia y actividad entre productos naturales, todos con bioactividades múltiples y poco específicas `bisson2016invalid`.

Mecanísticamente hay una explicación física directa: al examinar cinco fenoles bioactivos —capsaicina, **curcumina**, **EGCG**, genisteína y resveratrol— mediante dinámica molecular y ensayos funcionales, se demostró que **cada uno altera las propiedades de la bicapa lipídica y modula indiscriminadamente la función de proteínas de membrana no relacionadas entre sí**. Muchos de los efectos reportados se deben a perturbación inespecífica de membrana, no a unión específica a proteína `ingolfsson2014phytochemicals`. Es exactamente el tipo de interferencia que los filtros PAINS clásicos no reconocen, por haber sido diseñados para reactividad covalente.

**Implicación operativa para el pipeline:** (a) aplicar filtros de subestructura tipo Baell a los candidatos antes de reportarlos como hits, (b) tratar con escepticismo particular cualquier predicción de alta actividad para curcumina, EGCG y análogos estructurales —polifenoles galoilados, catecoles—, y (c) documentar explícitamente que un hit computacional para estos compuestos coincide con la literatura de interferencia conocida, no con actividad neuroprotectora genuina.

---

## 4. Fundamentos de la predicción computacional de actividad

### 4.1 Orígenes históricos del QSAR

La legitimidad de predecir actividad biológica a partir de estructura química tiene su origen formal en 1964, en dos trabajos independientes y conceptualmente distintos.

**Hansch y Fujita** establecieron la ecuación que lleva su nombre: un modelo de regresión lineal múltiple que relaciona la actividad biológica con parámetros fisicoquímicos de los sustituyentes — el parámetro hidrofóbico π, precursor directo del logP; la constante electrónica de Hammett σ; y el parámetro estérico de Taft `hansch1964`. La contribución conceptual fue tratar la interacción fármaco-receptor con la misma lógica de las relaciones lineales de energía libre de la química orgánica física.

La razón para adoptar el sistema octanol-agua como sustituto de la hidrofobicidad es que el octanol posee simultáneamente una cabeza polar y una cola hidrofóbica larga, lo que lo convierte en un mimetismo razonable del entorno anfipático que una molécula debe atravesar.

**Free y Wilson** propusieron un enfoque distinto: en lugar de regresar sobre parámetros fisicoquímicos continuos, codifican la presencia o ausencia de cada sustituyente como variables indicadoras binarias, expresando la actividad como suma de contribuciones aditivas `freewilson1964`. El contraste conviene establecerlo con claridad: **Hansch es paramétrico y mecanicista**, con descriptores físicamente interpretables y transferibles entre series; **Free-Wilson es puramente estructural-aditivo**, sin requerir datos externos pero con contribuciones no transferibles a otro andamiaje. Ambos son lineales y ambos son precursores directos del QSAR moderno `gogishvili2021`.

La evolución hacia alta dimensionalidad y aprendizaje automático está documentada en dos revisiones extensas `cherkasov2014, muratov2020`: los descriptores estéricos evolucionaron de Taft a STERIMOL a campos 3D; la expansión hacia índices de conectividad e índices topológicos permitió trabajar con conjuntos estructuralmente diversos y no congenéricos; y el QSAR de clasificación extendió el marco más allá de la regresión continua. Un dato útil para justificar el uso de modelos clásicos: **las redes neuronales profundas mostraron en promedio solo ~0.04 más de R² que *random forests*** a través de varios benchmarks `muratov2020`.

> **Advertencia:** los artículos originales de 1964 están tras muro de pago de ACS y no están indexados con resumen. Su contenido se confirmó indirectamente a través de las revisiones históricas citadas.

### 4.2 El principio de similitud y sus límites

El supuesto sobre el que descansa todo el proyecto —que moléculas estructuralmente similares tienden a tener propiedades similares— se conoce como **principio de similitud-propiedad** y se atribuye convencionalmente al libro editado por Johnson y Maggiora en 1990.

Un matiz importante para el rigor de la tesis: **el libro de 1990 nunca usa literalmente esa frase** `dalke2020`. El término se formaliza años después `maggiora2014`. Las convenciones de cita correctas son, entonces: citar Johnson y Maggiora (1990) como la obra que consolidó el concepto, y Maggiora et al. (2014) como la fuente donde se acuñó formalmente el término.

La crítica central que la tesis debe reconocer: *"la similitud es un concepto subjetivo y multifacético… Los métodos de similitud y las lecturas numéricas de cálculos de similitud están probablemente entre los enfoques computacionales peor entendidos en química medicinal"* `maggiora2014`. La similitud molecular **no es una propiedad intrínseca y objetivamente medible**, sino que depende del descriptor, el fingerprint y la métrica de distancia elegidos `bajorath2017`.

El punto donde el principio se rompe empíricamente es el de los **acantilados de actividad**: pares de compuestos estructuralmente muy similares con diferencias grandes de potencia. El comentario que dio visibilidad al fenómeno corrigió la práctica previa de descartarlos como valores atípicos, reencuadrándolos como fenómeno estructural fundamental `maggiora2006, stumpfe2019`. Son instancias de discontinuidad de la relación estructura-actividad que resultan perjudiciales para el modelado. El marco de doble filo es directamente relevante: *"mientras que los químicos medicinales pueden aprovechar regiones del espacio químico ricas en acantilados de actividad, los practicantes de QSAR necesitan escapar de dichas regiones"* `cruzmonteagudo2014`.

### 4.3 Dominio de aplicabilidad

El concepto de que un modelo solo es válido dentro de la región del espacio químico representada por sus datos de entrenamiento se formalizó en un reporte del taller ECVAM `netzeva2005`, y su desarrollo más citable revisa las familias de métodos `sahigara2012`: basados en rango, en distancia geométrica, en densidad de probabilidad y en *leverage*.

El método de *leverage* se define a partir de la matriz sombrero **H = X(XᵀX)⁻¹Xᵀ**, con un umbral convencional **h\* = 3p/n**; los compuestos con h > h* se consideran fuera del dominio.

> **Nota metodológica:** existe una discrepancia real en la literatura entre las convenciones h* = 3p/n y h* = 3(p+1)/n, según si el intercepto se cuenta entre los parámetros. **El capítulo de metodología debe declarar explícitamente cuál se usa.**

Un marco más moderno es la **predicción conforme** `norinder2014, norinder2015`, que reformula el dominio de manera estadística en lugar de geométrica: en vez de trazar un límite binario en el espacio de descriptores, emite para cada compuesto una región de predicción calibrada sobre un conjunto separado. Bajo intercambiabilidad, esa región contiene el valor verdadero con al menos la confianza especificada, y **se ensancha automáticamente para compuestos distintos a los del entrenamiento**.

Esto es metodológicamente atractivo para este trabajo precisamente porque los productos naturales se ubicarán en el borde —o fuera— de la distribución de entrenamiento de cualquier conjunto de BBB, y un predictor conforme se degrada de forma controlada en lugar de extrapolar silenciosamente.

### 4.4 El espacio químico de los productos naturales

La comparación cuantitativa más sólida entre fármacos aprobados de origen natural y sintético `stratton2015` reporta:

| Métrica | Productos naturales | Totalmente sintéticos |
|---|---|---|
| Peso molecular medio | 626 | 343 |
| Fracción de carbonos sp³ | 0.68 | 0.37 |
| Anillos aromáticos | 0.8 | 1.9 |
| Lipofilicidad (ALOGPs) | 1.5 | 2.7 |

El número de estereocentros es de 2 a 6 veces mayor en los de origen natural. La fracción sp³ como medida de complejidad se originó al demostrar que tanto ella como la quiralidad **aumentan sistemáticamente conforme los compuestos avanzan de descubrimiento a ensayo clínico a fármaco aprobado** `lovering2009`.

Un hallazgo que matiza el argumento: una vez controlado el peso molecular, **el cumplimiento de la regla de cinco es similar** entre compuestos no-drug-like, drug-like y productos naturales (86.8%, 88.3% y 85.4%). Es decir, **la regla de cinco por sí sola tiene poder discriminante débil**.

> **Dos afirmaciones sin entrada bibliográfica.** La comparación de cumplimiento de la regla de cinco (86.8 / 88.3 / 85.4%) proviene de un estudio de *drug-likeness* de medicina tradicional china (PMC3538521) cuya revista no se pudo confirmar, y la taxonomía por dimensionalidad 0D–4D de un artículo de *Molecular Informatics* cuyo año de publicación quedó en duda. Ambas se omitieron deliberadamente de `bibliografia.bib` en vez de adivinar los campos. **Hay que completarlas o retirar la afirmación antes de entregar.**

Esto refuerza el argumento sobre dominio de aplicabilidad: la divergencia real entre productos naturales y compuestos tipo fármaco no está en el cumplimiento de la regla de cinco, sino en la fracción sp³, los estereocentros y la complejidad de los sistemas de anillos — variables que justifican una evaluación explícita del dominio de aplicabilidad antes de aplicar el modelo `feher2003, rodrigues2016, chen2017`.

### 4.5 Los cinco principios de la OCDE

El documento de la OCDE establece, verbatim, que para considerar un modelo QSAR con fines regulatorios debe asociarse a: **(1) un *endpoint* definido; (2) un algoritmo inequívoco; (3) un dominio de aplicabilidad definido; (4) medidas apropiadas de bondad de ajuste, robustez y capacidad predictiva; (5) una interpretación mecanística, cuando sea posible** `oecd2007`.

Su origen se remonta a los principios de Setúbal, propuestos en 2002 y finalizados en 2004.

**Un matiz importante:** la OCDE es explícita en que estos principios **no constituyen criterios de aceptación regulatoria en sí mismos**, sino un marco conceptual para guiar la validación. Adherirse a él fortalece la credibilidad, transparencia y reproducibilidad, y ofrece una estructura clara para organizar la metodología:

| Principio | Correspondencia en este trabajo |
|---|---|
| Endpoint definido | Definición operacional de permeabilidad BBB y de actividad neuroprotectora |
| Algoritmo inequívoco | Pipeline de ML documentado y versionado |
| Dominio de aplicabilidad | Caracterización del espacio químico, crítica al puntuar productos naturales |
| Bondad de ajuste y predictividad | Validación interna y externa, scaffold split, Y-randomization |
| Interpretación mecanística | Descriptores interpretables consistentes con el mecanismo de permeabilidad |

### 4.6 Metodología de validación

**Scaffold split.** El concepto de andamiaje proviene del análisis de 5,120 fármacos conocidos, cuyos armazones 2D se reducen a solo 1,179 distintos, con los 32 más frecuentes describiendo la mitad de la base `bemis1996properties`. La justificación de dividir por andamiaje es explícita: *"dado que el scaffold splitting intenta separar moléculas estructuralmente diferentes en subconjuntos distintos, ofrece un desafío mayor para los algoritmos de aprendizaje que la división aleatoria"*, y *"imita el desarrollo real en el campo"* `wu2018moleculenet`.

> No se localizó en ese artículo una tabla numérica comparando directamente ambas divisiones sobre datos idénticos, por lo que el argumento debe presentarse como cualitativo.

Un ángulo complementario es la división temporal, que produce estimaciones que son mejor sustituto del desempeño prospectivo real `sheridan2013`. Como contrapunto necesario para no presentar la literatura como monolítica: una división racional puede lucir mejor estadísticamente sin que ello implique ganancia real en capacidad predictiva `martin2012rational`.

**Y-randomization.** Consiste en permutar aleatoriamente los valores de la variable respuesta manteniendo fijos los descriptores, y comparar el ajuste del modelo original contra los reajustados `rucker2007`. La lógica es directa: si permutar las etiquetas y reajustar aún produce buen ajuste, la correlación original probablemente sea artefacto de sobreajuste o azar — riesgo alto en situaciones de muchos descriptores y pocas muestras.

**Validación interna contra externa.** El artículo metodológicamente más influyente del campo muestra que la suposición generalizada de que un q² alto de validación cruzada demuestra capacidad predictiva es *"generalmente incorrecta"*: no encontraron correlación entre q² interno alto y desempeño real sobre un conjunto independiente `golbraikh2002`. Solo los modelos validados externamente, después de la validación interna, pueden considerarse confiables `gramatica2007`.

**Diseño que adopta este trabajo:** la validación cruzada es necesaria pero no suficiente; debe complementarse con un conjunto de prueba genuinamente externo —nunca tocado durante construcción, selección de variables ni ajuste de hiperparámetros— y dividido por andamiaje.

### 4.7 Desbalance de clases

Los conjuntos de bioactividad rara vez están balanceados. La razón por la que la exactitud engaña se ilustra canónicamente: en un ejemplo de mamografía con 98% normal y 2% anormal, un clasificador que siempre predice la clase mayoritaria alcanza **98% de exactitud siendo clínicamente inútil** `chawla2002smote`. El sobremuestreo ingenuo por replicación produce sobreajuste; el submuestreo descarta información real. SMOTE genera puntos sintéticos a lo largo del segmento hacia vecinos minoritarios, generalizando las regiones de decisión en vez de estrecharlas.

**Métricas apropiadas.** El coeficiente de correlación de Matthews es *"la única tasa de clasificación binaria que genera una puntuación alta solo si el predictor fue capaz de predecir correctamente la mayoría de las instancias positivas y la mayoría de las negativas"*, a diferencia de F1, que es independiente de los verdaderos negativos `chicco2020`. Su ejemplo numérico es ilustrativo: exactitud 0.90 y F1 0.95 sugieren excelente desempeño, mientras **MCC = −0.03** revela correctamente que el clasificador es inútil.

Sobre AUROC contra AUPRC: la tasa de falsos positivos se calcula sobre una clase negativa muy grande, de modo que un número absoluto fijo de falsos positivos se traduce en una tasa numéricamente pequeña, **haciendo que las curvas ROC luzcan casi idénticas independientemente del desbalance** `saito2015`. La curva de precisión-*recall* tiene como línea base la prevalencia, ofreciendo una referencia consciente del desbalance. **Para conjuntos BBB+/BBB− desbalanceados, el AUPRC es más diagnóstico que el AUROC.**

---

## 5. Representación molecular

### 5.1 SMILES, SELFIES e InChI

La representación de entrada del proyecto tiene su origen en el trabajo de Weininger `weininger1988`, con su continuación algorítmica que introdujo el algoritmo CANGEN para notación canónica `weininger1989`. Un grafo molecular se serializa mediante una gramática pequeña: un subconjunto orgánico de átomos escribibles sin corchetes, símbolos de enlace, ramificaciones con paréntesis y cierres de anillo con dígitos pareados.

**La SMILES canónica no es única entre herramientas.** No existe una forma estándar de generar una representación canónica: Daylight, OpenEye, ChemAxon y OpenBabel desarrollaron cada uno su propio algoritmo, no publicado y mutuamente incompatible, de modo que **la misma molécula produce cadenas canónicas distintas según el toolkit** `oboyle2012`. Es una consideración práctica para la deduplicación entre bases de datos.

**SELFIES** responde al problema de validez sintáctica: bajo una sola mutación de carácter, una cadena SMILES conserva su validez **solo el 9.9% de las veces**, frente al 100% de SELFIES; con dos mutaciones, 3.0% `krenn2020selfies`. Es relevante en contextos generativos, no en este proyecto, que no genera moléculas.

**InChI e InChIKey** no son descriptores sino **identificadores** `heller2015inchi`: su objetivo de diseño es que la misma etiqueta siempre se refiera a la misma sustancia, pensado para deduplicación y búsqueda. El InChIKey es un hash de 27 caracteres, unidireccional, que requiere una base de consulta para revertirse. Es la llave de unión entre las bases de datos de este proyecto, no una entrada del modelo.

#### Longitud variable: el problema que resuelve la featurización

Una propiedad del SMILES que condiciona toda la arquitectura del modelo es que **su longitud es variable**. Medido sobre los 7,805 compuestos válidos de B3DB (ver [`notebooks/01_EDA.ipynb`](../../notebooks/01_EDA.ipynb)):

| Estadístico | Caracteres |
|---|---|
| Mínimo | 1 (`O`, agua; `C`, metano) |
| Percentil 25 | 36 |
| Mediana | 49 |
| Percentil 75 | 70 |
| Percentil 95 | 117 |
| Máximo | 383 |

La cadena más larga es 383 veces la más corta, y la longitud correlaciona **0.908** con el número de átomos pesados: es esencialmente un proxy del tamaño molecular, sin información química propia.

A esto se suma que la longitud **no es estable ni para una misma molécula**. La cafeína escrita de dos formas válidas distintas produce cadenas de 28 y 26 caracteres, ambas con el mismo InChIKey. Es la consecuencia práctica del problema de canonicalización descrito arriba: la longitud depende de la herramienta y del orden de recorrido del grafo, no solo de la molécula.

**De aquí se sigue el papel de la featurización.** Los modelos de ensamble que adopta este trabajo exigen que todas las observaciones tengan el mismo número de variables. Los descriptores y los fingerprints convierten una entrada de longitud variable en un vector de longitud fija:

| Molécula | SMILES | Átomos pesados | Fingerprint Morgan | Descriptores RDKit |
|---|---|---|---|---|
| Agua | 1 carácter | 1 | 2,048 bits | 217 |
| Cafeína | 28 caracteres | 14 | 2,048 bits | 217 |
| Ciclosporina | 224 caracteres | 85 | 2,048 bits | 217 |

Esta es una razón adicional —independiente de la interpretabilidad y del costo computacional— para no usar un modelo de lenguaje sobre SMILES en este proyecto: exigiría relleno o truncamiento, y los límites de longitud de contexto empezarían a afectar a las moléculas grandes precisamente cuando su tamaño es una característica relevante para la permeabilidad.

**Implicación operativa para la deduplicación:** dado que la cadena no es un identificador estable, la deduplicación entre fuentes debe hacerse por InChIKey recalculado desde la estructura, nunca comparando cadenas SMILES. El EDA del Avance 1 aplica ese criterio.

### 5.2 Taxonomía de descriptores

La referencia canónica `todeschini2000handbook` clasifica los descriptores en familias: **constitucionales** (conteos simples), **topológicos** (derivados del grafo 2D), **geométricos** (requieren coordenadas 3D), **electrónicos** (distribución de carga) y **termodinámicos** `suaygarcia2022`. Una taxonomía complementaria por dimensionalidad va de 0D a 4D, ubicando explícitamente el índice de Wiener y el TPSA como descriptores 2D.

La base grafo-teórica se remonta al **índice de Wiener** `wiener1947`, definido como la suma de las distancias de camino más corto entre todos los pares de vértices del grafo molecular, y al **índice de conectividad de Randić** `randic1975`, que pondera cada enlace según el grado de los átomos que conecta.

Ambos son invariantes de grafo: el de Wiener crece con el tamaño y disminuye con la ramificación, lo que explica su correlación histórica con puntos de ebullición; el de Randić distingue isómeros ramificados de lineales a igual fórmula. **El TPSA es un descendiente conceptual directo**: se calcula de forma aditiva sobre el mismo grafo de conectividad, sin requerir coordenadas 3D, razón por la cual se clasifica como topológico pese a describir formalmente una propiedad de superficie.

### 5.3 Por qué TPSA y logP predicen permeabilidad: la razón física

El TPSA es un método fragmento-aditivo cuyo resultado prácticamente coincide con el área polar 3D real (r = 0.99 sobre 34,810 moléculas), siendo dos o tres órdenes de magnitud más rápido de calcular `ertl2000tpsa`.

El mecanismo físico es la **desolvatación**: *"la interfaz lípido-agua está asociada con una capa de moléculas de agua perturbadas con propiedades de polarización significativamente distintas. Por ello, la capacidad de estas moléculas de agua para formar puentes de hidrógeno con moléculas de fármaco se reduce dramáticamente y forma parte del proceso de desolvatación"* `pajouhesh2005`.

En síntesis: para cruzar una bicapa lipídica, un soluto debe abandonar el agua a granel —donde sus grupos polares están completamente enlazados por puentes de hidrógeno— e ingresar a un interior no polar incapaz de satisfacer esos enlaces. **La penalización de energía libre de ese paso escala con la cantidad de superficie polar que la molécula expone**, que es exactamente lo que el TPSA cuantifica de forma aditiva. El logP es el resumen experimental directo del mismo balance de energía libre.

Los umbrales son más estrictos en la barrera hematoencefálica que en la absorción intestinal (≲90 Å² frente a ≤140 Å² `clark1999`) porque las uniones estrechas abolen la ruta paracelular, dejando la difusión transcelular como mecanismo dominante. Existe además un límite superior de lipofilicidad: un logP excesivo atrapa la molécula en la membrana y favorece la unión inespecífica y el eflujo. La regla de cinco `lipinski2001` aproxima el mismo balance de forma más burda.

### 5.4 Familias de representación y evidencia comparativa

| Familia | Dimensión | Interpretabilidad por substructura |
|---|---|---|
| Descriptores fisicoquímicos 2D (RDKit) | 217 | Por propiedad, no por substructura |
| Mordred | ~1,826 | Mixta |
| Morgan / ECFP | 1024–4096 bits | **Directa**, vía mapeo bit → substructura |
| MACCS keys | 167 bits | **Trivial**: cada bit es un SMARTS nombrado |
| Embeddings preentrenados | ~768 | Débil |
| Redes de grafos | 300 | Fuerte solo con módulos específicos |

**Fingerprints de conectividad extendida.** Una precisión de nomenclatura: **el número del nombre es el diámetro**, de modo que `radius=2` en RDKit corresponde a ECFP4 `rogers2010ecfp`. El identificador nativo es un hash de 32 bits sin límite; plegarlo introduce **colisiones**, con consecuencias para la interpretabilidad tratadas en la sección 7.

**Evidencia comparativa.** Al evaluar 25 modelos preentrenados como embeddings congelados contra ECFP, sobre 25 conjuntos con scaffold split y análisis bayesiano, casi todos los modelos neuronales muestran mejora insignificante o nula `praski2026benchmarking`:

| Representación | AUROC medio | Rango (de 25) |
|---|---|---|
| ECFP | 79.89% | 7.52 |
| ChemBERTa (MTR) | 79.99% | 7.32 |
| MolFormer | 79.80% | 9.50 |
| SELFormer | 73.18% | 20.04 |

**Precisión importante sobre el alcance:** esta conclusión aplica a embeddings **congelados** alimentando un modelo clásico. MolFormer-XL **afinado de extremo a extremo** reporta 93.7 en BBBP contra 71.4 de Random Forest `ross2022molformer`. Este trabajo adopta descriptores y fingerprints por la combinación de evidencia comparable, costo en CPU e interpretabilidad directa.

En estudios específicos de BBB, **los descriptores solos superan a Morgan solo**: AUC 0.866 contra 0.771 sobre BBBP `zhu2025featureguided`, y R² de 0.418 contra 0.312 bajo scaffold split sobre B3DB `tiwari2026conformeros3d`. Combinar nunca resultó perjudicial.

---

## 6. Aprendizaje automático aplicado a permeabilidad BBB

### 6.1 Conjuntos de datos

| Dataset | Tamaño | Balance | Licencia |
|---|---|---|---|
| B3DB | 7,807–7,982 | 63.5% / 36.5% | CC0 |
| BBBP (MoleculeNet) | ~1,955–2,050 | 76% / 24% | No explícita |
| TDC BBB_Martins | 1,975 | No verificado | No especificada |
| LightBBB | 7,162 | 5,453 / 1,709 | No explícita |

B3DB se compiló a partir de 50 recursos publicados `meng2021b3db`. BBBP y TDC BBB_Martins derivan del mismo estudio `martins2012bayesian`, de modo que **no son fuentes independientes**.

### 6.2 Incertidumbre experimental y construcción de etiquetas

La característica que distingue a B3DB es su categorización por confiabilidad: Grupo A (1,058, con logBB numérico), Grupo B (3,621, fuentes que declararon el umbral −1 y coincidieron), Grupo C (3,077, acuerdo sin umbral especificado) y Grupo D (51, etiquetas contradictorias).

Este trabajo entrena sobre A y B, usa C como aumentación y reserva D como conjunto diagnóstico. La justificación es que esa estratificación captura precisamente la inconsistencia entre estudios que la sección 1.5 atribuye a la heterogeneidad de ensayos. El umbral de conversión es **logBB = −1.0**.

### 6.3 Desempeño esperable

| Contexto | Resultado |
|---|---|
| Scaffold split, mejor del leaderboard de TDC | 0.924 ± 0.003 AUROC |
| Rango esperable para un modelo bien construido | **0.85–0.92 AUROC** |
| Split aleatorio / Kennard-Stone | 98.7% exactitud `yuan2018improved` |

La brecha de 7 a 13 puntos entre ambos regímenes es el efecto de la fuga de información entre particiones. Una auditoría de 51 configuraciones de benchmarks encontró que, al endurecer las particiones, **el modelo de primer lugar perdió su posición en 15 de 28 conjuntos** `schuh2026auditing`.

Los baselines publicados para el mismo conjunto BBBP varían entre 0.681 y 0.7194 para Random Forest según la fuente, producto de implementaciones distintas del scaffold split. **Este trabajo no adopta cifras de la literatura como referencia, sino que construye su propio baseline.**

---

## 7. Explicabilidad en modelos moleculares

### 7.1 Justificación

La explicabilidad no es un complemento: los asesores la plantearon como requisito y el objetivo declarado es una interpretación biológica capaz de sostener una publicación. Esto condiciona la elección de representación, que debe permitir atribución a nivel de substructura.

### 7.2 Atribución sobre fingerprints y sus limitaciones

El mapeo de un bit de Morgan a la substructura que lo activó es directo mediante la API de RDKit. Tres limitaciones condicionan el diseño:

**Colisiones de bits.** Substructuras químicamente distintas comparten bit, forzando una atribución única a fragmentos con efectos opuestos. La solución adoptada es **Sort & Slice** `dablander2024sortslice`, que ordena las substructuras por frecuencia y conserva las más frecuentes, libre de colisiones por construcción, con más de un año de validación. Existe una alternativa más reciente `li2026collisionfree` que **se validó solo con splits aleatorios, no scaffold**, según admiten sus autores, y cuyo paquete está en estado alfa con adopción casi nula; se considera piloto comparativo, no base del pipeline.

**Moléculas fantasma.** El muestreo de fondo de SHAP perturba el vector de bits directamente, generando combinaciones que **no corresponden a ninguna molécula ensamblable** `tamura2021mmpkernel`. La atribución puede premiar un fragmento inexistente.

**Brecha semántica.** *"Las características decisivas para las predicciones pueden o no ser responsables de actividades específicas"* `rodriguezperez2020shapley`. Importancia para el modelo no equivale a causalidad biológica `kumar2020problems`.

### 7.3 Métodos complementarios

Siete criterios de evaluación permiten concluir que **SHAP es completo pero débil en accionabilidad y parsimonia, mientras que los contrafactuales son fuertes en ambas y débiles en completitud: son complementarios, no sustitutos** `wellawatte2023perspective, wellawatte2022mmace`.

Sobre redes de grafos, al comparar seis métodos contra substructuras de referencia y siete químicos medicinales, **Integrated Gradients alcanzó AUROC de atribución de 0.675 mientras que los métodos basados en atención quedaron cerca del azar** (0.467 y 0.520) `rao2022patterns`.

De ahí la decisión metodológica central: **emplear al menos dos métodos independientes y reportar como confirmadas únicamente las substructuras en que coinciden**, declarando los desacuerdos. El desacuerdo entre métodos está documentado como la norma.

Una explicación post-hoc es un modelo aproximador distinto del original, sin garantía de reflejar su razonamiento `rudin2019stop`. Por eso se entrena en paralelo un modelo inherentemente interpretable como control.

### 7.4 Del nivel molecular al enunciado agregado

Debe señalarse con franqueza que **no existe un método establecido y citable que realice este procedimiento de extremo a extremo**. Lo propuesto es una síntesis de componentes establecidos: agrupación por andamios `bemis1996properties`, matriz de presencia de fragmentos, prueba exacta de Fisher con corrección de Benjamini-Hochberg, y contraste contra la magnitud media de atribución. El antecedente más cercano son las redes de andamios `varin2011scaffoldnetworks, schuffenhauer2007scaffoldtree`.

La validación propuesta es por **triangulación**: que el enriquecimiento estadístico coincida con quimiotipos privilegiados del SNC ya conocidos `evans1988privileged`.

### 7.5 Riesgos documentados

**Acantilados de actividad.** Todos los métodos fallan desproporcionadamente en pares de estructura casi idéntica y actividad discontinua `vantilborg2022activitycliffs`. Los métodos de atribución suaves producirán explicaciones casi idénticas para estructuras casi idénticas, **justamente donde la relación real es discontinua**. Las explicaciones serán menos confiables en los compuestos limítrofes, que son los de mayor interés.

**Aprendizaje de atajos.** Sobre benchmarks derivados de ChEMBL, un modelo alimentado únicamente con el identificador de la diana y el laboratorio inferido iguala a los baselines estructurales `blevins2025cleverhans`. De ahí la recomendación de particiones disjuntas por fuente, no solo por andamio.

> **Advertencia:** esa última fuente es un preprint sin revisión por pares y debe citarse como tal.

---

## 8. Estado del arte y hueco identificado

No se identificó ningún trabajo publicado que implemente un clasificador de permeabilidad BBB basado en aprendizaje automático alimentando un clasificador de actividad neuroprotectora, específicamente sobre productos naturales y construido a partir de CMAUP, NPASS y ChEMBL.

Los antecedentes más próximos:

**Kato et al. (2025)** es el más cercano en arquitectura: biblioteca de ~1,700 constituyentes, ensayo PAMPA-BBB (611 resultados usables, 255 permeables), y una segunda etapa de neurotoxicidad sobre los 247 más permeables `kato2025bbbnp`. Es experimental, no computacional, y mide neurotoxicidad en lugar de neuroprotección.

**Gürbüz et al. (2025)** aplica la misma secuencia de dos etapas —permeabilidad seguida de inhibición de GSK-3β, CK-1δ y AChE— sobre 23 compuestos fenólicos naturales `gurbuz2025phenolic`. Directamente pertinente, pero de escala reducida y experimental.

**Yasir et al. (2026)** es la plantilla metodológica más próxima: Random Forest sobre 6,880 inhibidores de AChE de ChEMBL, seguido de filtro fisicoquímico de permeabilidad, acoplamiento molecular y validación experimental `yasir2026cnsache`. No trabaja con productos naturales, pero establece el mismo orden de etapas.

> **Advertencia de alcance:** la búsqueda leyó completos los tres trabajos más cercanos, pero no fue exhaustiva. La afirmación de novedad debe enunciarse con esa reserva.

---

## Bibliografía

En [`docs/referencias/bibliografia.bib`](../referencias/bibliografia.bib), con 207 entradas al 2026-09-23. Cada documento de `docs/referencias/` incluye la lista de lo que no se pudo verificar para su ámbito.
