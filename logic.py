from Azure_openai import *
from config import *
from utils import *
import ast

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
    1. If the user specified campaign requriments (e.g., medicine, fitness) or influencers by content category (e.g., travel, fashion), And generate search terms depending on user's request, use semantic search on 'combined_categories'
    2. If the user specify metadata filters (followers range, country, etc.), generate a pandas query
    3. If both are needed, do semantic search first then apply filters
    
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
    {results[display_cols].head(100).to_string()}
    
    You are an influencer marketing analyst at 6Degrees. Given a list of influencer profiles and campaign criteria

    List the influencers that the user asked for and with the details that the user wants, but always mention their name, Instagram ID, YouTube ID, IG category And email

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


def csv_out (mod_res):

    csv_prompt = f""" 
    {mod_res}
    Given this response from a model take the users in the response and their emails and the Personalized email for each user 
    your job is to put them in two lists 'emails', 'Personalized_Email' and both in a dict E_P

    like this example

    E_P = {{'emails':['email_for_user_1', 'email_for_user_2','email_for_other_users',...],
            
            'Personalized_Email': ['Personalized_Email_for_user1', 'Personalized_Email_for_user2','Personalized_Email_for_other_users',...]
            }}

    the output is E_P dict and assigned lists 'emails' and 'Personalized_Email' only nothing more or less no other data ONLY THE Dictionary
    """

    chat_response = chat_client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": csv_prompt}],
        temperature=0.1
    )
    response_csv = chat_response.choices[0].message.content

    dict_part = response_csv.split('=', 1)[1].strip()

    # Convert to actual dictionary
    pp = ast.literal_eval(dict_part)

    email_s = pp['emails']
    personalized_emails = pp['Personalized_Email']

    emails = pd.DataFrame(columns=['Email','Personalized Email'])

    emails['Email'] = email_s
    emails['Personalized Email'] = personalized_emails

    

    return emails


  


    


    



        



