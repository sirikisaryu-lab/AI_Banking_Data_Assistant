import os
from typing import List, Optional

from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from llm.llm_client import chat_completion


# ----------------------------
# Load PDFs from Folder
# ----------------------------
def load_pdfs_from_folder(folder_path: str) -> List[Document]:
    documents = []

    if not os.path.exists(folder_path):
        raise ValueError(f"Folder not found: {folder_path}")

    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)

            reader = PdfReader(file_path)
            content = ""

            for page in reader.pages:
                content += page.extract_text() or ""

            if content.strip():
                documents.append(
                    Document(
                        page_content=content,
                        metadata={"source": filename}
                    )
                )

    return documents


# ----------------------------
# Chunking
# ----------------------------
def chunk_documents(
    documents: List[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> List[Document]:

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    return splitter.split_documents(documents)


# ----------------------------
# RAG Engine
# ----------------------------
class RAGEngine:

    def __init__(
        self,
        documents_path: str = "documents",
        index_path: str = "faiss_index",
    ):
        self.documents_path = documents_path
        self.index_path = index_path
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore: Optional[FAISS] = None

        self._initialize_vectorstore()

    # ----------------------------
    # Initialize / Load / Auto-Index
    # ----------------------------
    def _initialize_vectorstore(self):
        if os.path.exists(self.index_path):
            try:
                self.vectorstore = FAISS.load_local(
                    self.index_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True,
                )
                print("✅ Loaded existing FAISS index.")
                return
            except Exception:
                print("⚠ Failed to load index. Rebuilding...")

        print("🔄 Creating new FAISS index...")
        self.index_folder(self.documents_path)

    # ----------------------------
    # Indexing
    # ----------------------------
    def index_folder(self, folder_path: str):
        documents = load_pdfs_from_folder(folder_path)

        if not documents:
            raise ValueError("No valid PDF documents found to index.")

        chunks = chunk_documents(documents)

        self.vectorstore = FAISS.from_documents(chunks, self.embeddings)
        self.vectorstore.save_local(self.index_path)

        print("✅ PDF documents indexed and saved successfully.")

    # ----------------------------
    # Retrieval
    # ----------------------------
    def retrieve(self, query: str, k: int = 2) -> str:
        if self.vectorstore is None:
            raise ValueError("Vectorstore not initialized.")

        docs = self.vectorstore.similarity_search(query, k=k)

        return "\n\n".join(
            [f"Source: {doc.metadata.get('source')}\n{doc.page_content}" for doc in docs]
        )

    # ----------------------------
    # Answer
    # ----------------------------
    def answer(self, query: str) -> str:
        # Retrieve relevant context from the vectorstore
        return self.retrieve(query)