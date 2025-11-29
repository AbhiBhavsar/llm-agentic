
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

client = OpenAI()
embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")

# 2. Create db connection
vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="rag-embeddings",
    embedding=embedding_model,
)


def process_query(query: str):
    print("Searching chunks...\n\n", query)
    search_result = vector_db.similarity_search(query=query)
    context = "\n\n\n".join(
        [
            f"""page_content:{result.page_content}\n 
                        page_num:{result.metadata['page_label']}\n
                        file_location: {result.metadata['source']}"""
            for result in search_result
        ]
    )

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
            {"role": "user", "content": query},
        ],
    )

    chat_resp = response.choices[0].message.content
    return chat_resp
