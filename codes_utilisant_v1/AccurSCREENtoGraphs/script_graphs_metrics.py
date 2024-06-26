import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
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
    if "new" in m.name:
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

preds = pd.DataFrame()
preds.index = pd.to_datetime(pd.concat([target['Date'], oo_target['Date']]))

#### Numéro de modèle à evaluer et tracer par utilisateur
flag_n = False
while not flag_n:
    try:
        n = int(input("Entrer le numéro de modeles à analyser (par ordre de R^2 décroissant, entre nombre inferieur à "+str(len(data))+"):"))
        flag_n = True
    except:
        print("Mauvaise entrée, ressayer.")
s = input("Voulez vous des graphes (Y/N)?")
graph = (s=='Y')
###### Tracé des modeles
for i in range(n):
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
    r2oos = float(act['R2OOS'])
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
    pred.index = pd.to_datetime(target['Date'])
    actual = target[target.columns[1]]
    actual.index =pd.to_datetime(target['Date'])


    ###Determination de l'intercept
    beta = round((actual - pred)[ver_lag:].mean())
    pred = pred + beta

    ## pred out of sample
    try:
        pred_oo = coeff1 * transformed_1_oo + coeff2 * transformed_2_oo + beta
    except:
        pred_oo = coeff1 *transformed_1_oo  + beta
    actual_oo = oo_target[target.columns[1]]
    pred_oo.index = pd.to_datetime(oo_target['Date'])
    actual_oo.index = pd.to_datetime(oo_target['Date'])
    ##modier 20 !!!!!!!!!!!!!!
    preds['pred_' + str(20 + i)] = pd.concat([pred[ver_lag:],pred_oo[ver_lag:]])
    ## figures
    if graph:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10,16))
        actual[ver_lag:].plot(label=target.columns[1], ax=ax1)
        pred[ver_lag:].plot(label='Prediction', ax=ax1)
        actual_oo[ver_lag:].plot(label=target.columns[1], ax=ax1)
        pred_oo[ver_lag:].plot(label='Prediction', ax=ax1)
        ax1.set_title('Comparison of Two Series')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Valeur')
        text= 'Variables explicatives: \n -' + str(act['Predictor_1'])  + " de coeff: "+ str(coeff1) +"\n-"+ str(act['Predictor_2'])  + " de coeff: "+ str(coeff2) + '\n- BETA (intercept):' + str(beta) +'\n\n équation:\n' +target.columns[1] +"= "+ str(beta) +" + ("+ str(coeff1) + ")*" + str(act['Predictor_1']) +"+(" + str(coeff2) + ")*" + str(act['Predictor_2']) + '\n \n Métriques: R^2='+ str(R2) + " R2oos =" +str(r2oos)

        ax2.text(0.5, 0.5, text, fontsize=12, ha='center', va='center')

        ax1.legend()
        ax2.axis('off')


        plt.show()
preds["target"] = pd.concat([target[target.columns[1]],oo_target[target.columns[1]]])
preds.to_csv('preds.csv', index=True, sep=';', decimal=',')
