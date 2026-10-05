# Biología de la barrera y de la enfermedad

Qué es la barrera hematoencefálica, qué enfermedades se quieren atacar y por qué los productos naturales son el punto de partida. Es la parte que no supone conocimiento de modelado.

> **Estado: borrador para revisión del equipo y los asesores.** Se construyó a partir de siete ramas de investigación documentadas en [`docs/referencias/`](../../referencias/README.md), que conservan la evidencia completa y las advertencias de acceso. La bibliografía está en [`bibliografia.bib`](../../referencias/bibliografia.bib), con 208 entradas.
>
> **Antes de entregar:** verificar contra doi.org toda referencia marcada como de acceso parcial o sin acceso. Varias entradas tienen metadatos que nadie del equipo ha leído.

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
