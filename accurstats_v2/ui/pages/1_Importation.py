##################################################################
############## TO DO
################## FOR MANUALLY IMPORTED FILES, CHECK DATES PROPERLY
#########################################################


import streamlit as st
import sys
import time
import plotly.express as px
st.set_page_config(
    page_title= "AccurStats - Importation",
    page_icon = 'A'
)
sys.path.append('../')
sys.path.append('../../')
sys.path.append('../../../')
from ui import utils_import_ui
from retrieval import utils_bce
import pandas as pd
from config import retrieval_methods
from retrieval import  utils_yfinance
pd.set_option('display.max_columns',None)
### CACHE
# Initialize session state variables if they don't exist
if 'queue' not in st.session_state:
    st.session_state.queue = []
if 'queue_names' not in st.session_state:
    st.session_state.queue_names = []
if 'visualization_toggle' not in st.session_state:
    st.session_state.visualization_toggle = []
if 'to_graph' not in st.session_state:
    st.session_state.to_graph =[]

st.title("Importation de données")

# Dropdown for selecting data retrieval method
choix = st.selectbox("Veuillez choisir un mode d'importation de données:", retrieval_methods)

# Handling different retrieval methods
if choix == retrieval_methods[-1]:
    # File uploader for importing tabular data
    file_ = st.file_uploader('Veuillez importer votre fichier tabulaire')

    if file_ is not None and file_.name not in st.session_state.queue_names:
        st.session_state.visualization_toggle.append(False)
        st.session_state.queue.append(utils_import_ui.read_file(file_))
        for col in st.session_state.queue[-1].columns:
            if 'date' in col.lower() or 'time' in col.lower():
                date_col = col
                break
        try:
            st.session_state.queue[-1].index = pd.to_datetime(st.session_state.queue[-1][date_col])
            st.session_state.queue[-1].pop(date_col)
            st.session_state.queue_names.append(file_.name)
        except:
            st.error("Fichier ne contient pas de colonne date (temps).")

elif choix == retrieval_methods[3]:
    # Text input for searching BCE data
    input = st.text_input('Entrez Ticker à chercher dans BCE.')
    input = str(input)
    try:
        if input:
            st.session_state.visualization_toggle.append(False)
            flow_ref = input.split('.')[0]
            series_key = input[len(flow_ref) + 1:]
            url_ = utils_bce.construct_fetch_url(flow_ref, series_key)
            data = utils_bce.fetch_ecb_data(url_)
            title = utils_bce.get_title(utils_bce.main_url(flow_ref, series_key))
            for col in data.columns:
                if 'date' in col.lower() or 'time' in col.lower():
                    date_col = col
                    data.index= pd.to_datetime(data[date_col])
                    break
            if title + '.pd' in st.session_state.queue_names:
                st.write('Fichier déjà importé')
            else:
                print(data)
                st.session_state.queue.append(data)
                st.session_state.queue_names.append(title + '.pd')
    except:
        st.error('Ticker erroné (exemple de ticker: EXR.D.JPY.EUR.SP00.A) ')
elif choix == retrieval_methods[1]:
    user_input = st.text_input('Entrer ticker:')
    st.write('ou')
    choix_=st.selectbox('Choisir ticker de la liste des tickers suivante:', utils_import_ui.stoxx)
    if choix_ == 'nan' and user_input == '':
        time.sleep(1)
    elif choix_ == 'nan':
        ticker = user_input
        title = user_input
    else:
        try:
            ticker = choix_.split('-')[0].strip()
            title = choix_.split('-')[1]
        except:
            print('nan')
    start_date = st.text_input('Entrer date de début sous la forme suivante 16-09-2019:').strip()
    end_date = st.text_input('Entrer date de fin sous la forme suivante 16-09-2019:').strip()
    while start_date == '' or end_date == '':
        time.sleep(1)
    st.session_state.visualization_toggle.append(False)
    #try:
    if title + " - " + start_date +  " - " +   end_date+ " - "+ "1d" +  '.pd' in st.session_state.queue_names:
        st.write('Fichier déjà importé')
    else:
        data = utils_yfinance.extract_daily([ticker], start_date, end_date, interval = '1d')
        print(data)
        if data.empty:
            st.error('Données inexsistantes sur yfinance, importez les manuellement ou bien sur BCE/BDF...')
            time.sleep(1)
        else:
            for col in data.columns:
                if 'date' in col.lower() or 'time' in col.lower():
                    date_col = col
                    data.index = pd.to_datetime(data[date_col])
                    break
            st.session_state.queue.append(data)
            st.session_state.queue_names.append(title + " - "+ start_date +  " - "+   end_date+" - "+  "1d"+  '.pd')
            choix = ""
            st.rerun()
            #except:
             #st.error("Veuillez choisir une période inférieure à 730 jours")
#except:
#    st.error('YFinance ne reconnait pas ce Ticker ou bien intervalle pas compatible avec difference de dates.')
#     print('Empty yahoo')
if st.session_state.queue_names:
    st.sidebar.header("Fichiers importés")
    for filename in st.session_state.queue_names:
        st.sidebar.write(filename)
else:
    st.sidebar.write("Aucun fichier importé.")
if st.session_state.queue:
    st.write(f"Fichiers importés ({len(st.session_state.queue)}) :")
    for i in range(len(st.session_state.queue_names)):
        st.write(f'Fichier {i + 1}: {st.session_state.queue_names[i]}')
        toggle_button_label = "Visualize" if not st.session_state.visualization_toggle[i] else "Hide Visualization"

        # Use if-else to manage the toggle button state and expanders
        if st.button(toggle_button_label, key=f"toggle_{i}"):
            st.session_state.visualization_toggle[i] = not st.session_state.visualization_toggle[i]

        # Show or hide visualization based on the toggle state
        if st.session_state.visualization_toggle[i]:
            with st.expander(f"Visualisation for {st.session_state.queue_names[i]}", expanded=True):
                df = st.session_state.queue[i]
                columns_exp = [f"{j}: {df.columns[j]} - {df[df.columns[j]].dtype}" for j in range(len(df.columns)) if
                               not ('date' in df.columns[j].lower() or 'time' in df.columns[j].lower() or 'temp' in
                                    df.columns[j].lower())]
                choix_rep_ = st.selectbox('Choisir feature à représenter par rapport au temps:', columns_exp,
                                          key=f"selectbox_{i}")
                choix_rep = df.columns[int(choix_rep_.split(":")[0])]

                # Set date column as index if available
                date_col = None
                for col in df.columns:
                    if 'date' in col.lower() or 'time' in col.lower() or 'temp' in col.lower():
                        date_col = col
                        break
                if date_col is None and not isinstance(df.index,pd.DatetimeIndex):
                    st.error("Il manque les données temporelles (dates) dans les données fournies.")

                elif isinstance(df.index,pd.DatetimeIndex):
                    fig = px.line(df, x=df.index, y=choix_rep, title=f"Time Series of {choix_rep}")
                    st.plotly_chart(fig)
                else:
                    df = df.set_index(date_col)
                    fig = px.line(df, x=df.index, y=choix_rep, title=f"Time Series of {choix_rep}")
                    st.plotly_chart(fig)
                    st.session_state.to_graph.append(pd.DataFrame(df[choix_rep], index=df.index))