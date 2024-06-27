import yfinance as yf
import pandas as pd
from pandas import DataFrame
from datetime import datetime

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------ Format de la date---------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


def date_valide(date_str):
    try:
        datetime.strptime(date_str, '%d-%m-%Y')
        return True
    except ValueError:
        return False


#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------- extraction des données---------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



def extract_daily(Tickers: list[str], date_debut: str, date_fin: str, interval: str) -> pd.DataFrame:
    if not date_valide(date_debut) or not date_valide(date_fin):
        raise Exception("Mauvais format pour les dates")
    else:
        date_debut_obj = datetime.strptime(date_debut, '%d-%m-%Y')
        date_fin_obj = datetime.strptime(date_fin, '%d-%m-%Y')
        data = yf.download(Tickers, start=date_debut_obj, end=date_fin_obj, interval=interval)
        return data


def extract_intraday(Tickers: list[str], date_debut: str, date_fin: str, interval: str) -> pd.DataFrame:
    if not date_valide(date_debut) or not date_valide(date_fin):
        raise Exception("Mauvais format pour les dates")

    else:
        date_debut_obj = datetime.strptime(date_debut, '%d-%m-%Y')
        date_fin_obj = datetime.strptime(date_fin, '%d-%m-%Y')
        if (date_fin_obj - date_debut_obj).days >= 730:
            raise Exception("Veuillez choisir une période moins des 730 derniers jours")
        else:
            data = yf.download(Tickers, start=date_debut_obj, end=date_fin_obj, interval=interval)
            return data
