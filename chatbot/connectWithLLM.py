from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import os

def get_rag_answer(query):
    response = qaChain.invoke({'query': query})
    formatted_answer = response["result"]
    formatted_sources = []
    for doc in response["source_documents"]:
        source = doc.metadata.get('source', 'Unknown source')
        page = doc.metadata.get('page_label', '?')
        formatted_sources.append(f"📄 {os.path.basename(source)} (page {page})")
    return {
        "answer": formatted_answer,
        "sources": formatted_sources
    }


# Loading... embedding and FAISS DB
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
DB_FAISS_PATH = "./chatbot/vectorstore/db_faiss"
db = FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)

# Loading.. LLaMA Model
llm = OllamaLLM(model="llama3:8b", temperature=0.5)

# Prompt
prompt = """
Use the pieces of information provided in the context to answer user's question.
If you dont know the answer, just say that Sorry, I don't have any knowledge related to this.
Don't provide anything out of the given context.

Context: {context}
Question: {question}

Start the answer directly. No small talk please.
"""

def set_custom_prompt(prompt_text):
    return PromptTemplate(template=prompt_text, input_variables=["context", "question"])

# Create QA chain
qaChain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=db.as_retriever(search_kwargs={"k": 3}),
    return_source_documents=True,
    chain_type_kwargs={"prompt": set_custom_prompt(prompt)}
)

# Querying
if __name__ == "__main__":
    user_query = input("Write your Query here: ")
    response = qaChain.invoke({"query": user_query})

    # Format and print the response
    formatted_answer = response["result"].replace("\n", "<br>")
    formatted_sources = []
    for doc in response["source_documents"]:
        metadata = doc.metadata
        source_info = f"📄 <b>{os.path.basename(metadata.get('source', ''))}</b> (page {metadata.get('page_label', '?')})"
        formatted_sources.append(source_info)

    final_response = {
        "answer": formatted_answer,
        "sources": formatted_sources
    }
    print(final_response)
