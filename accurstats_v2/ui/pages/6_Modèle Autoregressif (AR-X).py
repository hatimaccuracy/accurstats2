##################################################################
############## TO DO
################## FOR MANUALLY IMPORTED FILES, CHECK DATES PROPERLY
#########################################################


import statsmodels.api as sm
import streamlit as st
import sys
from core import utils_screening
import pandas as pd
import numpy as np
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
st.write("### Application du modèle AR-X pour un couple de variables")
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
try:
    if len(st.session_state.resultat_screen) == 0:
        st.error('Pas de screening fait.')
    else:
        st.write("Voici tous les modèles de la phase précedante.")
        st.write(st.session_state.resultat_screen)
        models = [f"Modèle {i}:  {st.session_state.resultat_screen.loc[i,'Predictor 1']} -  {st.session_state.resultat_screen.loc[i,'Predictor 2']} - {i}" for i in range(len(st.session_state.resultat_screen))]
        choice = st.selectbox("Choisissez un modèle sur lequel appliquer l'AR-X:", models)
        ordre = st.slider("Choisissez l'ordre d'autoregression $k$",1,12)
        nbr_points = len(st.session_state.to_drivers)
        rho = float(st.slider(r'Choisir nombre de points pour backtesting:', 1, nbr_points)) / nbr_points
        model_index = int(choice.split("-")[-1].strip())
        model = st.session_state.resultat_screen.iloc[model_index]
        pred_1 = model["Predictor 1"].split(" - ")[1].replace('_', '')
        pred_2 = model["Predictor 2"].split(" - ")[1].replace('_', '')
        beta = model['intercept']

        r2 = model['R2-in-sample']
        r2_oos = model['R2-out-of-sample']
        a_expliquer= st.session_state.var_expliquer_name.split("-")[1].replace('_', '')
        exp1 =  pd.DataFrame(st.session_state.para_index_d[model["Predictor 1"]]).reset_index()
        exp2 = pd.DataFrame(st.session_state.para_index_d[model["Predictor 2"]]).reset_index()

        # Fonction qui l'AR-X
        # results.summary() : pour fournir un résumé du modèle
        # results.params : pour renvoyer les coefficients estimés du modèle
        # results.pvalues : les p-valeurs des coefficients
        # results.fittedvalues : Renvoie les valeurs ajustées (prédites) par le modèle pour les données d'entraînement
        # results.resid : Renvoie les résidus (différences entre les valeurs observées et ajustées)

        if st.button('Valider'):
            #return results, dates_train, endog_train, exog_test, dates_test, endog_test, exog_train
            main_arx_df = utils_screening.Model_ARX_rho(st.session_state.para_index_e.reset_index(),exp1,exp2,  ordre=ordre, rho=rho)
            beta = main_arx_df[0].params[0]
            coeff_1 = main_arx_df[0].params[1]
            coeff_2 = main_arx_df[0].params[2]
            st.write("### Equation du model")
            markdown_text = (
                    r"$$"
                    r"\texttt{{ {}}}_t = ".format(a_expliquer) +
                    r"{} + ".format(round(beta, 5)) +
                    r"({}) \cdot \texttt{{ {}}}_t + ".format(round(coeff_1, 5), pred_1) +
                    r"({}) \cdot \texttt{{ {}}}_t".format(round(coeff_2, 5), pred_2) +
                    r"$$"
            )
            composante_text = ' $$'
            for i in range(ordre):
                composante_text += r"+({}) \cdot \texttt{{ {}}}_{{ t - {} }}  ".format(round(main_arx_df[0].params[3 + i], 5),
                                                                                        a_expliquer, i + 1)
            composante_text+= "$$"
            # Render the formatted Markdown text
            st.markdown(markdown_text + composante_text)



            pred_ = main_arx_df[0].predict(sm.add_constant(main_arx_df[6]))
            pred__ = main_arx_df[0].predict(sm.add_constant(main_arx_df[3]))
            date_ = main_arx_df[1]
            date__ = main_arx_df[4]
            actual_ = main_arx_df[2]
            actual__ = main_arx_df[5]

            ss_res = np.sum((actual_ - pred_) ** 2)
            ss_tot = np.sum((actual_ - np.mean(actual_)) ** 2)
            r2 = 1 - (ss_res / ss_tot)

            ss_res_test = np.sum((actual__ - pred__) ** 2)
            ss_tot_test = np.sum((actual__ - np.mean(actual__)) ** 2)
            r2_oos = 1 - (ss_res_test / ss_tot_test)

            st.write("### Métriques")
            st.write(f"$$R^2 = {r2}$$")
            st.write(r"$$R^2_{\text{oos}} = " + str(r2_oos) + "$$")

            st.write('### Graphiques')
            fig = go.Figure()

            # Add actual values to the plot
            fig.add_trace(go.Scatter(
                x=date_,
                y=actual_,
                mode='lines',
                name='Actual'
            ))
            first_common_date =date__.iloc[0]
            fig.add_shape(
                type="line",
                x0=first_common_date,
                y0=min(min(actual_.min(), pred_.min()), min(actual__.min(), pred__.min())),  # Adjust the y-coordinate as needed
                x1=first_common_date,
                y1=max(max(actual_.max(), pred_.max()), max(actual__.max(), pred__.max())),  # Adjust the y-coordinate as needed
                line=dict(
                    color="gray",  # Color of the dashed line
                    width=2,
                    dash="dashdot",  # Type of dash pattern ('dash', 'dot', 'dashdot')
                )
            )
            # Add predicted values to the plot
            fig.add_trace(go.Scatter(
                x=date_,
                y=pred_,
                mode='lines',
                name='Predicted'
            ))
            fig.add_trace(go.Scatter(
                x=date__,
                y=pred__,
                mode='lines',
                name='Predicted - OOS'
            ))
            fig.add_trace(go.Scatter(
                x=date__,
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

            st.write('### Summary')
            st.write(main_arx_df[0].summary())
except:
    st.error('Pas de screening ou fichiers.')