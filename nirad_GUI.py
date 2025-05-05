# -*- coding: utf-8 -*-
'''author__ = 'Alberto Costa'
   mail = 'noobsajbot@gmail.com'
   date = '21 Apr 2025'

   NIRAD Graphical interface with sounds
'''

import nirad_utils as shu
from smolagents import CodeAgent
import pandas as pd
from colorama import Fore, Back, Style
import streamlit as st

#for windows
#from playsound import playsound #use version 1.2.2

#general
import pygame


#set to True to disable sound
enable_sound=False


st.set_page_config(page_title="N.I.R.A.D.", page_icon="images/nirad_icon.ico", layout="wide")

initial_prompt=f'{shu.prompt_NIRAD_v2}\n {shu.few_shot_examples_v2}\n'

list_tools=[shu.compute_worst_case_attack, shu.compute_resilience, shu.compute_max_flow, shu.get_network, shu.generate_input_data, shu.change_capacity, shu.change_cost, shu.reset_values]

agent = CodeAgent(tools=list_tools, model=shu.model, additional_authorized_imports=['pandas','io'], max_steps=10, verbosity_level=-1)  #-1 to suppress reasoning steps



#style changes
st.markdown(
    """
    <style    /* Default border color */
    div[data-testid="stChatInput"] > div  {
        color: green !important;
        background-color: black!important;
    }
    div[data-testid="stChatInput"] > div textarea  {
        color: red !important;
        
    }
    style    """,
    unsafe_allow_html=True
)



st.title(":green[N.I.R.A.D.]")
st.header(":green[Network Interdiction Resilience Advanced Defense]")

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

    
if "chat_history" not in st.session_state:
    st.session_state.chat_history = initial_prompt  # Initialize an empty chat history

# Display the conversation history
for message in st.session_state.messages:
   with st.chat_message(message["role"], avatar=message["avatar"]):
       if message["role"]=='user':
           st.write(f":red[{message['content']}]")
       else:
            st.text(message["content"])
      

#reset network data when new execution            
if "reset_executed" not in st.session_state:
    st.session_state.reset_executed = False

# Run shu.reset_values() if it hasn't been executed in this session
if not st.session_state.reset_executed:
    shu.reset_values()  # Call your function here
    st.session_state.reset_executed = True
     

# Handling user input style
st.markdown("""
    <style>
    /* Target the placeholder inside the stChatInputTextArea */
    textarea[data-testid="stChatInputTextArea"]::placeholder {
        color: red;
    }
    </style>
""", unsafe_allow_html=True)
        

if enable_sound:
    pygame.mixer.init()        
        
if prompt := st.chat_input(">>"):
    # Add user input to the session state messages
    st.session_state.messages.append({"role": "user", "content": prompt, "avatar":"images/user_gpt.png"})
    with st.chat_message("user", avatar="images/user_gpt.png"):
        st.write(f":red[{prompt}]")
        if enable_sound:
            pygame.mixer.music.load("static/mixkit-sci-fi-click-900.mp3")
            pygame.mixer.music.play()
            
            #for windows
            #playsound("static/mixkit-sci-fi-click-900.mp3")
        
    # Append the new user input to the chat history
    st.session_state.chat_history += f"User: {prompt}\n"
    

    # Call N.I.R.A.D. agent to get the response
    with st.chat_message("NIRAD", avatar="images/nirad_gpt.png"):

        response = shu.retry(agent, st.session_state.chat_history)
        st.text(response)
        if enable_sound:
            #fow windows
            #playsound("static/mixkit-opening-software-interface-2578.mp3")
            pygame.mixer.music.load("static/mixkit-opening-software-interface-2578.mp3")
            pygame.mixer.music.play()
        
        # Append the agent's response to the chat history
        st.session_state.chat_history += f"Answer: {response}\n"
    
    # Append the assistant's response to the session state
    st.session_state.messages.append({"role": "NIRAD", "content": response, "avatar":"images/nirad_gpt.png"})



#  python -m streamlit run nirad_GUI.py










