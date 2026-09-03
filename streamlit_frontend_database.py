import streamlit as st
from langgraph_backend_database import chatbot,get_all_threads
from langchain_core.messages import HumanMessage
import uuid


#************************Utility function to generate unique thread IDs*************************
def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    # Check if messages key exists in state values, return empty list if not
    return state.values.get('messages', [])

            
# ************************Session State Initialization*********************************

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []


if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = get_all_threads()  # Load existing threads from the database

add_thread(st.session_state['thread_id'])    

# ***********************Configuration for the chatbot*************************

CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

        

# ***********************Side BAR UI*********************************
st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header('My Conversations')

for thread_id in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)

        temp_messages = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                role='user'
            else:
                role='assistant'
            temp_messages.append({'role': role, 'content': msg.content})

        st.session_state['message_history'] = temp_messages       
#**************************Main Chat Interface*********************************

# Previous conversation render karein
for message in st.session_state["message_history"]:
    if isinstance(message, dict) and "role" in message and "content" in message:
        with st.chat_message(message["role"]):
            st.write(message["content"])

user_input = st.chat_input('Type here...')

if user_input: 
    # User input state aur UI me append karein
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.write(user_input)

    # Backend ko touch kiye bina Frontend filtration generator
    def stream_generator():
        for chunk, metadata in chatbot.stream(
            {'messages': [HumanMessage(content=user_input)]},
            config=CONFIG,
            stream_mode='messages'
        ):
            # 1. Direct object content attribute extraction
            content = getattr(chunk, 'content', None)
            
            # 2. String check (Dictionaries aur metadata chunks ignore honge)
            if isinstance(content, str) and content:
                yield content
            elif isinstance(content, list):
                for part in content:
                    if isinstance(part, str) and part:
                        yield part
                    elif isinstance(part, dict) and 'text' in part and part['text']:
                        yield part['text']

    # Assistant response stream render karein
    with st.chat_message('assistant'):
        ai_message = st.write_stream(stream_generator())

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})