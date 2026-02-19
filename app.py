import streamlit as st
from azure.ai.projects import  AIProjectClient
from azure.ai.agents.models import ListSortOrder
from azure.identity import DefaultAzureCredential
import time

project = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint="https://azure-ai-foundry-hme.services.ai.azure.com/api/projects/Agentic-AI-Test")

agent = project.agents.get_agent("asst_XmSdr52VMvRJxJLqsTQLKGtN")

if "thread_id" not in st.session_state:
    thread = project.agents.threads.create()
    st.session_state.thread_id = thread.id

thread_id = st.session_state.thread_id

##Main App
USER_AVATAR = "images/user.png"
AGENT_AVATAR = "images/agent.png"

st.image("images/logo.png", width=180)
    
st.write("dbi services - IT Helpdesk by AI")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello, I'm your intelligent helpdesk agent. How may I help you?"}]

for message in st.session_state.messages:
    avatar = USER_AVATAR if message["role"] == "user" else AGENT_AVATAR
    with st.chat_message(message["role"], avatar = avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("..."):
    message = project.agents.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt
    )

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    run = project.agents.runs.create_and_process(
        thread_id=thread_id,
        agent_id=agent.id)
    
    if run.status == "failed":
        print(f"Run failed: {run.last_error}")
    else:
        paged = project.agents.messages.list(thread_id=thread_id, order=ListSortOrder.ASCENDING)
        messages = list(paged)
        message = messages[-1] 
        
        # Display assistant response in chat message container
        with st.chat_message("assistant", avatar=AGENT_AVATAR):
            message_placeholder = st.empty()
            full_response = ""
            assistant_response = message.text_messages[-1].text.value
            # Simulate stream of response with milliseconds delay
            for chunk in assistant_response.splitlines(keepends=True):
                full_response += chunk + " "
                time.sleep(0.1)
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})