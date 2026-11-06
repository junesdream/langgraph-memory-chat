# 🧠 LangGraph Memory Chat

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-agent-1C3C3C)
![LangChain](https://img.shields.io/badge/LangChain-create__agent-1C3C3C)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?logo=streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-persistence-003B57?logo=sqlite&logoColor=white)
![OpenRouter](https://img.shields.io/badge/OpenRouter-LLM%20gateway-6566F1)

A chat agent with **short-term and long-term memory**: it remembers facts about each user across new chats and app restarts, and a **human approves every fact** before it is stored.

---

## 📌 Overview

Most chatbots forget everything when a conversation ends. This project separates two kinds of memory:

- **Short-term memory** – the message history of one chat, stored per `thread_id` by LangGraph's `SqliteSaver`.
- **Long-term memory** – facts about a user (preferences, allergies, interests), stored per `user_id` in a separate SQLite table and injected into the system prompt of every new chat.

The agent proposes facts with a `remember` tool. They only become long-term memory after the user approves them (**human-in-the-loop**), and the user can delete any stored fact at any time.

---

## ✨ Core Features

| Feature | Description |
| --- | --- |
| Long-term memory | Facts per user survive new chats and restarts of the Python process |
| Short-term memory | Each chat resumes from its own thread history (`threads.db`) |
| `remember` tool | The LLM decides what is worth keeping and phrases it as a short fact |
| Human-in-the-loop approval | Proposed facts wait in the sidebar until the user clicks ✅ Save or ❌ Discard |
| Forget button | 🗑️ next to each fact deletes it from long-term memory |
| Multi-user | Memories are isolated per `user_id` (e.g. `alice` vs `bob`) |

---

## 🛠️ Tech Stack

| Layer | Technology |
| --- | --- |
| Agent | LangChain `create_agent` (built on LangGraph) |
| Short-term memory | `langgraph-checkpoint-sqlite` (`SqliteSaver`) |
| Long-term memory | SQLite + plain SQL |
| LLM | `openai/gpt-6-luna` via OpenRouter (`ChatOpenAI`) |
| UI | Streamlit |
| Tooling | uv, ruff |

---

## 🏗️ Architecture

```
┌──────────────────────┐     ┌───────────────────────┐     ┌────────────┐
│ Streamlit UI         │ ──▶ │ create_agent          │ ──▶ │ OpenRouter │
│ chat + sidebar       │     │ + SqliteSaver         │     └────────────┘
│ (user, memories,     │     │ + remember tool       │
│  approval buttons)   │     └───────────┬───────────┘
└──────────┬───────────┘                 │
           │                 ┌───────────┴───────────┐
           │                 ▼                       ▼
           │        ┌────────────────┐     ┌──────────────────────┐
           │        │ threads.db     │     │ memories.db          │
           │        │ per-thread     │     │ pending_memories ──▶ │
           └──────▶ │ message state  │     │ memories (per user)  │
     approve/delete └────────────────┘     └──────────────────────┘
```

**Flow per message:** load the user's facts from `memories.db` into the system prompt → agent answers with the thread history from `threads.db` → if it hears a new fact, `remember` writes it to `pending_memories` → the user approves or discards it in the sidebar.

| File | Responsibility |
| --- | --- |
| `app.py` | Streamlit UI: chat, user/thread controls, memory list, approval and delete buttons |
| `agent.py` | Builds the agent per turn: LLM, `SqliteSaver`, `remember` tool, system prompt with memories |
| `memory_db.py` | SQL helpers for `memories` and `pending_memories` (save, list, approve, discard, delete) |

---

## 🚀 Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/junesdream/langgraph-memory-chat.git
   cd langgraph-memory-chat
   ```
2. **Install dependencies** (requires [uv](https://docs.astral.sh/uv/))
   ```bash
   uv sync
   ```
3. **Set your OpenRouter API key**
   ```bash
   export OPENROUTER_API_KEY="sk-or-..."
   ```
4. **Run the app**
   ```bash
   uv run streamlit run app.py
   ```
5. **Try the memory flow**
   - As `alice`, send: *"Please remember that I'm vegetarian."*
   - Approve the fact in the sidebar (✅ Save).
   - Click **Start a new chat** and ask: *"What should I make for dinner tonight?"*
   - Restart the app and ask again – the fact is still there.
   - Switch to `bob` – no memories.

---

## 🔒 Security

| Topic | Measure |
| --- | --- |
| User isolation | All queries filter by `user_id`; delete and approve also check `user_id` |
| Tool permissions | `user_id` is bound into the tool via a closure, so the LLM cannot write facts for another user |
| SQL injection | Parameterised queries (`?` placeholders) only |
| Secrets | API key via environment variable; `.env` and `*.db` are in `.gitignore` |
| Human control | No fact is stored without explicit approval; any fact can be deleted |

---

## 🔍 Findings & Limitations

- The LLM phrases facts itself and sometimes merges several facts into one line.
- All of a user's facts are loaded into the prompt; with many facts this will hit token limits.
- `user_id` is a plain text field for the demo, not real authentication.
- Approval happens in the UI, not with LangGraph's `interrupt()`, so the agent does not wait for the decision.

---

## 🧭 Next Steps

- Semantic memory search: embed facts and load only the most relevant ones per message.
- Use LangGraph `interrupt()` for approval inside the graph.
- Thread list with LLM-generated titles in the sidebar.
- Replace SQLite with PostgreSQL for multi-user deployment.

---

## 📚 Docs

| Resource | Link |
| --- | --- |
| LangGraph memory concepts | [docs.langchain.com](https://docs.langchain.com/oss/python/langgraph/memory) |
| Streamlit chat elements | [docs.streamlit.io](https://docs.streamlit.io/develop/api-reference/chat) |

---

## 🙏 Acknowledgement

Based on an exercise from the **Turing College AI Engineering** program (Sprint 3, Part 4: Long-Term Memory), extended with human-in-the-loop approval and a forget button.

---

## 👤 Author

**JuNe** (@junesdream) – AI Engineering • Software & Full-Stack Development • Electronic Music