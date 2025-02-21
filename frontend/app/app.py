import rag_system
import streamlit as st
import user_management

st.set_page_config(page_title="Simple App", layout="wide")

tabs = st.tabs(["Rag System", "User Management"])

with tabs[0]:
    rag_system.show("user_action_1")


with tabs[1]:
    user_management.show("user_action_2")
