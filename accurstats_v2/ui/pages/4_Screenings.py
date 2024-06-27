##################################################################
############## TO DO
################## FOR MANUALLY IMPORTED FILES, CHECK DATES PROPERLY
#########################################################

import time
import streamlit as st
import sys

sys.path.append('../')
sys.path.append('../../')
sys.path.append('../../../')

import pandas as pd
from core import utils_analyse
from core import utils_screening
pd.set_option('display.max_columns',None)


st.set_page_config(
    page_title= "AccurStats - Screening",
    page_icon = 'A'
)
st.title("Screening des variables")
st.write("Choisissez la variable à expliquer, les drivers et le modèle. Revenez à la partie analyse pour faire les transformations que vous voulez.")
if 'para_index_d' not in st.session_state:
    para_index = pd.DataFrame()
if 'para_index_e' not in st.session_state:
    para_index = pd.DataFrame()
if 'rho' not in st.session_state:
    st.session_state.rho = 0.01
if 'queue' not in st.session_state:
    st.session_state.queue = []
if 'queue_names' not in st.session_state:
    st.session_state.queue_names = []
if 'visualization_toggle' not in st.session_state:
    st.session_state.visualization_toggle = []
if 'to_graph' not in st.session_state:
    st.session_state.to_graph =[]
if 'resultat_screen' not in st.session_state:
    resultat_screen = pd.DataFrame()
if st.session_state.queue_names:
    st.sidebar.header("Fichiers importé")
    for filename in st.session_state.queue_names:
        st.sidebar.write(filename)
else:
    st.sidebar.write("Aucun fichier importé.")
st.sidebar.header('Screening')
if 'var_expliquer_name' not in st.session_state:
    st.session_state.var_expliquer_name = ''
if 'var_expliquer' not in st.session_state:
    st.session_state.var_expliquer = pd.DataFrame()
if 'drivers' not in st.session_state:
    st.session_state.drivers = []
if 'to_drivers' not in st.session_state:
    st.session_state.to_drivers = pd.DataFrame()
if 'to_explique' not in st.session_state:
    st.session_state.to_explique = pd.DataFrame()
try:
    files = [str(i) + " @ " + st.session_state.queue_names[i] for i in range(len(st.session_state.queue_names))]
    st.write("---")
    with st.expander('Variable à expliquer'):
        file = st.selectbox('Choisir fichier contenant la variable à expliquer:', files)
        pot_expl = [ ]
        if file != '':
            index = int(file.split('@')[0].strip())
            for r in st.session_state.queue[index].columns:
                pot_expl.append(str(index) + " - " + r)
        col_to = st.selectbox('Choisir colonne à expliquer:', pot_expl)
        if st.button('Confirmer', key="conf_explique"):
            st.session_state.var_expliquer_name = col_to
            st.session_state.var_expliquer =  st.session_state.queue[index][col_to.split('-')[1].strip()]
            st.success('Variable à expliquer choisie avec succès')
    if st.session_state.var_expliquer_name:
        st.sidebar.write(f"Variable à expliquer: {st.session_state.var_expliquer_name}")
    with (st.expander('Drivers')):
        drivers_files = st.multiselect('Choisir fichiers:', files)
        pot_col = []
        for j in drivers_files:
            index = int(j.split('@')[0].strip())
            for r in st.session_state.queue[index].columns:
                if (str(index) + " @ " + r==st.session_state.var_expliquer_name):
                    continue
                else:
                    pot_col.append(str(index) + " @ " + r)
        to_columns = st.multiselect('Choisir colonnes:', pot_col)
        union = pd.DataFrame()
        meth = st.selectbox("Sélectionner une méthode d'interpolation si nécessaire:", utils_analyse.interpolations,
                            key=f'meth_glob')
        if st.button("Confimer", key='choix_drivers'):
            for j in to_columns:
                index = int(j.split('@')[0].strip())
                column = j.split('@')[1].strip()
                union[str(index) + " - "+ column] = st.session_state.queue[index][column]
            for j in range(len(union.columns)):
                r_col = union.columns[j]
                t = str(union[r_col].dtype)
                if ('int' not in t and 'float' not in t):
                    continue
                else:
                    union = utils_analyse.interpolate(data=union, i=j, inter=meth)
            st.session_state.drivers = union.sort_index()
            st.success('Le choix des drivers est confirmé.')
    try:
        drivers = list(st.session_state.drivers.columns)
        st.sidebar.write(f'Variable drivers: {drivers}')
    except:
        st.sidebar.write('Variable drivers: ')
    st.write("---")
    st.write(f"#### Screening de {st.session_state.var_expliquer_name} par les variables drivers avec regression linéaire:" )
    st.session_state.to_drivers = st.session_state.drivers.copy()
    st.session_state.to_explique = st.session_state.var_expliquer.copy()
    st.session_state.para_index_d = st.session_state.drivers.copy()
    st.session_state.para_index_e = st.session_state.var_expliquer.copy()
    if isinstance(st.session_state.var_expliquer.index, pd.DatetimeIndex):
        st.session_state.to_explique = st.session_state.to_explique.reset_index()

    if isinstance(st.session_state.drivers.index, pd.DatetimeIndex):
        st.session_state.to_drivers = st.session_state.to_drivers.reset_index()

    st.session_state.to_explique = st.session_state.to_explique.sort_index()
    st.session_state.to_drivers = st.session_state.to_drivers.sort_index()

    st.session_state.para_index_d = st.session_state.para_index_d.sort_index()
    st.session_state.para_index_e = st.session_state.para_index_e.sort_index()

    st.session_state.to_drivers = st.session_state.to_drivers.dropna()
    st.session_state.to_explique = st.session_state.to_explique.dropna()

    st.session_state.para_index_d = st.session_state.para_index_d.dropna()
    st.session_state.para_index_e = st.session_state.para_index_e.dropna()



    nbr_points= len(st.session_state.to_drivers)
    st.session_state.rho = float( st.slider(r'Choisir nombre de points pour backtesting:', 1, nbr_points))/nbr_points
    if st.button('Commencer screening', key=f"begin_screen"):
        st.sidebar.write("Pourentage screening:")
        custom_progress_bar = st.sidebar.progress(0)
        try:
            st.session_state.resultat_screen = utils_screening.Model_screening(st.session_state.to_drivers, st.session_state.to_explique ,st.session_state.rho, utils_screening.Model_reg, custom_progress_bar)
            st.write('Modèles proposés, pour détailler un model, voir partie examination')
            st.write(st.session_state.resultat_screen)
        except Exception as e:
            print(e)
            st.session_state.drivers = []
            st.session_state.var_expliquer_name=''
            st.session_state.var_expliquer = pd.DataFrame()
            st.session_state.resultat_screen = pd.DataFrame()
            st.error("Ressayer.")
            time.sleep(2)
except Exception as e:
    print(e)
    st.error('Pas de fichier importé.')