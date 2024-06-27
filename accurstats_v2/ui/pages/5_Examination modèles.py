##################################################################
############## TO DO
################## FOR MANUALLY IMPORTED FILES, CHECK DATES PROPERLY
#########################################################



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
st.write("### Examination d'un model")
try:
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
        st.write("Voici tous les modèles de la phase précedante.")
        st.write(st.session_state.resultat_screen)
        models = [f"Modèle {i}:  {st.session_state.resultat_screen.loc[i,'Predictor 1']} -  {st.session_state.resultat_screen.loc[i,'Predictor 2']} - {i}" for i in range(len(st.session_state.resultat_screen))]
        with st.expander('Chercher des variables'):
            var1 = st.text_input('Nom de première variable:')
            var2 = st.text_input('Nom de deuxième variable (laisser vide si vous cherchez une seule):')
            if st.button('Chercher'):
                if var1 != '':
                    if var2 == '':
                        filtered_df = st.session_state.resultat_screen[
                            (st.session_state.resultat_screen['Predictor 1'].str.contains(var1)) |
                            (st.session_state.resultat_screen['Predictor 2'].str.contains(var1))
                            ]
                    else:
                        filtered_df = st.session_state.resultat_screen[
                            ((st.session_state.resultat_screen['Predictor 1'].str.contains(var1)) &
                             (st.session_state.resultat_screen['Predictor 2'].str.contains(var2))) |
                            ((st.session_state.resultat_screen['Predictor 1'].str.contains(var2)) &
                             (st.session_state.resultat_screen['Predictor 2'].str.contains(var1)))
                            ]
                    st.write(filtered_df)
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
                    r"{} + ".format(round(beta,5)) +
                    r"({}) \cdot \texttt{{ {} }} + ".format(round(coeff_1,5), pred_1) +
                    r"({}) \cdot \texttt{{ {} }}".format(round(coeff_2,5), pred_2) +
                    r"$$"
            )

            # Render the formatted Markdown text
            st.markdown(markdown_text)


            st.write("### Métriques")
            st.write(f"$$R^2 = {r2}$$")
            st.write(r"$$R^2_{\text{oos}} = " +str(r2_oos) + "$$")

            st.write('### Graphiques')
            pred = st.session_state.drivers[model["Predictor 1"]]*coeff_1 +st.session_state.drivers[model["Predictor 2"]]*coeff_2 +beta
            pred = pred.dropna()
            actual = st.session_state.var_expliquer.dropna()
            common_index = actual.index.intersection(pred.index)
            actual_ = actual.loc[common_index]
            pred_= pred.loc[common_index]
            actual__ = actual.loc[common_index]
            pred__ = pred.loc[common_index]
            num_rows = int(len(actual__) * st.session_state.rho)
            actual__ = actual__.tail(num_rows)
            pred__ = pred__.tail(num_rows)
            # Plotly graph for actual and predicted values
            fig = go.Figure()

            # Add actual values to the plot
            fig.add_trace(go.Scatter(
                x=actual_.index,
                y=actual_,
                mode='lines',
                name='Actual'
            ))
            first_common_date = actual__.index[0]
            fig.add_shape(
                type="line",
                x0=first_common_date,
                y0=min(actual.min(), pred.min()),  # Adjust the y-coordinate as needed
                x1=first_common_date,
                y1=max(actual__.max(), pred__.max()),  # Adjust the y-coordinate as needed
                line=dict(
                    color="gray",  # Color of the dashed line
                    width=2,
                    dash="dashdot",  # Type of dash pattern ('dash', 'dot', 'dashdot')
                )
            )
            # Add predicted values to the plot
            fig.add_trace(go.Scatter(
                x=pred_.index,
                y=pred_,
                mode='lines',
                name='Predicted'
            ))
            fig.add_trace(go.Scatter(
                x=pred__.index,
                y=pred__,
                mode='lines',
                name='Predicted - OOS'
            ))
            fig.add_trace(go.Scatter(
                x=actual__.index,
                y=actual__,
                mode='lines',
                name='Actual - OOS'
            ))

            fig.update_layout(
                title='Actual vs Predicted',
                xaxis_title='Date',
                yaxis_title='Value',
                legend_title='Legend',
                template='plotly_white'
            )

            st.plotly_chart(fig)
            st.write("### Interpretation")

            st.write("##### Interpretation selon ChatGPT")
            st.info('En cours de chargement...')
            st.session_state.chat_gpt_response= gpt.interpret_model(a_expliquer, ["1", beta, pred_1, coeff_1, pred_2 ,coeff_2])
            st.write(st.session_state.chat_gpt_response)

except Exception as e:
    print(e)
    st.error('Pas de fichier importé ou pas de screening fait.')