import pandas as pd
import streamlit as st
import time
stoxx = list(pd.read_csv('st.csv')['ST'])
intervals = ['','1d','1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '5d', '1wk', '1mo', '3mo']
def autocomplete(input_text, suggestions):
    matches = [s for s in suggestions if input_text.lower() in s.lower()]
    return matches

def read_file(uploaded_file):
    file_extension = uploaded_file.name.split('.')[-1].lower()

    if file_extension == 'csv':
        deli = st.selectbox('Choisir delimitation:', ['', ';', ',', r'\t'])
        while (deli == ''):
            time.sleep(1)
        deci = st.selectbox('Choisir delimitation décimale:', ['', ';', ',', r'\t'])
        while (deci == ''):
            time.sleep(1)
        return pd.read_csv(uploaded_file, delimiter=deli, decimal= deci)
    elif file_extension in ['xls', 'xlsx']:
        xls = pd.read_excel(uploaded_file, sheet_name=None)
        sheet_names = list(xls.keys())
        sheet_names.insert(0,'')
        sheet = st.selectbox('Choisir sheet:',sheet_names )
        while (sheet == ''):
            time.sleep(1)
        return pd.read_excel(uploaded_file, sheet_name=sheet)
    elif file_extension == 'json':
        return pd.read_json(uploaded_file)
    elif file_extension == 'html':
        return pd.read_html(uploaded_file)
    elif file_extension == 'parquet':
        return pd.read_parquet(uploaded_file)
    elif file_extension == 'hdf':
        return pd.read_hdf(uploaded_file)
    elif file_extension == 'feather':
        return pd.read_feather(uploaded_file)
    elif file_extension == 'orc':
        return pd.read_orc(uploaded_file)
    elif file_extension == 'sas':
        return pd.read_sas(uploaded_file)
    elif file_extension == 'spss':
        return pd.read_spss(uploaded_file)
    else:
        raise ValueError(f"Unsupported file extension: {file_extension}")
