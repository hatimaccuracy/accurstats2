import streamlit as st
import sys
sys.path.append('../')
sys.path.append('../../')
sys.path.append('../../../')
st.set_page_config(
    page_title= "AccurStats - Bienvenue",
    page_icon = 'A'
)
st.title('Bienvenue à AccurStats')
st.write("Ceci est une description sympathique d'AccurStats.")
st.write("Pour commencer, cliquer sur importation.")
if st.session_state.queue_names:
    st.sidebar.header("Fichiers Exportés")
    for filename in st.session_state.queue_names:
        st.sidebar.write(filename)
else:
    st.sidebar.write("Aucun fichier exporté.")