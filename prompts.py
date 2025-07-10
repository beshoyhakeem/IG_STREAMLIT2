from config import *
from utils import *

daf, index = check_data()

    # Step 1: Analyze query and determine search strategy
analysis_prompt = f"""
    You're an influencer marketing analyst at 6Degrees. Given this request:
    "{user_query}"
    
    Available metadata columns: {list(daf.columns)}
    
    Decide the search strategy:
    1. If the user wants influencers by content category (e.g., travel, fashion), use semantic search on 'combined_categories'
    2. If they specify metadata filters (followers range, country, etc.), generate a pandas query
    3. If both are needed, do semantic search first then apply filters
    
    Return JSON with:
    {{
        "use_semantic_search": boolean,
        "search_terms": "terms for semantic search",
        "pandas_query": "query string or null",
        "display_columns": ["relevant", "columns"]
    }}
    """



    # Step 3: Generate response
response_prompt = f"""
    User request: {user_query}
    
    Search strategy used:
    - Semantic search: {use_semantic} ({search_terms})
    - Pandas query: {pandas_query or 'None'}
    
    Top {min(5, len(results))} influencers:
    {results[display_cols].head(5).to_string()}
    
    You are an influencer marketing analyst at 6Degrees. Given a list of influencer profiles and campaign criteria, do the following:

    1-Score each influencer from 0 to 100 based on relevance.
    2-Provide a short explanation of the score
    3-Select the top 10 most relevant influencers

    Scoring Criteria:

    1-Follower count (relative to campaign target)
    2-Platform match
    3-Engagement rate
    4-Content category alignment
    
    Then
    Output Format (JSON array of top 10)
    json
    CopyEdit
    [

        "ig_handle": "@sophie.travel",
        "score": 92,
        "explanation": "Sophie is a great fit: strong US audience (85%), high engagement, and a perfect travel category match."
 
    ...
    ]

    Then Ask the user for two things:

    First, You are an outreach strategist working with 6Degrees. For each influencer provided (with their IG handle and campaign info), generate a personalized outreach message that:
    
    1- Mentions their name and IG category
    2-References a detail or theme (e.g., recent trip, content style)
    3-Introduces the brand and campaign
    4-Ends with a friendly CTA

    Tone: Friendly, personal, professional — not robotic or corporate.

    If he wants the outreach:

    Output Format (per influencer)
    json
    CopyEdit

    "ig_handle": "@sophie.travel",
    "score": 92,
    "explanation": "Sophie is a great fit: strong US audience (85%), high engagement, and a perfect travel category match.",
    "outreach_message": "Hey Sophie! 👋 I love your travel content — your Iceland trip was amazing! I’m reaching out from 6Degrees for Nomad Gear Co. We’re launching a new summer line and think you’d be a great fit. We’re looking for a post + story in July. Let me know if you're open to collab!"


    Second:
    Combine Into Downloadable File
    File Output Structure (CSV)
    Each row should include:
    IG Handle  Relevance Score  Score Explanation  Personalized Message

    CSV Example
    csv
    CopyEdit
    IG Handle,Relevance Score,Explanation,Outreach Message
    @sophie.travel,92,"Sophie is a great fit: strong US audience (85%), high engagement, and a perfect travel category match.","Hey Sophie! 👋 I love your travel content — your Iceland trip was amazing! I’m reaching out from 6Degrees for Nomad Gear Co. We’re launching a new summer line and think you’d be a great fit. We’re looking for a post + story in July. Let me know if you're open to collab!"

    """