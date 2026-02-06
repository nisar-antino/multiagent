# Setup & Usage Guide - Multi-Agent GST System

This guide explains how to set up, configure, and run the Multi-Agent GST System using Docker.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

1.  **Docker Desktop** (or Docker Engine + Docker Compose)
    -   [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
    -   Ensure Docker is running (`docker --version`)

2.  **Git**
    -   To clone the repository.

3.  **Google Gemini API Key**
    -   Get a free API key from [Google AI Studio](https://ai.google.dev/).
    -   This is required for the LLM agents to function.

---

## 🚀 Step-by-Step Setup

### 1. Clone the Repository

Open your terminal (PowerShell, Command Prompt, or Terminal) and run:

```bash
git clone <repository_url>
cd multiagent
```

### 2. Configure Environment Variables

Create the `.env` file from the template:

**Windows (PowerShell):**
```powershell
copy .env.template .env
```

**Mac/Linux:**
```bash
cp .env.template .env
```

Open `.env` in a text editor and add your API key:

```ini
GOOGLE_API_KEY=your_actual_api_key_here
# Other settings can be left as default for local testing
```

### 3. Start the System with Docker

Build and start the services (MySQL database, Python app, Streamlit UI):

```bash
docker-compose up -d --build
```

-   `-d`: Runs in "detached" mode (background).
-   `--build`: Rebuilds the images to ensure you have the latest code.

Wait a few seconds for the database to initialize. You can check the status with:

```bash
docker-compose ps
```

---

## ⚙️ First-Time Initialization

If this is your first time running the system, you must **ingest the GST rules** into the vector database (ChromaDB) so the RAG agent can answer regulatory questions.

Run this command:

```powershell
docker exec gst_app python -c "import sys; sys.path.insert(0, '/app'); from src.agents.rag_agent import rag_agent; rag_agent.ingest_documents()"
```

*Note: You only need to do this once, or if you add new documents to `data/gst_rules/`.*

---

## 🖥️ How to Run

There are two ways to interact with the system:

### Option A: Command Line Interface (CLI)

Best for quick testing and seeing the raw agent outputs.

```powershell
docker exec -it gst_app python -m src.main
```

### Option B: Streamlit Web Dashboard

A user-friendly web interface for visual interaction.

1.  Ensure the containers are running (`docker-compose ps`).
2.  Open your browser and visit:
    **http://localhost:8501**

*(Note: If the Streamlit container isn't running automatically, you can start it manually or check `docker-compose.yml` to see if a Streamlit service is defined. Based on the file structure, run `streamlit run streamlit_app.py` locally if Python is installed, or ensure the docker service is configured.)*

---

## ❓ Troubleshooting

### 1. `RESOURCE_EXHAUSTED` / `429` Error
**Issue:** You hit the rate limit of the free Google Gemini API.
**Solution:**
-   Wait a minute for the quota to reset.
-   Use the **Direct SQL Tool** (bypasses LLM):
    ```powershell
    docker exec -it gst_app python -m src.sql_direct
    ```

### 2. Database Connection Failed
**Issue:** The Python app cannot connect to MySQL.
**Solution:**
-   Ensure the database container is healthy: `docker-compose ps`
-   Check logs: `docker-compose logs db`
-   Wait 30 seconds after starting Docker for MySQL to be fully ready.

### 3. "Vector store is empty"
**Issue:** RAG queries fail because no documents were ingested.
**Solution:** Run the initialization command from the "First-Time Initialization" section above.

### 4. Stopping the System
To stop all containers:
```bash
docker-compose down
```
