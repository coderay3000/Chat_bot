from config import setup_env
setup_env()
from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI


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

# Checkpointer
checkpointer = InMemorySaver()

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

CONFIG = {'configurable': {'thread_id': 'thread-1'}}
response = chatbot.invoke(
            {'messages': [HumanMessage(content='hi my name is ayush')]},
            config=CONFIG
        )

print(chatbot.get_state(config=CONFIG).values['messages'])  # Print the last message content