from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv

load_dotenv()

#1. Load the data source
pdf_path = Path(__file__).parent/'all.pdf'
loader = PyPDFLoader(file_path=pdf_path)
docs = loader.load()

#2. Chunk and split the data
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=400)
chunks = text_splitter.split_documents(documents=docs)

#3. Create and store embedding for every chunks in to vector DB qdRant
embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")

#4. Store embedding to vector store
vector_store = QdrantVectorStore.from_documents(
    documents = docs,
    embedding = embedding_model,
    url = 'http://localhost:6333',
    collection_name = 'rag-embeddings'
)
