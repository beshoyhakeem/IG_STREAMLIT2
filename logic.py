from Azure_openai import *
from config import *
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


def RAG_GPT(user_query, default_strategy):

    strategy = default_strategy

    
        # Step 1: Analyze query and determine search strategy
    analysis_prompt = f"""
    You're an influencer marketing analyst at 6Degrees. Given this request:
    "{user_query}"
    
    Available metadata columns: {list(daf.columns)}
    
    Decide the search strategy:
    1. If the user wants influencers by content category (e.g., travel, fashion), use semantic search on 'combined_categories'
    2. If they specify metadata filters (followers range, country, etc.), generate a pandas query
    3. If both are needed, do semantic search first then apply filters

    And Always return 'emails' column in pandas query even if the user didn't ask for email 
    
    Return JSON with:
    {{
        "use_semantic_search": boolean,
        "search_terms": "terms for semantic search",
        "pandas_query": "query string or null",
        "display_columns": ["relevant", "columns"]
    }}
    """

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
            try:
                # Apply metadata filters
                results = results.query(pandas_query, engine='python')
            except Exception as e:
                    print(f"Query error: {e}")
    else:
        # Pure metadata filtering
        if pandas_query:
            try:
                results = daf.query(pandas_query, engine='python')
            except:
                    results = daf.head(10)  # Fallback
        else:
            results = daf.head(10)

    # If no results found, return some fallback results
    if len(results) == 0:
        results = daf.head(5)

    response_prompt = f"""
    User request: {user_query}
    
    Search strategy used:
    - Semantic search: {use_semantic} ({search_terms})
    - Pandas query: {pandas_query or 'None'}
    
    Top {min(5, len(results))} influencers:
    {results[display_cols].head(10).to_string()}
    
    You are an influencer marketing analyst at 6Degrees. Given a list of influencer profiles and campaign criteria, do the following:

    1-Score each influencer from 0 to 100 based on relevance.
    2-Provide a short explanation of the score
    3-Select the top 10 most relevant influencers

    Scoring Criteria:

    1-Follower count (relative to campaign target)
    2-Platform match
    3-Engagement rate
    4-Content category alignment
    
    Then write a personlized email for each one required*

    1- Mentions their name , IG category And email 
    2-References a detail or theme (e.g., recent trip, content style)
    3-Introduces the brand and campaign
    4-Ends with a friendly CTA

    Tone: Friendly, personal, professional — not robotic or corporate.
    """

    chat_response = chat_client.chat.completions.create(
    model="chatgpt-4o-latest",
    messages=[{"role": "user", "content": response_prompt}],
    temperature=0.5
    )
    response_text = chat_response.choices[0].message.content
    #response_text = "I found some influencers matching your criteria:\n" + results[display_cols].head(5).to_string()
    
    return {
        "response": response_text,
        "data": results.head(5).to_dict('records'),
        "strategy": strategy
    }





  


    


    



        



