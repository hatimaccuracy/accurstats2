import requests
import pandas as pd
from io import StringIO
from bs4 import BeautifulSoup

def construct_fetch_url(flow_ref, series_key, start_period=None, end_period=None, format_type='csvdata', detail='full', include_history='false'):
    base_url = 'https://data-api.ecb.europa.eu/service/data/'
    url = f"{base_url}{flow_ref}/{series_key}?format={format_type}&detail={detail}&includeHistory={include_history}"

    if start_period:
        url += f"&startPeriod={start_period}"
    if end_period:
        url += f"&endPeriod={end_period}"

    return url


def main_url(flow_ref, series_key):
    base_url ='https://data.ecb.europa.eu/data/datasets/'
    url = f"{base_url}{flow_ref}/{flow_ref}.{series_key}"
    return url


def fetch_ecb_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = pd.read_csv(StringIO(response.text))
        return data
    else:
        print(f"Mauvaise requête: {response.status_code}")
        return None

def get_title(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    title = soup.find('div', class_='title-social-wrapper')
    export =  str(title).split('\n')[4].lstrip()
    if export == "</h1>":
        return 'Titre indisponible'
    else:
        return export
"""
#Exemple d'utilisation
flow_ref = 'EXR'
series_key = 'D.USD.EUR.SP00.A'
start_period = '2022-01-01'
end_period = '2024-12-31'

# Construct the URL
url = construct_fetch_url(flow_ref, series_key, start_period, end_period)
url_ = main_url(flow_ref, series_key)
print(f"Constructed URL: {url}")
print(get_title(url_))
# Fetch the data
data = fetch_ecb_data(url)

# Display the data
if data is not None:
    print(data)
else:
    print("Données non reçus")
"""

