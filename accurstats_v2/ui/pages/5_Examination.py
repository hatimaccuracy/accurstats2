import streamlit as st
import sys
import pandas as pd
from core import utils_analyse
import plotly.graph_objects as go
from core import gpt
sys.path.append('../')
sys.path.append('../../')
sys.path.append('../../../')
st.set_page_config(
    page_title= "AccurStats - Examination",
    page_icon = 'A'
)

if 'queue' not in st.session_state:
    st.session_state.queue = []
if 'queue_names' not in st.session_state:
    st.session_state.queue_names = []
if 'visualization_toggle' not in st.session_state:
    st.session_state.visualization_toggle = []
if 'to_graph' not in st.session_state:
    st.session_state.to_graph =[]
if st.session_state.queue_names:
    st.sidebar.header("Fichiers importé")
    for filename in st.session_state.queue_names:
        st.sidebar.write(filename)
else:
    st.sidebar.write("Aucun fichier importé.")
if 'var_expliquer_name' not in st.session_state:
    st.session_state.var_expliquer_name = ''
if 'var_expliquer' not in st.session_state:
    st.session_state.var_expliquer = pd.DataFrame()
if 'drivers' not in st.session_state:
    st.session_state.drivers = []
if 'resultat_screen' not in st.session_state:
    resultat_screen = pd.DataFrame()
if len(st.session_state.resultat_screen) == 0:
    st.error('Pas de screening fait.')
else:
    st.title("Examination d'un modèle")
    st.write("Voici tous les modèles de la phase précedante.")
    st.write(st.session_state.resultat_screen)
    models = [f"Modèle {i}:  {st.session_state.resultat_screen.loc[i,'Predictor 1']} -  {st.session_state.resultat_screen.loc[i,'Predictor 2']} - {i}" for i in range(len(st.session_state.resultat_screen))]
    choice = st.selectbox('Choisissez un modèle à examiner:', models)
    model_index = int(choice.split("-")[-1].strip())
    model = st.session_state.resultat_screen.iloc[model_index]
    pred_1 = model["Predictor 1"].split(" - ")[1].replace('_', '')
    pred_2 = model["Predictor 2"].split(" - ")[1].replace('_', '')
    beta = model['intercept']
    coeff_1 = model['coefficient 1']
    coeff_2 = model['coefficient 2']
    r2 = model['R2-in-sample']
    r2_oos = model['R2-out-of-sample']
    a_expliquer= st.session_state.var_expliquer_name.split("-")[1].replace('_', '')
    if st.button('Valider'):
        st.write("### Equation du model")
        markdown_text = (
                r"$$"
                r"\texttt{{ {} }} = ".format(a_expliquer) +
                r"{} + ".format(round(beta)) +
                r"({}) \cdot \texttt{{ {} }} + ".format(round(coeff_1), pred_1) +
                r"({}) \cdot \texttt{{ {} }}".format(round(coeff_2), pred_2) +
                r"$$"
        )

        # Render the formatted Markdown text
        st.markdown(markdown_text)
        st.write("### Métriques")
        st.write(f"$$R^2 = {r2}$$")
        st.write(r"$$R^2_{\text{oos}} = " +str(r2_oos) + "$$")
        st.write("### Interpretation")
        st.write("##### Interpretation selon ChatGPT")
        st.info('En cours de chargement...')
        st.session_state.chat_gpt_response= gpt.interpret_model(a_expliquer, ["1", beta, pred_1, coeff_1, pred_2 ,coeff_2])
        st.write(st.session_state.chat_gpt_response)

