##################################################################
############## TO DO
################## DESCRIPTION
#########################################################

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys
from core import utils_analyse

# Ensure paths are set correctly if needed
sys.path.append('../')
sys.path.append('../../')
sys.path.append('../../../')

import matplotlib.pyplot as plt
import seaborn as sns
# Set page configuration
st.set_page_config(
    page_title="AccurStats - Visualisation",
    page_icon='A'
)

# Main title and description
st.title('Visualisation et gestion des données traités/importés')
st.write("Pour supprimer un fichier, cliquer sur le fichier puis sur supprimer.")
st.write("Pour tracer un ensemble de features d'un fichier particulier, cliquer sur le fichier puis visualiser.")
st.write('Pour tracer un ensemble de features pas nécessairement dans le même fichier, utiliser la dernière partie.')

# Initialize session state variables
if 'queue' not in st.session_state:
    st.session_state.queue = []
if 'queue_names' not in st.session_state:
    st.session_state.queue_names = []
if 'visualization_toggle' not in st.session_state:
    st.session_state.visualization_toggle = []
if 'to_graph' not in st.session_state:
    st.session_state.to_graph = []

# Sidebar section for displaying imported files using st.expander
if st.session_state.queue_names:
    st.sidebar.header("Fichiers importé")
    for filename in st.session_state.queue_names:
        st.sidebar.write(filename)
else:
    st.sidebar.write("Aucun fichier importé.")

# Main content for visualizing data with Plotly
if st.session_state.queue_names:
    for i in range(len(st.session_state.queue_names)):
        with st.expander(f"Fichier {i + 1}: {st.session_state.queue_names[i]}"):
            st.write('#### Visualisations', key =f"vis_{i}")
            # Multiselect for choosing features to visualize
            to_gr = st.multiselect('Choisir features à visualiser (vous pouvez choisir plusieurs):',
                                   st.session_state.queue[i].columns[1:], key=f'to_graph{i}')
            check_normal = st.checkbox(
                r'Normaliser les variables suivant $$ N(X) = \dfrac{X- \textbf{E}(X)}{\sigma(X)}$$',
                key=f"nor_{i}")
            if st.button("Visualiser", key=f'trace_{i}'):
                fig = go.Figure()
                if check_normal:
                    for j in to_gr:
                        try:
                            normalized_data = (st.session_state.queue[i][j] - np.mean(
                                st.session_state.queue[i][j])) / np.std(st.session_state.queue[i][j])
                            fig.add_trace(go.Scatter(x=st.session_state.queue[i].index, y=normalized_data, mode='lines',
                                                     name=f'{j} (Normalized)'))
                        except Exception as e:
                            st.error(f'Erreur: {str(e)}')
                else:
                    for j in to_gr:
                        fig.add_trace(
                            go.Scatter(x=st.session_state.queue[i].index, y=st.session_state.queue[i][j], mode='lines',
                                       name=f'{j}'))

                fig.update_layout(
                    title=f'Données du fichier {i + 1}: {st.session_state.queue_names[i]}',
                    xaxis_title='Index',
                    yaxis_title='Valeur'
                )
                st.plotly_chart(fig)

            st.write('---')
            to_corr = st.multiselect(
                'Choisir features pour lesquels on étudie la correlation (vous pouvez choisir plusieurs):',
                st.session_state.queue[i].columns, key=f'to_corr{i}'
            )
            check_normal = st.checkbox(
                r'Normaliser les variables suivant $$ N(X) = \dfrac{X- \textbf{E}(X)}{\sigma(X)}$$',
                key=f"nor_corr_{i}"
            )
            if st.button("Calculer Corrélation", key=f'corr_{i}'):
                if len(to_corr) < 2:
                    st.error("Veuillez sélectionner au moins deux features.")
                else:
                    try:
                        data_to_corr = st.session_state.queue[i][to_corr]

                        if check_normal:
                            data_to_corr = (data_to_corr - data_to_corr.mean()) / data_to_corr.std()

                        correlation_matrix = data_to_corr.corr()

                        st.write(f'Corrélation des données du fichier {i + 1}: {st.session_state.queue_names[i]}')

                        # Plotting the heatmap
                        fig, ax = plt.subplots()
                        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', ax=ax)
                        st.pyplot(fig)
                    except Exception as e:
                        st.error(f'Erreur: {str(e)}')
            st.write('---')
            st.write('#### Suppressions', key=f"vis_{i}")
            # Multiselect for choosing columns to delete
            cols_to_del = st.multiselect('Choisir colonnes à supprimer:', st.session_state.queue[i].columns,
                                         key=f'del{i}')
            if st.button('Supprimer', key=f"key_del_col{i}"):
                st.session_state.queue[i] = st.session_state.queue[i].drop(columns=cols_to_del)
                st.success('Transformation bien fait')
                time.sleep(2)
                st.rerun()

            st.write('---')
            st.write('Cliquer ici pour supprimer le fichier.')
            if st.button('Supprimer', key=f"key_del{i}"):
                del st.session_state.queue_names[i]
                del st.session_state.queue[i]
                st.session_state.visualization_toggle.pop()
                st.rerun()

    # Expander for collective visualization
    with st.expander('Visualisation collective'):
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
            union[j] = st.session_state.queue[index][column]
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
                xaxis_title='Date',
                yaxis_title='Valeur'
            )
            st.plotly_chart(fig)

else:
    st.error("Aucun fichier importé.")
