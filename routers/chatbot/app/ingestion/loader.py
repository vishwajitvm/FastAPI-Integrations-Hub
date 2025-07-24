import os
from langchain_community.document_loaders import PyPDFLoader

def load_documents_from_local(folder_path):
    docs = []
    print(f"📁 Starting ingestion from: {folder_path}")
    
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            path = os.path.join(folder_path, filename)
            print(f"📄 Loading PDF: {filename}")
            try:
                loader = PyPDFLoader(path)
                file_docs = loader.load()  # Loads by page
                print(f"✅ Loaded {len(file_docs)} pages")

                for doc in file_docs:
                    doc.metadata.update({"source": "admin", "filename": filename})
                docs.extend(file_docs)
            except Exception as e:
                print(f"❌ Failed to load {filename}: {e}")
    return docs
