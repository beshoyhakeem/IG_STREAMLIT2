import pandas as pd



use_semantic = True
user_query = ""
search_terms = ""
pandas_query = None
display_cols = []
results = pd.DataFrame()

default_strategy = {
        "use_semantic_search": True,
        "search_terms": user_query,
        "pandas_query": None,
        "display_columns": ["Name", "combined_categories"]
    }

