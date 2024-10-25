import os
import sys
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.vectorstores.chroma import Chroma
from dotenv import load_dotenv
import chromadb
import streamlit

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from model.data_ingestion import ingest_data

# Load environment variables
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

# Setup paths
data_directory = os.path.join(ROOT_DIR, "ingestion/data_sources")
persist_directory = os.path.join(ROOT_DIR, "db/")

if not os.path.exists(persist_directory):
    print(f"Directory {persist_directory} does not exist. Creating it.")
    os.makedirs(persist_directory)

# Initialize embeddings and Chroma
embeddings = OpenAIEmbeddings(api_key=openai_api_key)

# Check if persist_directory is empty
if not os.listdir(persist_directory):
    print(f"The directory {persist_directory} is empty. Ingesting data...")
    # Initialize Chroma DB if directory is empty
    persistent_client = chromadb.PersistentClient()
    collection = persistent_client.get_or_create_collection("Text2SQL_Papers")
    db = Chroma(collection_name="Text2SQL_Papers", persist_directory=persist_directory,
                embedding_function=embeddings)

    # Ingest data into the DB
    ingest_data(data_directory, db)
else:
    print(f"The directory {persist_directory} is not empty. Loading existing data...")
    # Initialize Chroma DB using existing data
    db = Chroma(collection_name="Text2SQL_Papers", persist_directory=persist_directory,
                embedding_function=embeddings)

# Check collection count
print("Collection count:", db._collection.count())
print("Data ingestion completed.")

# Initialize LLM and retriever
llm = ChatOpenAI(temperature=0.7, api_key=openai_api_key)
retriever = db.as_retriever()

### Contextualize question ###
contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
)
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

### Answer question ###
system_prompt = (
    "You are an assistant for question-answering tasks on 4 Text2SQL research papers. "
    "Use the following pieces of retrieved context from these papers to answer "
    "the question. If you don't know the answer, say that you "
    "don't know. Use three sentences maximum and keep the "
    "answer concise unless asked otherwise."
    "\n\n"
    "{context}"
)
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

### Statefully manage chat history ###
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)

def answer_question(question, session_id):
    response = conversational_rag_chain.invoke(
        {"input": question},
        config={
            "configurable": {"session_id": session_id}
        },
    )
    return response["answer"], db._collection.count()