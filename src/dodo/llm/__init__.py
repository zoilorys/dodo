from langchain_ollama import ChatOllama, OllamaEmbeddings

# LLM_MODEL='llama3.2:3b-instruct-fp16'
# LLM_MODEL='gemma2'
# LLM_MODEL = 'phi3.5'
LLM_MODEL = 'mistral-nemo'

EMBEDDING_MODEL = 'nomic-embed-text'
EMBEDDING_CHUNK_SIZE = 525
EMBEDDING_CHUNK_OVERLAP = 150

chat_llm = ChatOllama(model=LLM_MODEL, temperature=0)
embeddings_llm = OllamaEmbeddings(model=EMBEDDING_MODEL)

