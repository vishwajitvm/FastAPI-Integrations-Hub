from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_documents_by_section(docs, user_id=None):
    all_chunks = []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " "]
    )

    for doc in docs:
        text = doc.page_content
        metadata = doc.metadata.copy()
        if user_id:
            metadata["user_id"] = user_id

        chunks = splitter.split_text(text)

        for chunk in chunks:
            all_chunks.append(Document(page_content=chunk, metadata=metadata))

    print(f"🧠 Total chunks created: {len(all_chunks)}")
    return all_chunks
