import requests
import pandas as pd
from config import BDF_API_KEY
pd.set_option('display.width', None)
headers = {"accept": "application/json"}

# URL for the API endpoint

def return_types():
    types_url = f"https://api.webstat.banque-france.fr/webstat-fr/v1/catalogue?client_id={BDF_API_KEY}&format=json"
    response_types = requests.get(types_url, headers=headers)

    # Check if the request was successful
    if response_types.status_code == 200:
        # Parse the JSON response
        data = response_types.json()

        # Convert the JSON data to a pandas DataFrame
        df_types = pd.json_normalize(data)

        # Print the DataFrame
        L = [str(df_types['name'][i]) + " @ " + str(df_types['description'][i]) for i in range(len(df_types))]
        return L
    else:
        print(f"Failed to retrieve data: {response_types.status_code}")

def return_series(type):
    url = f"https://api.webstat.banque-france.fr/webstat-fr/v1/catalogue/{type}?client_id={BDF_API_KEY}&format=json"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()

        # Convert the JSON data to a pandas DataFrame
        df = pd.json_normalize(data)
        L = [ str(df['seriesKey'][i]) + " @ " + str(df['titleCompl'][i]) for i in range(len(df))]
        return L
    else:
        print(f"Failed to retrieve data: {response.status_code}")

#### FIXE
def bdf_dates(date):
    try:
        d = date.split('-')
        return f"{d[2]}-{d[1]}-{d[0]}"
    except:
        raise ValueError('Mauvais format de date')

def return_serie(serie, start_date, end_date):
    serie_split = serie.split(' @ ')
    serie_code = serie_split[0]
    type_=serie_code.split('.')[0]
    url = f"https://api.webstat.banque-france.fr/webstat-fr/v1/data/{type_}/{serie_code}?client_id={BDF_API_KEY}&format=json&detail=dataonly&startPeriod={bdf_dates(start_date)}&endPeriod={bdf_dates(end_date)}"
    response = requests.get(url, headers=headers)
    dates = []
    values = []
    if response.status_code == 200:
        data = response.json()
        df = pd.json_normalize(data)
        df_p = pd.json_normalize(df['seriesObs'][0][0])
        df_p_ = pd.json_normalize(df_p["ObservationsSerie.observations"][0])
        for i in range(len(df_p_)):
            date = df_p_["ObservationPeriod.periodFirstDate"][i]
            dates.append(date)
            value = float(df_p_["ObservationPeriod.value"][i])
            values.append(value)
        return pd.DataFrame({serie_code:values}, index= pd.to_datetime(dates))
    else:
        print(f"Failed to retrieve data: {response.status_code}")
print(return_serie(return_series('EXR')[0], '03-06-2020','02-07-2023'))