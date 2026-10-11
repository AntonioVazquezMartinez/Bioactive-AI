#!/usr/bin/env python3
"""Cómo cambia el desempeño con el tamaño L del vocabulario de Sort & Slice.

Evidencia de la decisión 1.7 del registro (`docs/decisiones.md`). Sobre la
partición por andamio del Avance 2 (5,557 / 749 / 1,499) compara L entre 64 y
4,096 con validación cruzada de 5 pliegues agrupada por andamio y esqueleto de
conectividad (los acíclicos, solo por esqueleto), repetida con 3 semillas, y tres modelos con hiperparámetros fijos
(regresión logística, Random Forest y XGBoost). El vocabulario se reaprende
dentro de cada pliegue; **la prueba no se toca**.

Salida: `notebooks/datos/resultados_L_sortslice.csv`, que sí se versiona: el
notebook 02 (sección 5.1) lo lee para mostrar la comparación sin volver a correrla.
Requiere las dependencias de `requirements.txt`. Tarda unos 10 minutos.
"""
import sys, warnings, time
from pathlib import Path
warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / 'src'))
from collections import Counter
import numpy as np, pandas as pd
from scipy import sparse
from rdkit.Chem import rdFingerprintGenerator
from features.molecular import a_mol
from data_prep.splits import andamio_murcko, esqueleto_conectividad, scaffold_split
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import matthews_corrcoef, average_precision_score, roc_auc_score
from xgboost import XGBClassifier

b=pd.read_csv(RAIZ / 'data/external/profesora/bbb_permeability_experimental.csv')
b.columns=[c.strip().lstrip("﻿") for c in b.columns]
b=b.rename(columns={"smiles_std":"SMILES","bbb_class":"BBB+/BBB-"})
b['mol']=b['SMILES'].map(a_mol)
d=b.dropna(subset=['mol','BBB+/BBB-']).reset_index(drop=True)
d['y']=(d['BBB+/BBB-']=='BBB+').astype(int)
d['andamio']=[andamio_murcko(m) for m in d['mol']]
d['esqueleto']=[esqueleto_conectividad(m) for m in d['mol']]
d['particion']=scaffold_split(d,fraccion_prueba=0.2,fraccion_validacion=0.1,semilla=42,acíclicos_a='entrenamiento')
print(d.particion.value_counts().to_dict())
gen=rdFingerprintGenerator.GetMorganGenerator(radius=2)
ids=[list(gen.GetSparseCountFingerprint(m).GetNonzeroElements().keys()) for m in d['mol']]

def vocab(idx,L):
    c=Counter()
    for i in idx: c.update(ids[i])
    o=sorted(c.items(),key=lambda kv:(-kv[1],kv[0]))
    return [k for k,_ in o[:L]], len(o)
def mat(idx,voc):
    ind={k:j for j,k in enumerate(voc)}
    rows,cols=[],[]
    for r,i in enumerate(idx):
        for k in ids[i]:
            j=ind.get(k)
            if j is not None: rows.append(r); cols.append(j)
    return sparse.csr_matrix((np.ones(len(rows),dtype=np.uint8),(rows,cols)),shape=(len(idx),len(voc)))
def cobertura(idx,voc):
    s=set(voc); t=v=0
    for i in idx:
        t+=len(ids[i]); v+=sum(1 for k in ids[i] if k in s)
    return v/t
def modelos(seed):
    return {'LogReg':LogisticRegression(C=0.1,max_iter=3000,random_state=seed),
            'RF':RandomForestClassifier(n_estimators=300,n_jobs=-1,random_state=seed),
            'XGB':XGBClassifier(n_estimators=300,max_depth=6,learning_rate=0.1,subsample=0.8,colsample_bytree=0.5,n_jobs=-1,random_state=seed,verbosity=0)}
def metr(y,s):
    p=(s>=0.5).astype(int)
    return matthews_corrcoef(y,p), average_precision_score(1-y,1-s), roc_auc_score(y,s)
tr=np.where(d.particion=='entrenamiento')[0]; va=np.where(d.particion=='validacion')[0]
y=d['y'].values
# grupos de la validación cruzada: el esqueleto de conectividad, unido al andamio
# cuando lo hay. Los acíclicos no tienen andamio: se agrupan solo por esqueleto, de
# modo que los estereoisómeros de un mismo compuesto nunca caigan en pliegues distintos
# (darle a cada acíclico su propio grupo los separaba: 127 filas en 44 esqueletos).
ac=(d['andamio']=='<aciclico>').values
par={}
def f(x):
    while par.setdefault(x,x)!=x:
        par[x]=par[par[x]]; x=par[x]
    return x
for a,e,c in zip(d['andamio'],d['esqueleto'],ac):
    if not c: par[f('A'+a)]=f('E'+e)
g=np.array([f('E'+e) for e in d['esqueleto']])
Ls=[64,128,256,512,1024,2048,4096]
filas=[]
for L in Ls:
    t0=time.time()
    voc,total=vocab(tr,L)
    cov_tr=cobertura(tr,voc); cov_va=cobertura(va,voc)
    # validación cruzada agrupada, vocabulario reajustado por pliegue
    for seed in (0,1,2):
        cv=StratifiedGroupKFold(n_splits=5,shuffle=True,random_state=seed)
        for k,(a,bb) in enumerate(cv.split(tr,y[tr],g[tr])):
            ia,ib=tr[a],tr[bb]
            vf,_=vocab(ia,L); Xa,Xb=mat(ia,vf),mat(ib,vf)
            for nom,m in modelos(seed).items():
                m.fit(Xa,y[ia]); s=m.predict_proba(Xb)[:,1]
                mcc,ap,au=metr(y[ib],s)
                filas.append(dict(L=L,seed=seed,fold=k,modelo=nom,MCC=mcc,AUPRC_neg=ap,AUROC=au,eval='cv'))
    # validación fija
    Xt,Xv=mat(tr,voc),mat(va,voc)
    for nom,m in modelos(0).items():
        m.fit(Xt,y[tr]); s=m.predict_proba(Xv)[:,1]
        mcc,ap,au=metr(y[va],s)
        filas.append(dict(L=L,seed=0,fold=-1,modelo=nom,MCC=mcc,AUPRC_neg=ap,AUROC=au,eval='val'))
    filas.append(dict(L=L,seed=0,fold=-1,modelo='cobertura',eval='cov',
                      cob_entrenamiento=cov_tr,cob_validacion=cov_va,vocabulario_total=total))
    print(f'L={L} listo en {time.time()-t0:.0f}s; vocabulario total en train={total}',flush=True)
salida = RAIZ / 'notebooks/datos/resultados_L_sortslice.csv'
salida.parent.mkdir(parents=True, exist_ok=True)
pd.DataFrame(filas).to_csv(salida, index=False)
print('escrito', salida)
