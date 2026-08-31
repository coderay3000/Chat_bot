import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage

# with st.chat_message('user'):
#   st.text('Hi')

# with st.chat_message('AI'):
#   st.text('Hi how can i assist you')  

# with st.chat_message('user'):
#   st.text('My name is ayush')  

CONFIG = {'configurable':{'thread_id':'thread-1'}}

#st.session_state -> dict ->enter press krne pe bhi andar ki cheeje erase nhi hoti
if 'message_history' not in st.session_state:
   st.session_state['message_history'] = []


#loading the convo history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
       st.text(message['content'])
# {'role':'user','content':'Hi'}
# {'role':'user','content':'Hi'}

user_input = st.chat_input('Type here')  

if user_input:

  # first add the message to the message history
  st.session_state['message_history'].append({'role':'user','content':user_input})
                         
  with st.chat_message('user'):
    st.text(user_input)


  

  response = chatbot.invoke({'messages':[HumanMessage(content=user_input)]},config=CONFIG)
  ai_message = response['messages'][-1].text  
  # first add the message to the message history
  st.session_state['message_history'].append({'role':'assistant','content':ai_message})
  with st.chat_message('assistant'):
    st.text(ai_message)