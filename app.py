from uuid import uuid4

import streamlit as st

from agent import build_agent
from memory_db import (
    approve_pending,
    delete_memory,
    discard_pending,
    get_memories_with_ids,
    get_pending,
    init_memory_db,
)

st.set_page_config(page_title="Memory Chat", page_icon="🧠")

# Ensure the memory table exists on first run
init_memory_db()

# --- Sidebar: user, thread control, and memory viewer ---
# --- Sidebar: user, thread control, and memory viewer ---
with st.sidebar:
    st.header("Session")
    user_id = st.text_input("User ID", value="alice")   # muss VOR der Memory-Liste stehen

    # Start a fresh thread on first run or whenever the user ID changes
    if st.session_state.get("user_id") != user_id:
        st.session_state.user_id = user_id
        st.session_state.thread_id = str(uuid4())
        st.session_state.messages = []

    if st.button("Start a new chat"):
        st.session_state.thread_id = str(uuid4())
        st.session_state.messages = []
        st.rerun()

    st.caption(f"Current thread: `{st.session_state.thread_id[:8]}...`")

    st.header("Long-term memory")
    memories = get_memories_with_ids(user_id)
    if memories:
        for mem_id, fact in memories:
            col_fact, col_btn = st.columns([5, 1])
            col_fact.write(f"- {fact}")
            if col_btn.button("🗑️", key=f"del_{mem_id}", help="Forget this fact"):
                delete_memory(user_id, mem_id)
                st.rerun()
    else:
        st.write("_No memories yet._")
    pending = get_pending(user_id)
    if pending:
        st.header("Waiting for approval")
        for p_id, fact in pending:
            st.write(f"- {fact}")
            col_ok, col_no = st.columns(2)
            if col_ok.button("✅ Save", key=f"ok_{p_id}"):
                approve_pending(user_id, p_id)
                st.rerun()
            if col_no.button("❌ Discard", key=f"no_{p_id}"):
                discard_pending(user_id, p_id)
                st.rerun()

# --- Main pane: chat ---
st.title("🧠 Memory Chat")
st.caption(
    "Tell the bot to remember something, click 'Start a new chat', "
    "and watch it recall the fact in the next conversation."
)

for msg in st.session_state.get("messages", []):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("Type a message..."):
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Build a fresh agent so the latest memories appear in its system prompt
    agent = build_agent(user_id)
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_input}]},
        config=config,
    )
    reply = result["messages"][-1].content

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()  # replay history and refresh the sidebar memory list