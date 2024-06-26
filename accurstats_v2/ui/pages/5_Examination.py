import streamlit as st
import sys
import pandas as pd
from core import utils_analyse

sys.path.append('../')
sys.path.append('../../')
sys.path.append('../../../')
st.set_page_config(
    page_title= "AccurStats - Examination",
    page_icon = 'A'
)
st.title("Examination d'un modèle")
st.write("Ceci est une description sympathique d'AccurStats.")
st.write("Pour commencer, cliquer sur importation.")
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
files = [str(i) + " - " + st.session_state.queue_names[i] for i in range(len(st.session_state.queue_names))]
to_grr = st.multiselect('Choisir fichiers:', files)
pot_col = []
for j in to_grr:
    index = int(j.split('-')[0].strip())
    for r in st.session_state.queue[index].columns:
        pot_col.append(str(index) + " - " + r)
to_columns = st.multiselect('Choisir columns', pot_col)
union = pd.DataFrame()
meth = st.selectbox("Sélectionner une méthode d'interpolation si nécessaire:", utils_analyse.interpolations,
                    key=f'meth_glob')

for j in to_columns:
    index = int(j.split('-')[0].strip())
    column = j.split('-')[1].strip()
    union[column] = st.session_state.queue[index][column]
for j in range(len(union.columns)):
    r_col = union.columns[j]
    t = str(union[r_col].dtype)
    if ('int' not in t and 'float' not in t):
        continue
    else:
        union = utils_analyse.interpolate(data=union, i=j, inter=meth)
check_normal = st.checkbox(
    r'Normaliser les variables suivant $$ N(X) = \dfrac{X- \textbf{E}(X)}{\sigma(X)}$$',
    key=f"nor_tous")
if st.button('Visualiser'):
    if check_normal:
        for j in union.columns:
            try:
                union[j] = (union[j] - np.mean(union[j])) / np.std(union[j])
            except:
                st.error("Vous essayez de normaliser une valeur non numérique.")
    fig = go.Figure()
    for col in union.columns:
        fig.add_trace(go.Scatter(x=union.index, y=union[col], mode='lines', name=col))

    fig.update_layout(
        title='Visualisation collective',
        xaxis_title='Index',
        yaxis_title='Valeur'
    )
    st.plotly_chart(fig)
