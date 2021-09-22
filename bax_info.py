import streamlit as st
import const as cn

class App:
    """
    """

    def __init__(self, texts: dict):
        self.texts = texts


    def show_info(self):
        st.markdown(self.texts['intro'])


    def show_menu(self):
        self.show_info()
        
    