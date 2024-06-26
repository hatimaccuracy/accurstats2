import streamlit as st
import sys
import pandas as pd
from core import utils_analyse

sys.path.append('../')
sys.path.append('../../')
sys.path.append('../../../')
st.set_page_config(
    page_title= "AccurStats - Screening",
    page_icon = 'A'
)
st.title("Screening des variables")
st.write("Choisissez la variable à expliquer, les drivers et le modèle. Revenez à la partie analyse pour faire les transformations que vous voulez.")
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

if 'var_expliquer' not in st.session_state:
    st.session_state.var_expliquer = ''
if 'drivers' not in st.session_state:
    st.session_state.drivers = []
files = [str(i) + " - " + st.session_state.queue_names[i] for i in range(len(st.session_state.queue_names))]
with st.expander('Variable à expliquer'):
    file = st.selectbox('Choisir fichier contenant la variable à expliquer:', files)
    pot_expl = [ ]
    if file != '':
        index = int(file.split('-')[0].strip())
        for r in st.session_state.queue[index].columns:
            pot_expl.append(str(index) + " - " + r)
    col_to = st.selectbox('Choisir colonne à expliquer:', pot_expl)
    if st.button('Confirmer', key="conf_explique"):
        st.session_state.var_expliquer = col_to
        st.success('Variable à expliquer choisie avec succès')

if st.session_state.var_expliquer:
    st.sidebar.header('Screening')
    st.sidebar.write(f"Variable à expliquer: {st.session_state.var_expliquer}")
with (st.expander('Drivers')):
    drivers_files = st.multiselect('Choisir fichiers:', files)
    pot_col = []
    for j in drivers_files:
        index = int(j.split('-')[0].strip())
        for r in st.session_state.queue[index].columns:
            if (str(index) + " - " + r==st.session_state.var_expliquer):
                continue
            else:
                pot_col.append(str(index) + " - " + r)
    to_columns = st.multiselect('Choisir colonnes:', pot_col)
    union = pd.DataFrame()
    meth = st.selectbox("Sélectionner une méthode d'interpolation si nécessaire:", utils_analyse.interpolations,
                        key=f'meth_glob')
    if st.button("Confimer", key='choix_drivers'):
        for j in to_columns:
            index = int(j.split('-')[0].strip())
            column = j.split('-')[1].strip()
            union[str(index) + " - "+ column] = st.session_state.queue[index][column]
        for j in range(len(union.columns)):
            r_col = union.columns[j]
            t = str(union[r_col].dtype)
            if ('int' not in t and 'float' not in t):
                continue
            else:
                union = utils_analyse.interpolate(data=union, i=j, inter=meth)
        st.session_state.drivers = union
try:
    drivers = list(st.session_state.drivers.columns)
    st.sidebar.write(f'Variable drivers: {drivers}')
except:
    st.sidebar.write('Variable drivers: ')