import pandas as pd
from pandas import DataFrame
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline




"""

Ce  fichier est résponsable du traitement des séries temporelles en entrée, avant toute autre manipulation.

Principalement , il fera les taches suivantes : - Transformer le fichier en entrée (peu importe son format) en un DataFrame pandas
                                                - Gérer les valeurs manquantes des séries
                                                
"""

input = "Series-Factoring-test.xlsx"
#input = "test_interpolation.xlsx"



# Fonction qui transforme un fichier excel en un pandas
def from_excel(input: str) -> DataFrame:
    file_path = os.path.join(os.path.dirname(__file__), input)
    return pd.read_excel(file_path)


# Fonciton qui élimine les lignes où il manque la date
def no_date(data: DataFrame) -> DataFrame:
    indices_to_drop = []
    for i in range(len(data)):
        if pd.isna(data.iloc[i, 0]):
            indices_to_drop.append(i)
    data = data.drop(index=indices_to_drop).reset_index(drop=True)
    return data


def concatenate(data1: DataFrame , data2: DataFrame) -> DataFrame:
    return pd.concat([data1, data2], ignore_index=True)


def intersection_date(serie1: DataFrame , serie2: DataFrame , serie3: DataFrame) -> DataFrame:
    serie1.iloc[:, 0] = pd.to_datetime(serie1.iloc[:, 0])
    serie2.iloc[:, 0] = pd.to_datetime(serie2.iloc[:, 0])
    serie3.iloc[:, 0] = pd.to_datetime(serie3.iloc[:, 0])

    # l'intersection des dates
    common_dates = set(serie1.iloc[:, 0]).intersection(serie2.iloc[:, 0]).intersection(serie3.iloc[:, 0])

    # Filtrage des DataFrames pour ne garder que les dates communes
    serie1_filtered = serie1[serie1.iloc[:, 0].isin(common_dates)].reset_index(drop=True)
    serie2_filtered = serie2[serie2.iloc[:, 0].isin(common_dates)].reset_index(drop=True)
    serie3_filtered = serie3[serie3.iloc[:, 0].isin(common_dates)].reset_index(drop=True)

    return [serie1_filtered, serie2_filtered, serie3_filtered]


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------- Y a-t-il des données manquantes?----------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


def existe_trous(data: DataFrame) -> bool:
    n = len(data.columns)          # Nombre de colonnes
    for i in range(n):
        for j in range(len(data.iloc[:,i])):
            if pd.isna(data.iloc[j,i]):
                return True
    return False


def colonne_trouee(data: DataFrame) -> list:
    n = len(data.columns)  # Nombre de colonnes
    trous = []
    for i in range(n):
        for j in range(len(data.iloc[:, i])):
            if pd.isna(data.iloc[j, i]):
                trous.append(i)
                break
    return trous

def colonnes(data: DataFrame) -> list:
    return data.columns


#def remove_first_nan(data:DataFrame , i:int) ->DataFrame:                   # Elle ne prend en argument qu'une série , c-à-d une colonne pandas


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------- Interpolation des valeurs manquantes dans un DataFrame-----------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Fonction qui fait l'interpolation linéaire
def linear_interpol(data: DataFrame, i: int) -> DataFrame:
    df = data.copy()
    n = len(df.iloc[:, i])
    c = 0

    # Trouver le premier index non-NaN
    if pd.isna(df.iloc[c, i]):
        while pd.isna(df.iloc[c, i]) and c < n-1:
            c += 1

    # Trouver le dernier index non-NaN
    d = n - 1
    if pd.isna(df.iloc[d, i]):
        while pd.isna(df.iloc[d, i]) and d > 0:
            d -= 1

    print(f"les {c} premières valeurs n'ont pas été interpolées")
    print(f"les {n-1-d} dernières valeurs n'ont pas été interpolées")

    haut, bas = c+1, c
    while haut < d + 1:
        if not pd.isna(df.iloc[haut, i]) and haut - bas + 1 >= 1:
            start = df.iloc[bas, i]
            end = df.iloc[haut, i]
            print(haut , bas)
            interp = np.linspace(start, end, haut - bas + 1)
            df.iloc[bas:haut + 1, i] = interp
            bas = haut
        haut += 1

    return df




# Fonction qui fait l'interpolation par la valeur suivante dans les valeurs d'une colonne i
def next_interpol(data: DataFrame , i:int) -> DataFrame:
    df = data.copy()
    n = len(df.iloc[:,i])
    haut , bas = 0 , 0
    while haut < n:
        if not pd.isna(df.iloc[haut, i]):
            while bas < haut:
                df.iloc[bas, i] = df.iloc[haut, i]
                bas += 1
            bas = haut + 1
        haut += 1
    if bas < n:
        print(f"les {n - bas} dernières valeurs n'ont pas pu être interpolées")
    return df


# Fonction qui fait l'interpolation par la valeur précedente
def previous_interpol(data: DataFrame , i:int) -> DataFrame:
    df = data.copy()
    n = len(df.iloc[:,i])
    c = 0
    if pd.isna(df.iloc[c,i]) :
        while pd.isna(df.iloc[c,i]):
            c+=1
    print("les " + str(c) + " premières valeurs n'ont pas été interpolées" )
    for k in range(c , n):
        if pd.isna(df.iloc[k,i]):
            df.iloc[k, i] = df.iloc[k-1,i]
    return df



# Fonction qui fait l'interpolation polynomiale
def spline_interpol(data: pd.DataFrame, i: int) -> pd.DataFrame:
    df = data.copy()
    n = len(df.iloc[:, i])

    # Convertir les générateurs en listes
    x = np.array([k for k in range(n) if not pd.isna(df.iloc[k, i])])
    y = np.array([df.iloc[k, i] for k in range(n) if not pd.isna(df.iloc[k, i])])

    cs = CubicSpline(x, y)

    # Interpoler les valeurs manquantes uniquement
    for k in range(n):
        if pd.isna(df.iloc[k,i]):
            df.iloc[k,i] = cs(k)

    return df


# Fonction qui fait l'interpolation par Filtre de Kalman
def kalman_interpol(data: pd.DataFrame, i: int) -> pd.DataFrame:
    df = data.copy()
    A = np.array([[1]])
    H = np.array([[1]])
    Q = np.array([[0.0001]])
    R = np.array([[0.01]])
    x_hat = np.array([df.iloc[0, i] if not pd.isna(df.iloc[0, i]) else 0])
    P = np.array([[1]])
    esti_data = []
    for k in range(len(df.iloc[:, i])):
        if not pd.isna(df.iloc[k, i]):
            K = P @ H.T @ np.linalg.inv(H @ P @ H.T + R)
            x_hat = x_hat + K @ (df.iloc[k, i] - H @ x_hat)
            P = (np.eye(1) - K @ H) @ P
            esti_data.append(df.iloc[k, i])
        else:
            esti_data.append((H @ x_hat)[0])
        x_hat = A @ x_hat
        P = A @ P @ A.T + Q
    df.iloc[:, i] = pd.Series(esti_data).astype(float)
    return df


# Fonction qui fait l'interpolation par la valeur moyenne
def mean_interpol(data: DataFrame, i:int) -> DataFrame:
    df = data.copy()
    n = len(df.iloc[:,i])
    obs = np.array([df.iloc[k,i] for k in range(n) if not pd.isna(df.iloc[k,i])])
    mean = np.mean(obs)
    for k in range(n):
        if pd.isna(df.iloc[k,i]) :
            df.iloc[k, i] = mean
    return df


# Fonction qui fait l'interpolation par la mediane
def median_interpol(data: DataFrame, i:int) -> DataFrame:
    df = data.copy()
    n = len(df.iloc[:, i])
    obs = np.array([df.iloc[k, i] for k in range(n) if not pd.isna(df.iloc[k, i])])
    median = np.median(obs)
    for k in range(n):
        if pd.isna(df.iloc[k, i]):
            df.iloc[k, i] = median
    return df


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------ Extraction de données-----------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def extract_column(data:DataFrame , i:int) -> DataFrame:
    return data.iloc[:, [0, i]]

