from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# 1. Using same embedding that was used for embedding chunks
client = OpenAI()
embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")

# 2. Create db connection
vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="rag-embeddings",
    embedding=embedding_model,
)

# .3 Take the user query
user_query = input(f"⌨️: Ask me.. ")

# 4. Embed the user_query and use it to do similarity search in vector db
search_result = vector_db.similarity_search(query=user_query)
context = "\n\n\n".join(
    [
        f"""page_content:{result.page_content}\n 
                        page_num:{result.metadata['page_label']}\n
file_location: {result.metadata['source']}
"""
        for result in search_result
    ]
)

# 5. Make system promt out of search result
SYSTEM_PROMPT = f"""
You are an assistant who solves user queries based on available context got from
a pdf file along with page content, number and details. Use only available context and 
guide the user with document
Context: {context}
"""
response = client.chat.completions.create(
    model="gpt-5",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ],
)

chat_resp = response.choices[0].message.content
print(f'🤖: {chat_resp}')