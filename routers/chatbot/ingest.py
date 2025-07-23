from app.ingestion.ingest_common import ingest_common_pdfs_from_local

def main():
    folder_path ="routers/chatbot/Docs"
    print(f"📁 Starting ingestion from: {folder_path}")
    result = ingest_common_pdfs_from_local(folder_path)
    print(result)

if __name__ == "__main__":
    main()