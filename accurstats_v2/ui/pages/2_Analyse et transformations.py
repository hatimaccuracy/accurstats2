##################################################################
############## TO DO
################## k dans croissances
#########################################################

import pandas as pd
import streamlit as st
import sys
import numpy as np
from core import utils_analyse
import time
from core import utils_extraction_TS
sys.path.append('../')
sys.path.append('../../')
sys.path.append('../../../')

####### CONFIGUARTION PAGE ST
st.set_page_config(
    page_title= "AccurStats - Analyse et transformations",
    page_icon = 'A'
)


##### DESCRIPTION
st.title('Analyse des données importés')
st.write("Cette page vous permet de manipuler les données que vous venez d'entrer.")
st.write("Vous pouvez transformer autant que vous voulez les colonnes des données d'entrées, il en résulte une nouvelle colonne notée (T) - NOM_DE_COLONNE - TRANSFORMATION.")
st.write('Pour des visualisations ou suppression de fichiers, voir partie visualisation...')
st.warning('Assurez-vous bien que vous appliquer des transformations sur des données quantitatives (numériques)')
#### INITIALISATION DE QQ VARIABES
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
#### DEFILE DES FICHIERS
if st.session_state.queue_names:
    for i in range(len(st.session_state.queue_names)):


        ####### TRAITEMENT DE FICHIER I
        st.write(f"### Fichier {i+1}: {st.session_state.queue_names[i]}")

        #### ONGLET - CHANGEMENT DE FREQUENCE
        with st.expander('Changement de fréquence'):
            choix_res = st.selectbox('Choisir nouvelle fréquence:', ['D - Jour', 'W - Semaine', 'M - Mois', 'Q - Trimestre', 'Y - Année' , 'H - Heure', 'T - Minute', 'S - Second'], key=f"freq_change{i}")
            agg = st.selectbox("Choisir fonction d'aggregation:", ['mean - Moyenne', 'max - Valeur maximale', 'sum - Somme'], key=f"freq_agg{i}")
            st.info('Après changement de fréquence vers une fréquence plus petite, vous pouvez utiliser les interpolations (onglet transformations) pour de meilleurs résultats.')
            if st.button('Appliquer', key=f"changement_freq{i}"):
                if "mean" in agg:
                    agg_ = 'mean'
                else:
                    agg_ = agg[:3]
                st.session_state.queue.insert(i+1,st.session_state.queue[i].asfreq(choix_res[0].lower()))
                st.session_state.queue[i+1].index.freq = choix_res[0].lower()
                for col in st.session_state.queue[i+1].columns:
                    if 'int' in col or 'float' in col:
                        st.session_state.queue[i+1][col] = st.session_state.queue[i+1][col].aggregate(agg_)
                    else:
                        continue

                st.session_state.queue_names.insert(i+1,st.session_state.queue_names[i]+ f" (T)/ {choix_res} / {agg}")
                st.success(f'Changement de fréquence en {choix_res}/{agg_} fait avec succes')
                st.rerun()


        #### ONGLET - TRANSFORMATIONS
        with st.expander('Transformations'):

            #### INTERPOLATION
            st.write("##### Interpolation")
            columns = [str(j) + ' - '+ st.session_state.queue[i].columns[j] + ' - '+ str(st.session_state.queue[i][st.session_state.queue[i].columns[j]].dtype) for j in range(1,len(st.session_state.queue[i].columns))]
            columns.insert(0,'TOUT')
            selected_column_int = st.multiselect("Sélectionner des colonnes :", columns, key = f'col{i}')
            meth = st.selectbox("Sélectionner une méthode d'interpolation:", utils_analyse.interpolations, key =f'meth{i}')
            check_inplace=st.checkbox('Remplacer colonne par sa tranformée', key = f'check_inter{i}')
            if st.button("Appliquer la transformation", key = f'but{i}'):
                if 'TOUT' in  selected_column_int :
                    for j in range(len(st.session_state.queue[i].columns)):
                        t = str(st.session_state.queue[i][st.session_state.queue[i].columns[j]].dtype)
                        r_col = st.session_state.queue[i].columns[j]
                        if ('int' not in t and 'float' not in t):
                            continue
                        else:
                            output = utils_analyse.interpolate(data=st.session_state.queue[i], i=j, inter=meth)
                            if check_inplace:
                                st.session_state.queue[i][r_col] = output[r_col]
                            else:
                                st.session_state.queue[i][f"(T) / {r_col} / INTERPOLATION_{meth}"] = output[r_col]
                    st.success(f"Transformation appliquée avec succès pour tout le fichier avec la méthode {meth}")
                else:
                    for j in selected_column_int:
                        index = int(j.split('-')[0].strip())
                        r_col = st.session_state.queue[i].columns[index]
                        output = utils_analyse.interpolate(data=st.session_state.queue[i], i=index, inter= meth)
                        if check_inplace:
                            st.session_state.queue[i][r_col] = output[r_col]
                        else:
                            st.session_state.queue[i][f"(T) / {r_col} / INTERPOLATION_{meth}"] = output[r_col]
                        st.success(f"Transformation appliquée avec succès pour {r_col} avec la méthode {meth}")
            st.write("---")



            ####NORMALISATION
            st.write("##### Normalisation")
            st.write("Vous êtez en train d'appliquer l'opération suivante:")
            st.markdown(r'$$ N(X) = \dfrac{X- \textbf{E}(X)}{\sigma(X)}$$')
            selected_column_int = st.multiselect("Sélectionner des colonnes :", columns, key=f'col_norm{i}')
            check_inplace = st.checkbox('Remplacer colonne par sa tranformée', key=f'check_norm{i}')
            if st.button("Appliquer la transformation", key=f'but_norm{i}'):
                if 'TOUT' in selected_column_int:
                    for j in range(len(st.session_state.queue[i].columns)):
                        t = str(st.session_state.queue[i][st.session_state.queue[i].columns[j]].dtype)
                        r_col = st.session_state.queue[i].columns[j]
                        if ('int' not in t and 'float' not in t):
                            continue
                        else:
                            output = (st.session_state.queue[i][r_col]  -np.mean(st.session_state.queue[i][r_col] ))/np.std(st.session_state.queue[i][r_col] )
                            if check_inplace:
                                st.session_state.queue[i][r_col] = output
                            else:
                                st.session_state.queue[i][f"(T) / {r_col} / NORMALISATION"] = output
                    st.success(f"Normalisation appliquée avec succès pour tout le fichier")
                else:
                    for j in selected_column_int:
                        index = int(j.split('-')[0].strip())
                        r_col = st.session_state.queue[i].columns[index]
                        output = (st.session_state.queue[i][r_col] - np.mean(
                            st.session_state.queue[i][r_col])) / np.std(st.session_state.queue[i][r_col])
                        if check_inplace:
                            st.session_state.queue[i][r_col] = output
                        else:
                            st.session_state.queue[i][f"(T) / {r_col} / NORMALISATION"] = output
                        st.success(f"Normalisation appliquée avec succès pour {r_col}")

            st.write("---")


            ##### LAG SIMPLE
            st.write("##### Appliquation d'un lag")
            st.write("Vous êtez en train d'appliquer l'opération suivante:")
            st.markdown(r'$$\texttt{Transformation}(\text{Colonne}, k)_t = \text{Colonne}_t - \text{Colonne}_{t-k}$$')
            parameter_value = st.slider("Sélectionner un paramètre $k$ (1 à 12) :", 1, 12, key = f'param_lag{i}')
            selected_column_int = st.multiselect("Sélectionner des colonnes :", columns, key=f'col_lag{i}')
            check_inplace = st.checkbox('Remplacer colonne par sa tranformée', key=f'check_lag{i}')
            if st.button("Appliquer la transformation", key=f'but_lag{i}'):
                if 'TOUT' in selected_column_int:
                    for j in range(len(st.session_state.queue[i].columns)):
                        t = str(st.session_state.queue[i][st.session_state.queue[i].columns[j]].dtype)
                        r_col = st.session_state.queue[i].columns[j]
                        if ('int' not in t and 'float' not in t):
                            continue
                        else:
                            output = utils_extraction_TS.lag(st.session_state.queue[i][r_col],parameter_value)
                            if check_inplace:
                                st.session_state.queue[i][r_col] = output
                            else:
                                st.session_state.queue[i][f"(T) / {r_col} / LAG_{parameter_value}"] = output
                    st.success(f"LAG appliquée avec succès pour tout le fichier avec pas {parameter_value}")
                else:
                    for j in selected_column_int:
                        index = int(j.split('-')[0].strip())
                        r_col = st.session_state.queue[i].columns[index]
                        output = utils_extraction_TS.lag(st.session_state.queue[i][r_col],parameter_value)
                        if check_inplace:
                            st.session_state.queue[i][r_col] = output
                        else:
                            st.session_state.queue[i][f"(T) / {r_col} / LAG_{parameter_value}"] = output
                        st.success(f"Lag appliquée avec succès pour {r_col} avec pas {parameter_value}")
                time.sleep(1)
                st.rerun()
            st.write("---")  # Separator between transformation sections



            ###### CROISSANCE
            st.write("##### Appliquation d'une croissance")
            selected_column_int = st.multiselect("Sélectionner des colonnes :", columns, key=f'col_croissance{i}')
            selected_growth = st.selectbox('Choisir type de croissance:', ['', 'Relative', 'Logarithmique'], key = f"growth_{i}")
            parameter_value_growth = st.slider("Sélectionner un paramètre $k$ (1 à 12) :", 1, 12, key = f'growth_param{i}')
            if selected_growth == 'Relative':
                st.write("Vous êtez en train d'appliquer l'opération suivante:")
                st.markdown(r'$$\texttt{Transformation}(\text{Colonne})_t = \dfrac{\text{Colonne}_t - \text{Colonne}_{t-k}}{\text{Colonne}_{t-k}}$$')
            if selected_growth == 'Logarithmique':
                st.write("Vous êtez en train d'appliquer l'opération suivante:")
                st.markdown(r'$$\texttt{Transformation}(\text{Colonne})_t =\ln\bigg( \dfrac{\text{Colonne}_t }{\text{Colonne}_{t-k}}\bigg)$$')
            check_inplace = st.checkbox('Remplacer colonne par sa tranformée', key=f'check_croissance{i}')
            if st.button("Appliquer la transformation", key=f'but_croissance{i}'):
                if 'TOUT' in selected_column_int:
                    for j in range(len(st.session_state.queue[i].columns)):
                        t = str(st.session_state.queue[i][st.session_state.queue[i].columns[j]].dtype)
                        r_col = st.session_state.queue[i].columns[j]
                        if ('int' not in t and 'float' not in t):
                            continue
                        else:
                            if selected_growth == 'Relative':
                                output =  st.session_state.queue[i][r_col].pct_change(periods=parameter_value_growth)
                            if selected_growth == 'Logarithmique':
                                output = np.log(
                                    st.session_state.queue[i][r_col] / st.session_state.queue[i][
                                        r_col].shift(parameter_value_growth))
                            if check_inplace:
                                st.session_state.queue[i][r_col] = output
                            else:
                                st.session_state.queue[i][f"(T) / {r_col} / CROISSANCE_{selected_growth}_{parameter_value_growth}"] = output
                    st.success(f"Croissance appliquée avec succès pour tout le fichier de type {selected_growth} et de paramètre {parameter_value_growth}")
                else:
                    for j in selected_column_int:
                        index = int(j.split('-')[0].strip())
                        r_col = st.session_state.queue[i].columns[index]
                        if selected_growth == 'Relative':
                            output = st.session_state.queue[i][r_col].pct_change(periods=parameter_value_growth)
                        if selected_growth == 'Logarithmique':
                            output = np.log(
                                st.session_state.queue[i][r_col] / st.session_state.queue[i][
                                    r_col].shift(parameter_value_growth))
                        if check_inplace:
                            st.session_state.queue[i][r_col] = output
                        else:
                            st.session_state.queue[i][f"(T) / {r_col} / CROISSANCE_{selected_growth}_{parameter_value_growth}"] = output
                        st.success(f"Croissance appliquée avec succès pour {r_col} de type {selected_growth} et de paramètre {parameter_value_growth}")
                time.sleep(1)

        ####### ONGLET - TSA
        with st.expander('Analyse de séries temporelles'):
            st.write("##### Approximation polynômiale de tendance")
            columns = st.session_state.queue[i].columns[1:]
            selected_column_prox = st.selectbox("Sélectionner une colonne :", columns, key=f'approx_pol{i}')

            # Slider for parameter selection (1 to 12)
            parameter_value_pol = st.slider("Choisir degré de polynôme (0 à 2) :", 0, 2, key=f'param_pol{i}')
            # Button to apply transformation
            if st.button("Chercher polynome", key=f'poly_app{i}'):
                to_transform = pd.DataFrame(st.session_state.queue[i][selected_column_prox])
                to_transform =to_transform.reset_index()
                transformed_data = utils_extraction_TS.extract_trend_OLS(to_transform,parameter_value_pol)
                transformed_data[0].index = st.session_state.queue[i].index
                st.session_state.queue[i][f"(AST) / {selected_column_prox} / POLYNOME_{parameter_value_pol}_TENDANCE"] = transformed_data[0]
                st.write(f'Polynôme de degré {parameter_value_pol} qui approche au mieux la tendance:')
                if parameter_value_pol == 0:
                    poly_expr=f"$${transformed_data[1][0]}$$"
                elif parameter_value_pol == 1:
                    poly_expr = f"$${transformed_data[1][0]} + ({transformed_data[1][1]})\cdot (t-t_0)$$"
                else:
                    poly_expr = f"$${transformed_data[1][0]} + ({transformed_data[1][1]})\cdot (t-t_0) + ({transformed_data[1][2]})\cdot (t-t_0)^2 $$"
                st.markdown(poly_expr)
                st.success("Polynôme d'interpolation est ajouté au colonnes du fichier original")

            st.write("---")
            st.write("##### Extraction de tendance")
            columns = st.session_state.queue[i].columns[1:]
            selected_column_trend = st.selectbox("Sélectionner une colonne :", columns, key=f'trend{i}')
            parameter_value_trend_freq = st.slider("Choisir période (fréquence sur base de temps de fichier):", 1, 24, key=f'trend_freq{i}')

          # Button to apply transformation
            if st.button("Extraire", key=f'tend{i}'):
                to_transform = st.session_state.queue[i][selected_column_trend]
                to_transform = to_transform.reset_index()
                to_transform= to_transform.dropna()
                transformed_data = utils_extraction_TS.tendance(to_transform, parameter_value_trend_freq)
                transformed_data.index = to_transform[to_transform.columns[0]]
                st.session_state.queue[i][f"(AST) / {selected_column_trend} / ACTUEL_TENDANCE{parameter_value_trend_freq}"] = transformed_data
                st.success("Tendance bien ajoutée")


            st.write("---")
            st.write("##### Extraction de saisonalité")
            columns = st.session_state.queue[i].columns[1:]
            selected_column_seas = st.selectbox("Sélectionner une colonne :", columns, key=f'season{i}')
            parameter_value_seas_freq = st.slider("Choisir période (fréquence sur base de temps de fichier):", 1, 24,
                                                  key=f'season_freq{i}')

            # Button to apply transformationa
            if st.button("Extraire", key=f'seas{i}'):
                to_transform = st.session_state.queue[i][selected_column_seas]
                to_transform = to_transform.reset_index()
                to_transform = to_transform.dropna()
                transformed_data = utils_extraction_TS.saisonnalite(to_transform, parameter_value_seas_freq)
                transformed_data.index = to_transform[to_transform.columns[0]]
                st.session_state.queue[i][
                    f"(AST) / {selected_column_seas} / ACTUEL_SEASONALITE{parameter_value_seas_freq}"] = transformed_data
                st.success("Seasonalité bien ajoutée")
            st.write("---")

            st.write("##### Extraction de résidus")
            columns = st.session_state.queue[i].columns[1:]
            selected_column_res= st.selectbox("Sélectionner une colonne :", columns, key=f'res_c{i}')
            parameter_value_res_freq = st.slider("Choisir période (fréquence sur base de temps de fichier):", 1, 24,
                                                  key=f'res_freq{i}')

            # Button to apply transformation
            if st.button("Extraire", key=f'res{i}'):
                to_transform = st.session_state.queue[i][selected_column_res]
                to_transform = to_transform.reset_index()
                to_transform = to_transform.dropna()
                transformed_data = utils_extraction_TS.residus(to_transform, parameter_value_res_freq)
                transformed_data.index = to_transform[to_transform.columns[0]]
                st.session_state.queue[i][
                    f"(AST) / {selected_column_res} / ACTUEL_RESIDUS{parameter_value_res_freq}"] = transformed_data
                st.success("Résidu bien ajoutée")

else:
    st.error("Aucun fichier importé.")
