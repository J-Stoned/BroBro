from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
loader = PyPDFLoader("large_document.pdf")
pages = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(pages)
for i, chunk in enumerate(chunks):
    print(f"Chunk {i}: {chunk.page_content[:100]}...")
