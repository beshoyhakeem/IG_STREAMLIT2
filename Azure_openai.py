from openai import AzureOpenAI

model_name = "text-embedding-3-small"

embed_client = AzureOpenAI(
    api_key="dFix9cCVoEU8z5qk49mmMRTdpZG4nouTgcg31Ich5Mv6JY9YolmdJQQJ99BFACfhMk5XJ3w3AAABACOGBgrn",
    api_version="2024-12-01-preview",
    azure_deployment = "text-embedding-3-small",
    azure_endpoint="https://ragaopen2.openai.azure.com/openai/deployments/text-embedding-3-small/embeddings?api-version=2023-05-15"
)

chat_client = AzureOpenAI(
    api_key="dFix9cCVoEU8z5qk49mmMRTdpZG4nouTgcg31Ich5Mv6JY9YolmdJQQJ99BFACfhMk5XJ3w3AAABACOGBgrn",
    api_version="2025-01-01-preview",
    azure_deployment = "gpt-4.1",
    azure_endpoint="https://ragaopen2.openai.azure.com/openai/deployments/gpt-4.1/chat/completions?api-version=2025-01-01-preview"
)