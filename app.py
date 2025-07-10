from logic import *
from utils import *
import streamlit as st

st.title('AI-Powered Influencers Finder')

with st.chat_message('assistant'):
    st.write('Hey 👋 lets explore new Influencers')

if "messages" not in st.session_state:
    st.session_state.messages= []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])   

if Niche_query := st.chat_input("input Niche Required"):
    with st.chat_message("user"):
        st.markdown(Niche_query)
    st.session_state.messages.append({"role":"user", "content": Niche_query})

    
with st.chat_message("AI"):
    results = RAG_GPT(Niche_query,analysis_prompt,response_prompt ,default_strategy)
    
    st.session_state.messages.append({"role":"AI","content":results })

          


