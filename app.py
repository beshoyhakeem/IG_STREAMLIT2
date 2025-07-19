from logic import *
import streamlit as st


st.title('AI-Powered Influencers Finder')

if "messages" not in st.session_state:
    st.session_state.messages= []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])   

st.session_state.response_shown = False

if Niche_query := st.chat_input("Campaign Requirements"):
    st.session_state.messages.append({"role":"user", "content": Niche_query})
    with st.chat_message("user"):
        st.markdown(Niche_query)

    st.session_state.results = RAG_GPT(Niche_query,default_strategy)    
            
    with st.chat_message("AI"):
        st.markdown(st.session_state.results["response"])
        st.markdown(st.session_state.results["strategy"])
    

    st.session_state.messages.append({"role":"AI","content":st.session_state.results["response"]})
    st.session_state.response_shown = True  # Show the button from now on



          


