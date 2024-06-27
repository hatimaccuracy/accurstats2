import pandas as pd
from pandas import DataFrame
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from core import utils_Traitement
from itertools import combinations
import statsmodels.api as sm




# Fonction de regression entre deux variables explicatives
def Model_reg(cible: pd.DataFrame,
              expli1: pd.DataFrame,
              expli2: pd.DataFrame,
              rho: float):

    # Préparation de la donnée
    donnees_traites = utils_Traitement.intersection_date(cible, expli1, expli2)
    cible, expli1, expli2 = donnees_traites[0], donnees_traites[1], donnees_traites[2]

    # Gestion des dates
    dates = cible.iloc[:, 0]
    #X = pd.DataFrame({'explicative1': expli1.iloc[:, 1].values, 'explicative2': expli2.iloc[:, 1].values}, index=dates)
    X = pd.DataFrame({'explicative1': expli1.iloc[:, 1].values, 'explicative2': expli2.iloc[:, 1].values})
    y = cible.iloc[:, 1].values

    # Séparation des données
    X_train, X_test, y_train, y_test, dates_train, dates_test = train_test_split(
        X, y, dates, test_size=rho, random_state=42, shuffle=False)
    # Modèle
    model = LinearRegression()
    model.fit(X_train, y_train)                                                                                         # Le problème c'est que les valeurs de X sont des strings
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)

    # Metriques de la regression
    mse_train = mean_squared_error(y_train, y_pred_train)
    mse_test = mean_squared_error(y_test, y_pred_test)
    r2_train = r2_score(y_train, y_pred_train)
    r2_test = r2_score(y_test, y_pred_test)

    # Coefficients du modèle
    coeffs = model.coef_
    interc = model.intercept_

    # Retour au pd.DataFrame avec les dates
    y_pred_test = pd.DataFrame({'Date': dates_test, 'y_test': y_pred_test})
    y_pred_train = pd.DataFrame({'Date': dates_train, 'y_test': y_pred_train})

    return (y_pred_test, y_pred_train , r2_train , r2_test , mse_train , mse_test , coeffs , interc)



# Fonction résumant le modèle:
def toString_Model_Reg(cible: pd.DataFrame,
                   expli1: pd.DataFrame,
                   expli2: pd.DataFrame,
                   rho: float,
                   r2_train ,
                   r2_test ,
                   mse_train ,
                   mse_test ,
                   coeffs ,
                   interc
                   ):


    return (f'\n'
            f'Le modèle étudié explique {cible.columns[1]} en fonction de {expli1.columns[1]} et de {expli2.columns[1]} \n'
            f'\n'
            f'Le coefficient attribué à {expli1.columns[1]} est de {coeffs[0]} , et celui attribué à {expli2.columns[1]} est de {coeffs[1]}. En plus , l\'intercept proposée est de {interc}\n'
            f'\n'
            f'Ce modèle a un R2 in sample de {r2_train} (avec une erreur : mse = {mse_train}) et un R2 out of sample de {r2_test} (avec une erreur : mse = {mse_test})\n'
            f'\n'
            f''
            f'Le back test est effectué sur une proportion {rho*100}% des données')



# Fonction de screening par brute force
def Model_screening(explicatives: DataFrame , cible: DataFrame ,rho: float , Model, progress_bar) -> DataFrame:           # hatim stv ajoutes la progress bar
    # On élimine la colonne des dates                                                                       ###################################
    dates = explicatives.iloc[:,0]
    explicatives.pop('Date')

    # Le dictionnaire des metriques et des variables explicatives
    dico_screen = {'Predictor 1':[] , 'Predictor 2':[] , 'intercept':[] , 'coefficient 1':[] , 'coefficient 2':[] ,'MSE-in-sample':[] , 'MSE-out-of-sample':[] , 'R2-in-sample':[] , 'R2-out-of-sample':[]}

    # On cherche toutes les combinaisons possibles
    colonnes = explicatives.columns
    combinaisons = list(combinations(colonnes, 2))

    # Boucler sur chaque combinaison
    count =0
    co= len(combinaisons)
    for col1, col2 in combinaisons:
        dico_screen['Predictor 1'].append(col1)
        dico_screen['Predictor 2'].append(col2)
        count =count +1
        progress_bar.progress(int(count/co*100))
        expli1 = pd.DataFrame({'Date' : dates , col1 : explicatives[col1]})
        expli2 = pd.DataFrame({'Date' : dates , col2 : explicatives[col2]})

        # On effectue la regression
        cible_pred_test, cible_pred_train, r2_train, r2_test, mse_train, mse_test, coeffs, interc = Model(cible, expli1, expli2, rho)

        # On ajoute le résultat au dictionnaire
        dico_screen['intercept'].append(interc)
        dico_screen['coefficient 1'].append(coeffs[0])
        dico_screen['coefficient 2'].append(coeffs[1])
        dico_screen['MSE-in-sample'].append(mse_train)
        dico_screen['MSE-out-of-sample'].append(mse_test)
        dico_screen['R2-in-sample'].append(r2_train)
        dico_screen['R2-out-of-sample'].append(r2_test)

    # Vers le DataFrame pandas
    data_screening = pd.DataFrame(dico_screen)

    return data_screening



# Fonction qui l'AR-X
# results.summary() : pour fournir un résumé du modèle
# results.params : pour renvoyer les coefficients estimés du modèle
# results.pvalues : les p-valeurs des coefficients
# results.fittedvalues : Renvoie les valeurs ajustées (prédites) par le modèle pour les données d'entraînement
# results.resid : Renvoie les résidus (différences entre les valeurs observées et ajustées)

def Model_ARX(cible: pd.DataFrame, expli1: pd.DataFrame, expli2: pd.DataFrame, ordre: int):
    # Préparation de la donnée
    donnees_traites = utils_Traitement.intersection_date(cible, expli1, expli2)
    cible, expli1, expli2 = donnees_traites[0], donnees_traites[1], donnees_traites[2]

    # Gestion des dates et dataframe
    dates = cible.iloc[:, 0]
    df = pd.DataFrame({
        cible.columns[1]: cible.iloc[:, 1],
        expli1.columns[1]: expli1.iloc[:, 1],
        expli2.columns[1]: expli2.iloc[:, 1]
    })


    extract = [expli1.columns[1], expli2.columns[1]]
    for i in range(1, ordre + 1):
        df[f'{cible.columns[1]}_lag{i}'] = df[cible.columns[1]].shift(i)
        extract.append(f'{cible.columns[1]}_lag{i}')

    df = df.iloc[ordre:]
    endog = df[cible.columns[1]]
    exog = sm.add_constant(df[extract])
    # Ajustement du modèle AR-X
    model = sm.OLS(endog, exog)
    results = model.fit()

    return results, dates.iloc[ordre:], endog


def Model_ARX_rho(cible: pd.DataFrame, expli1: pd.DataFrame, expli2: pd.DataFrame, ordre: int, rho: float):


    # Préparation de la donnée
    donnees_traites = utils_Traitement.intersection_date(cible, expli1, expli2)
    cible, expli1, expli2 = donnees_traites[0], donnees_traites[1], donnees_traites[2]

    # Gestion des dates et dataframe
    dates = cible.iloc[:, 0]
    df = pd.DataFrame({
        cible.columns[1]: cible.iloc[:, 1],
        expli1.columns[1]: expli1.iloc[:, 1],
        expli2.columns[1]: expli2.iloc[:, 1]
    })

    extract = [expli1.columns[1], expli2.columns[1]]
    for i in range(1, ordre + 1):
        df[f'{cible.columns[1]}_lag{i}'] = df[cible.columns[1]].shift(i)
        extract.append(f'{cible.columns[1]}_lag{i}')

    df = df.iloc[ordre:]
    endog = df[cible.columns[1]]
    exog = sm.add_constant(df[extract])

    # Diviser les données en ensembles d'entraînement et de test
    train_size = int(len(df) * (1 - rho))
    endog_train, endog_test = endog[:train_size], endog[train_size:]
    exog_train, exog_test = exog[:train_size], exog[train_size:]
    dates_train, dates_test = dates.iloc[ordre:train_size + ordre], dates.iloc[train_size + ordre:]

    # Ajustement du modèle AR-X sur les données d'entraînement
    model = sm.OLS(endog_train, exog_train)
    results = model.fit()

    return results, dates_train, endog_train, exog_test, dates_test, endog_test, exog_train















"""
# Exemple de test

input = "../data-test/Clean_data.csv"

explicatives = pd.read_csv(input , delimiter=";")
explicatives.iloc[:, 0] = pd.to_datetime(explicatives.iloc[:, 0], format='%d/%m/%Y', errors='coerce')
explicatives.iloc[:, 1:] = explicatives.iloc[:, 1:].replace(',', '.', regex=True).astype(float)                                                 # La data de hatim est de la merde , il faut à chaque fois transformer de str à float


#ex1 = utils_Traitement.extract_column(explicatives , 6)
#ex2 = utils_Traitement.extract_column(explicatives , 7)

input2 = "../data-test/Series-Factoring-test.xlsx"

frame = pd.read_excel(input2)
cible = utils_Traitement.extract_column(frame , 1)
ex1 =utils_Traitement.extract_column(frame , 4)
ex2 = utils_Traitement.extract_column(frame , 13)

resultat = Model_ARX(cible , ex1 , ex2, 2)

print(resultat.summary())
"""






