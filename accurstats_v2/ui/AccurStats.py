##################################################################
############## TO DO
################## WRITE STEPS AND WARNINGS ETC
#########################################################

import streamlit as st
import pandas as pd
import sys
sys.path.append('../')
sys.path.append('../../')
sys.path.append('../../../')
st.set_page_config(
    page_title= "AccurStats - Bienvenue",
    page_icon = 'A'
)
st.title('Bienvenue à AccurStats')
st.write("Guide de navigation:")
st.markdown(r"$$\blacktriangleright \textbf{Importation}:$$ Pour commencer, on peut importer des fichiers localement ou bien directement de la BCE/BDF ou Yahoo Finance.")
st.markdown(r"$$\blacktriangleright \textbf{Analyse et transformations}:$$ Cette partie vous permet de faire les différents analyse sur les series temporelles possibles ainsi que faire des transformations sur vos données (normalisation, interpolation, ...).")
st.markdown(r"$$\blacktriangleright \textbf{Visualisation et gestion des données}:$$ Cette partie vous permet de visualiser des parties de vos données ainsi que de les gérer (supprimer colonne, supprimer fichier).")
st.markdown(r"$$\blacktriangleright \textbf{Screening}:$$ Cette partie vous fournit une multitude de variables expliquatives avec des métriques différentes.")
st.markdown(r"$$\blacktriangleright \textbf{Examination modèles}:$$ Cette partie vous permet d'examiner un modèle fournit par le screening de près (interpretation, fit i.e graphiques...).")

if 'queue' not in st.session_state:
    st.session_state.queue = []
if 'queue_names' not in st.session_state:
    st.session_state.queue_names = []
if 'visualization_toggle' not in st.session_state:
    st.session_state.visualization_toggle = []
if 'to_graph' not in st.session_state:
    st.session_state.to_graph =[]
if 'var_expliquer_name' not in st.session_state:
    st.session_state.var_expliquer_name = ''
if 'var_expliquer' not in st.session_state:
    st.session_state.var_expliquer = pd.DataFrame()
if 'drivers' not in st.session_state:
    st.session_state.drivers = []
if 'resultat_screen' not in st.session_state:
    resultat_screen = pd.DataFrame()
if st.session_state.queue_names:
    st.sidebar.header("Fichiers importé")
    for filename in st.session_state.queue_names:
        st.sidebar.write(filename)
else:
    st.sidebar.write("Aucun fichier importé.")