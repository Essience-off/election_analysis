import os 
import streamlit as st

import graph_init
from llm_chains.build_chain import resume_memory_llm

import dotenv

import time

dotenv_file = dotenv.find_dotenv()

st.title("Avez-vous des questions sur les parties politiques ?")

if 'memory' not in st.session_state:
    st.session_state['memory'] = ''
if "messages" not in st.session_state:
    st.session_state.messages = []
if "option" not in st.session_state:
    st.session_state.option = ""

option = st.selectbox(
"De quel partie voulez-vous avoir des informations ?",
("Ren", "RN", "nFP"),
index=None,
placeholder="Choisisez-votre partie...",
)

if option == "RN":
    dotenv.set_key(dotenv_file, "POLITICAL_PARTI", str(option))
    app = graph_init.build_graph()
    if st.session_state.option != option:
        st.session_state.option = option
        st.session_state['memory'] = ''
        st.rerun()

    
elif option == "nFP":
    dotenv.set_key(dotenv_file, "POLITICAL_PARTI", str(option))
    app = graph_init.build_graph()
    if st.session_state.option != option:
        st.session_state.option = option
        st.session_state['memory'] = ''
        st.rerun()

elif option == "Ren":
    dotenv.set_key(dotenv_file, "POLITICAL_PARTI", str(option))
    app = graph_init.build_graph()
    if st.session_state.option != option:
        st.session_state.option = option
        st.session_state['memory'] = ''
        st.rerun()




def response_generator():
    for word in response["generation"].split(" "):
        yield word + " "
        time.sleep(0.03)


if prompt := st.chat_input("Comment puis-je aider ?"):
# Display user message in chat message container
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    with st.chat_message("user"):
        st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.status("En attente d'une réponse..."):
            response = app.invoke({"question": str(prompt),
                                   "memory": st.session_state['memory']
                                   })
        stream_response = st.write_stream(response_generator())
        #st.markdown(response["generation"])
        st.session_state['memory'] = resume_memory_llm(response)

    st.session_state.messages.append({"role": "assistant", "content": response["generation"]})

