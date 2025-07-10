from logic import *
import streamlit as st


st.title('AI-Powered Influencers Finder')

if "messages" not in st.session_state:
    st.session_state.messages= []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])   


if Niche_query := st.chat_input("Campaign Requirements"):
    st.session_state.messages.append({"role":"user", "content": Niche_query})
    with st.chat_message("user"):
        st.markdown(Niche_query)

    results = RAG_GPT(Niche_query,default_strategy)    
            
    with st.chat_message("AI"):
        st.markdown(results["response"])
        st.markdown(results["strategy"])
    

    st.session_state.messages.append({"role":"AI","content":results["response"]})


          


