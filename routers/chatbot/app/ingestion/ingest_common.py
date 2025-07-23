from .loader import load_documents_from_local
from .chunker import chunk_documents_by_section
from ..db.vectorstore import get_vectorstore

def ingest_common_pdfs_from_local(folder_path):
    docs = load_documents_from_local(folder_path)
    chunks = chunk_documents_by_section(docs)
    vectorstore = get_vectorstore()
    vectorstore.add_documents(chunks)
    return {
        "message": f"Ingested {len(docs)} documents and {len(chunks)} chunks from public PDFs."
    }
