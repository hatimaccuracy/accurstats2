import pandas
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
def transform(transformation, serie):
    if transformation == "Growth_rate":
        return serie.pct_change()
    if transformation == "Level":
        return serie
    if transformation == "Difference":
        return serie.diff()


supported_extensions = ['.csv', '.xls', '.xlsx']
in_folder = Path("input_graphs")

#### Execution sur tout les fichiers dans le répértoire input_graphs
for m in in_folder.iterdir():
    if "screening" in  m.name:
        file = m
    if 'n_target'in m.name:
        file_ = m
    elif 'target' in m.name:
        file__ = m
    elif 'n_oo' in m.name:
        oo_ = m
    elif 'oo' in m.name:
        oo = m

data = pd.read_csv(file, delimiter=";", decimal = ",")
orig = pd.read_csv(file_, delimiter=";", decimal = ",")
oo_orig = pd.read_csv(oo_, delimiter=";", decimal = ",")
target = pd.read_csv(file__, delimiter=";", decimal = ",")
oo_target = pd.read_csv(oo, delimiter=";", decimal = ",")
#### Tri suivant R2
data.sort_values(by ='R2',inplace=True,ascending=False)

#### Détérmination des distributions des R2oos
oos = []
for i in range(len(data)):
    act = data.iloc[i]
    ##### Extraction des caracteristiques du modèles
    var1 = act['Predictor_1'].split('.')[0]
    lag1=  act['Predictor_1'].split('.')[-1]
    try:
        var2 = act['Predictor_2'].split('.')[0]
        lag2 = act['Predictor_2'].split('.')[-1]
        coeff2 = float(act['Coeff_2'])
        transformation2 = act['Transfo_2'].split('.')[-1]
    except:
        var2 = 'Date'
        lag2 =''
        coeff2 = 0
        transformation2 = 'Level'
    transformation1 = act['Transfo_1'].split('.')[-1]

    coeff1 = float(act['Coeff_1'])
    R2 = float(act['R2'])

    #### Transformation des variables
    if 'lag' in lag1:
         lagr1 = int(lag1.split('_')[-1])
         transformed_1 = transform(transformation1, orig[var1]).shift(lagr1).fillna(0)
         transformed_1_oo = transform(transformation1, oo_orig[var1]).shift(lagr1).fillna(0)
    else:
         lagr1 = 0
         transformed_1 = transform(transformation1, orig[var1])
         transformed_1_oo = transform(transformation1, oo_orig[var1])

    if 'lag' in lag2:
         lagr2 = int(lag2.split('_')[-1])
         transformed_2 = transform(transformation2, orig[var2]).shift(lagr2).fillna(0)
         transformed_2_oo = transform(transformation1, oo_orig[var2]).shift(lagr2).fillna(0)
    else:
         lagr2 = 0
         transformed_2 = transform(transformation2, orig[var2])
         transformed_2_oo = transform(transformation2, oo_orig[var2])
    ver_lag=max(lagr1,lagr2)

    ## pred in sample
    try:
        pred = coeff1 * transformed_1 + coeff2*transformed_2
    except:
        pred = coeff1 * transformed_1
    pred.index = target['Date']
    actual = target[target.columns[1]]
    actual.index = target['Date']


    ###Determination de l'intercept
    beta = (actual - pred)[ver_lag:].mean()
    pred = pred + beta

    ## pred out of sample
    try:
        pred_oo = coeff1 * transformed_1_oo + coeff2 * transformed_2_oo + beta
    except:
        pred_oo = coeff1 *transformed_1_oo  + beta
    actual_oo = oo_target[target.columns[1]]
    pred_oo.index = oo_target['Date']
    actual_oo.index =oo_target['Date']


    ## rso
    tss = ((actual_oo[ver_lag:]-actual_oo[ver_lag:].mean())**2).sum()
    rsso = ((actual_oo[ver_lag:] - pred_oo[ver_lag:])**2).sum()
    r2oos = 1 - rsso/tss
    oos.append(r2oos)
data['R2OOS'] = pd.DataFrame({'R2OOS':oos})
data.sort_values(by='R2OOS', inplace=True, ascending=False)

data.to_csv('input_graphs/new_screening.csv', index=False, sep=';', decimal=',')

print("Done, executez script_graphs_metrics.py")