# Modelos finales

Lo que recibe la patrocinadora: **los dos modelos finales ya entrenados** y lo necesario para usarlos con SMILES nuevos. No hay servicio; se usan desde `notebooks/06_Uso_de_los_modelos.ipynb` o con `src/inferencia.py`.

| archivo | qué es | tamaño |
|:--|:--|--:|
| `fase1_svm_rbf.joblib` | `svm_rbf` calibrado (escalado min–max dentro), 151 descriptores → probabilidad de cruzar la barrera | 0.5 MB |
| `fase2_aft.json` | `aft` censurado (XGBoost, pérdida `survival:aft`), 201 descriptores y la diana → pActividad | 0.7 MB |
| `huellas_fase1.npz`, `huellas_fase2.npz` | huellas de Morgan (radio 2, 2,048 bits, empaquetadas) de los compuestos de ajuste, para decir qué tan cerca queda una consulta de lo ya visto | 2 MB |
| `meta.json` | columnas, dianas, parámetros, cifras registradas y 25 predicciones de referencia sobre compuestos de B3DB | 10 KB |

## Con qué se entrenaron

Con las filas de **ajuste** (6,306 compuestos en la fase 1 y 56,241 pares en la fase 2), **sin la prueba reservada**. Es la decisión del 4 de noviembre: en la fase 2 la curva de aprendizaje sigue subiendo (+0.0076 de concordancia), y se renuncia a esa ganancia para poder evaluar y repetir la cifra registrada. Las cifras de desempeño son las de las corridas registradas (decisiones 1.5 y 2.13), no se recalculan aquí.

## Cómo se regeneran

```bash
./env312/bin/python scripts/entrenar_finales.py
```

Deja una corrida en `experimentos/` (parámetros, commit, `sha256` de los datos). `tests/test_inferencia.py` comprueba que los artefactos reproducen las 25 predicciones de `meta.json` sin necesitar los datos, y que los descriptores calculados desde un SMILES coinciden con los de entrenamiento.

## Lo que hay que saber antes de usarlos

- **Una cifra de validación cruzada no describe a la química nueva.** En la prueba reservada la fase 1 baja de MCC 0.70 a 0.34 y la fase 2 de 0.761 a 0.720 de concordancia (0.530 en los pares que solo tiene NPASS, 117 pares).
- **No hay corte.** La probabilidad de la fase 1 se entrega tal cual: a 0.5 el modelo cambia de sesgo cuando el compuesto es distinto de lo entrenado.
- **La fase 2 predice una potencia para cada diana, también las que el compuesto nunca ha tocado.** Es una extrapolación de lo aprendido, no una medición.
- **Versiones.** El `.joblib` depende de la versión de scikit-learn (la de `requirements.lock`); con otra, regenerar.
- **Uso no comercial:** NPASS, una de las fuentes de la fase 2, es CC BY-NC.
