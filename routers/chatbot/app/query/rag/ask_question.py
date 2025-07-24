# ask_question.py
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from config import Config
from ...db.vectorstore import get_vectorstore  # 🧠 Shared vectorstore from ingestion module

def ask_question(query: str, user_id: str) -> dict:
    print(f"\n Received query: {query}")
    print(f" User ID: {user_id}")

    vectorstore = get_vectorstore()
    print("Vectorstore initialized.")

    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
    print("Retriever created with top-k = 5")

    is_summary = any(word in query.lower() for word in ["summarize", "summary", "explain", "overview"])
    print(f"Summary intent detected: {is_summary}")

    prompt_template = None
    if is_summary:
        prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""
                You are an expert at making complex information easy to understand.
                Summarize the following content in a clear, simple, and engaging way,
                as if explaining to a beginner.

                Context:
                {context}

                User request:
                {question}

                Answer:
            """
        )
        print("Custom summarization prompt template created.")

    llm = ChatGoogleGenerativeAI(
        google_api_key=Config.GOOGLE_API_KEY,
        model=Config.LLM_MODEL
    )
    print(f"Gemini LLM initialized with model: {Config.LLM_MODEL}")

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt_template} if prompt_template else {}
    )
    print("RetrievalQA chain constructed.")

    result = qa_chain.invoke(query)
    print("QA chain invoked successfully.")
    print(f"Answer: {result['result']}")

    source_docs = result["source_documents"]
    print(f"Retrieved {len(source_docs)} documents.")

    # 🧠 Join top context chunks for agent context
    source_text = "\n\n".join([doc.page_content for doc in source_docs])
    print("Assembled context from source documents.")

    return {
        "context": source_text,
        "result": result["result"],
        "source_documents": [doc.metadata for doc in source_docs]
    }




# ##### CACHE CODE
# ask_question.py
# from langchain.chains import RetrievalQA
# from langchain.prompts import PromptTemplate
# from langchain_google_genai import ChatGoogleGenerativeAI
# from config import Config
# from ...db.vectorstore import get_vectorstore, get_chat_cache_vectorstore # 🧠 Shared vectorstores
# from datetime import datetime

# CACHE_TOP_K = 3
# CACHE_SCORE_THRESHOLD = 0.88


# def ask_question(query: str, user_id: str) -> dict:
#     print(f"\n Received query: {query}")
#     print(f" User ID: {user_id}")

#     # 1. Try Cache First ----------------------------------
#     cache_vs = get_chat_cache_vectorstore()
#     print("Checking cache vectorstore...")

#     cache_results = cache_vs.similarity_search_with_score(query, k=CACHE_TOP_K)

#     for doc, score in cache_results:
#         print(f"🔍 Cache score: {score:.4f} for cached doc.")
#         if score >= CACHE_SCORE_THRESHOLD and doc.metadata.get("user_id") == user_id:
#             print("✅ Cache hit! Returning cached result.")
#             return {
#                 "context": doc.metadata.get("context", ""),
#                 "result": doc.metadata.get("answer", ""),
#                 "source_documents": [doc.metadata]
#             }

#     print("❌ No valid cache hit. Proceeding with RAG...")

#     # 2. Initialize RAG ----------------------------------
#     vectorstore = get_vectorstore()
#     print("Vectorstore initialized.")

#     retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
#     print("Retriever created with top-k = 5")

#     is_summary = any(word in query.lower() for word in ["summarize", "summary", "explain", "overview"])
#     print(f"Summary intent detected: {is_summary}")

#     prompt_template = None
#     if is_summary:
#         prompt_template = PromptTemplate(
#             input_variables=["context", "question"],
#             template="""
#                 You are an expert at making complex information easy to understand.
#                 Summarize the following content in a clear, simple, and engaging way,
#                 as if explaining to a beginner.

#                 Context:
#                 {context}

#                 User request:
#                 {question}

#                 Answer:
#             """
#         )
#         print("Custom summarization prompt template created.")

#     llm = ChatGoogleGenerativeAI(
#         google_api_key=Config.GOOGLE_API_KEY,
#         model=Config.LLM_MODEL
#     )
#     print(f"Gemini LLM initialized with model: {Config.LLM_MODEL}")

#     qa_chain = RetrievalQA.from_chain_type(
#         llm=llm,
#         retriever=retriever,
#         return_source_documents=True,
#         chain_type_kwargs={"prompt": prompt_template} if prompt_template else {}
#     )
#     print("RetrievalQA chain constructed.")

#     result = qa_chain.invoke(query)
#     print("QA chain invoked successfully.")
#     print(f"Answer: {result['result']}")

#     source_docs = result["source_documents"]
#     print(f"Retrieved {len(source_docs)} documents.")

#     # 🧠 Join top context chunks for agent context
#     source_text = "\n\n".join([doc.page_content for doc in source_docs])
#     print("Assembled context from source documents.")

#     # 3. Save into Cache ----------------------------------
#     print("Saving result to cache vectorstore...")
#     cache_vs.add_texts(
#         texts=[query + "\n\n" + result["result"]],
#         metadatas=[{
#             "user_id": user_id,
#             "query": query,
#             "answer": result["result"],
#             "context": source_text,
#             "timestamp": datetime.now().isoformat()
#         }]
#     )
#     print("✅ Saved in cache.")

#     return {
#         "context": source_text,
#         "result": result["result"],
#         "source_documents": [doc.metadata for doc in source_docs]
#     }
