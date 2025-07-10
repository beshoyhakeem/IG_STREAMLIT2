import numpy as np
import pandas as pd
import faiss
import json
from IPython.display import Markdown

DATA_PATH = 'C:/Users/besho/Desktop/IG-PROJECT/RAG_streamlit/RAG_streamlit/gpt_rag.csv'
FAISS_PATH = "C:/Users/besho/Desktop/IG-PROJECT/RAG_streamlit/RAG_streamlit/cosine_sim_index.faiss"

def check_data():
    global daf, index

    if 'daf' not in globals() or daf.empty:
        print("metadata is not loaded")
        daf = pd.read_csv(DATA_PATH)
        print("metadata loaded")
    else:
        print("metadata already loaded")

    if'index' not in globals() or index.ntotal == 0:
        print("Faiss Index not loaded")
        index = faiss.read_index(FAISS_PATH)
        print("Index loaded") 
    else:
        print("Index already loaded")
    
    return daf, index
    
