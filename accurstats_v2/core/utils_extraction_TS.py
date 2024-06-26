import sys
sys.path.append('../')
sys.path.append('../../')
sys.path.append('../../../')

import pandas as pd
from pandas import DataFrame
import numpy as np
from core import Test_stats
from core import utils_Traitement
from core.Moving_average_Container import Moving_average
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import statsmodels.api as sm


"""
L'objectif est de pouvoir estimer la tendance et la saisonnalité d'une serie temporelle , par des procédures classiques:

        - Estimation par moindres carrés
        - Procédure X11
"""
# Renvoie la série décalée
def lag(serie: pd.DataFrame, l: int) -> pd.DataFrame:           # Elle prend en entrée une serie , c-à-d une colonne pandas
    return serie.shift(l)


# Application d'une série temporelle

def apply(MA, serie: pd.DataFrame) -> pd.DataFrame:
    temps = serie.iloc[:,0]     #pd.Series                                                        # Elle prend en entrée une serie , c-à-d une colonne pandas
    sr = serie.iloc[:, 1]       #pd.Series
    p1 = MA.ordre_inf
    p2 = MA.ordre_sup
    resultat = lag(sr,-p1) * MA.coeff[0]
    for i in range(-p1 + 1, p2 + 1):
        a = MA.coeff[i + p1]
        sr_i = lag(sr, i)
        sr_i = a * sr_i
        resultat += sr_i
    final = pd.DataFrame({'Date' : temps, 'Cible':resultat})
    return final



# Tendance polynomiale
def extract_trend_OLS(serie: DataFrame, degre: int) -> DataFrame:
    #if serie.isna().any().any():
     #   raise TypeError("Veuillez interpoler la série svp")
    # Let's goooooo
    date_min = serie.iloc[:, 0].min()
    t = (serie.iloc[:, 0] - date_min).dt.days
    initial_coeff = np.zeros(degre + 1)
    result = minimize(Test_stats.mse_loss_trend, initial_coeff, args=(serie, t))

    temps = serie.iloc[:, 0]
    values = pd.Series(np.polyval(result.x, t))
    return (values, result.x)





# La saisonnailté à partir de la librairie statsmodels
def saisonnalite(serie: DataFrame, period) -> DataFrame :        # Elle renvoie la saisonnalité de la série
    temps = serie.iloc[:,0]
    decomposition = sm.tsa.seasonal_decompose(serie.iloc[:, 1],model='additive', period= period)  # Ajustez 'period' selon la fréquence de votre saisonnalité
    saiso = decomposition.seasonal
    return saiso


# La tendance à partir de la librairie statsmodels
def tendance(serie: DataFrame,period) -> DataFrame:
    temps = serie.iloc[:, 0]
    decomposition = sm.tsa.seasonal_decompose(serie.iloc[:, 1], model='additive',period=period)  # Ajustez 'period' selon la fréquence de votre saisonnalité
    saiso = decomposition.trend
    return saiso



# Les résidus à partir de la librairie statsmodels
def residus(serie: DataFrame, period) -> DataFrame:
    temps = serie.iloc[:, 0]
    decomposition = sm.tsa.seasonal_decompose(serie.iloc[:, 1],model='additive',period=period)  # Ajustez 'period' selon la fréquence de votre saisonnalité
    saiso = decomposition.resid
    return saiso



# Elle enlève simplement la tendance
def remove_trend(serie: DataFrame , tendance: DataFrame) ->list:
    temps = serie.iloc[:, 0]
    resultat = serie.iloc[:, 1] - tendance.iloc[:,1]
    return pd.DataFrame({'Date' : temps, 'Cible':resultat})






# Trend par la procédure X11
def procedure_X11(serie: DataFrame) -> DataFrame:           # Il faut avant modifier l'implémentation de la classe Moving Average
    # Estimation par M2_12
    M12 = Moving_average(6 , 5 , [1/12 for i in range(12)])
    M2 = Moving_average(1 , 0  , [1/2,1/2])
    m1 = apply(M2 , apply(M12 , serie))
    s1 =  pd.DataFrame({'Date': serie.iloc[:,0], 'Cible': serie.iloc[:,1] - m1.iloc[:,1]})

    # Estimation par M3,3
    M3 = Moving_average(1,1,[1/3,1/3,1/3])
    M33_s1 = apply(M3 , apply(M3 , s1))
    intermed = M33_s1.iloc[:,1] - apply(M2 , apply(M12 , M33_s1)).iloc[:,1]
    s2 = pd.DataFrame({'Date': serie.iloc[:,0], 'Cible': intermed})

    serie1 = pd.DataFrame({'Date': serie.iloc[:,0], 'Cible': serie.iloc[:,1] - s2.iloc[:,1]})

    # Estimation par moyenne mobile d'henderson M13
    M_Henderson_13 = Moving_average(6,6,[0.028 , -0.006 , 0.092 , 0.14 , 0.161 , 0.147 , 0.166 , 0.147 , 0.161 , 0.14 , 0.092 , -0.006 , 0.028])
    m2 = apply(M_Henderson_13 , serie1)
    s3 = pd.DataFrame({'Date': serie.iloc[:, 0], 'Cible': serie.iloc[:, 1] - m2.iloc[:, 1]})

    # Estimation par M3x5
    M5 = Moving_average(2,2,[1/5 for i in range(5)])
    s3_intermed = apply(M5 , apply(M3 , m2))                                                                                            # ICI c'est pas complet

    final_trend = pd.DataFrame({'Date': serie.iloc[:, 0], 'Cible': m2.iloc[:, 1]})

    final_seasonal = pd.DataFrame({'Date': serie.iloc[:, 0], 'Cible': s3.iloc[:, 1]})

    final_irregular = pd.DataFrame(
        {'Date': serie.iloc[:, 0], 'Cible': serie.iloc[:, 1] - final_trend.iloc[:, 1] - final_seasonal.iloc[:, 1]})

    return final_trend
