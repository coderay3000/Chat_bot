from config import setup_env
setup_env()
from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
import sqlite3

llm_endpoint = HuggingFaceEndpoint(
    # Model 1: Llama 3.1 8B Instruct
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    
    # Model 2: (Alternative) Qwen 2.5 7B
    # repo_id="Qwen/Qwen2.5-7B-Instruct",
    
    task="text-generation",
    max_new_tokens=512,
    do_sample=False,
    repetition_penalty=1.03
)

# Chat Model Wrapper (Messages & Streaming handle karne ke liye)
model = ChatHuggingFace(llm=llm_endpoint)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state['messages']
    response = model.invoke(messages)
    return {"messages": [response]}


conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)

# Checkpointer
checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

def get_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):  # ye bata dega ki aapke db me kitne checkpoints stored hai ,ya particular thread me kitne checkpoints hai 
        all_threads.add(checkpoint.config['configurable']['thread_id'])
    return list(all_threads)

