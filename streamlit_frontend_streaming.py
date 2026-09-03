import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage



CONFIG = {'configurable': {'thread_id': 'thread-1'}}

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# Previous conversation render karein
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.write(message['content'])

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