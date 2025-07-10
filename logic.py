from Azure_openai import *
from prompts import *
from utils import *


daf, index = check_data()



# Embed user Query
def get_embedding(text, model="text-embedding-3-small"):  # Use your Azure deployment name
    response = embed_client.embeddings.create(
        input=text,
        model=model
    )
    return response.data[0].embedding


# Embed Query and Search for users 
def search(query_text, top_k=5):
    # Step 1: Embed the query using the same Azure OpenAI model
    query_embedding = np.array([get_embedding(query_text)]).astype('float32')
    faiss.normalize_L2(query_embedding)  # Normalize query for cosine similarity
    
    # Step 2: Search the FAISS index
    distances, indices = index.search(query_embedding, top_k)
    
    # Step 3: Return matching rows from the DataFrame
    results = daf.iloc[indices[0]].copy()
    results['cosine_similarity'] = distances[0]  # Higher = more similar
    return results


def RAG_GPT(user_query,analysis_prompt,response_prompt ,default_strategy):

    strategy = default_strategy

    # Get strategy from GPT-4
    analysis_response = chat_client.chat.completions.create(
        model="chatgpt-4o-latest",
        messages=[{"role": "user", "content": analysis_prompt}],
        temperature=0.0,
        response_format={"type": "json_object"}
        )
    
    strategy = json.loads(analysis_response.choices[0].message.content)

    # Extract parameters from strategy
    use_semantic = strategy.get("use_semantic_search", True)
    search_terms = strategy.get("search_terms", user_query)
    pandas_query = strategy.get("pandas_query")
    display_cols = strategy.get("display_columns", ["Name", "combined_categories"])


    # Step 2: Execute search strategy
    if use_semantic:
        # Semantic search with embeddings
        results = search(search_terms, top_k=50)
        if pandas_query:
            # Apply metadata filters
            results = results.query(pandas_query, engine='python')

    else:
        # Pure metadata filtering
        if pandas_query:

            results = daf.query(pandas_query, engine='python')

        else:
            results = daf.head(10)

    # If no results found, return some fallback results
    if len(results) == 0:
        results = daf.head(5)

    chat_response = chat_client.chat.completions.create(
    model="chatgpt-4o-latest",
    messages=[{"role": "user", "content": response_prompt}],
    temperature=0.5
    )
    response_text = chat_response.choices[0].message.content
    response_text = "I found some influencers matching your criteria:\n" + results[display_cols].head(5).to_string()
    
    return {
        "response": response_text,
    }





  


    


    



        



