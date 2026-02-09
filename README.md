# Multi-Agent GST & Invoice Orchestration System

An intelligent multi-agent system that bridges structured financial data (MySQL) with unstructured regulatory documents (GST Rules) using LLM-powered orchestration.

## 🎯 Overview

This system uses **LangGraph** to coordinate three specialized agents:

- **SQL Agent**: Converts natural language to SQL queries against invoice data
- **RAG Agent**: Retrieves relevant GST compliance rules from documents
- **Orchestrator**: Routes queries and synthesizes intelligent answers

## Architecture

- **Sequential Reasoning**: For complex queries, system first retrieves rules, then generates SQL
- **LangGraph State Machine**: Manages agent coordination and data flow
- **Docker Containerized**: MySQL database + Python application
- **ChromaDB Vector Store**: Persistent storage for GST rule embeddings

## Quick Start

### Prerequisites

- Docker & Docker Compose installed
- Google Gemini API key ([Get one free](https://ai.google.dev))

### Setup

1. **Clone and configure**

   ```bash
   cd multiagent
   cp .env.template .env
   # Edit .env and add your GOOGLE_API_KEY
   ```
2. **Start the system**

   ```powershell
   docker-compose up -d --build
   ```
3. **Run the CLI**

   ```powershell
   docker exec -it gst_app python -m src.main
   ```

### First Time Setup

After starting, ingest GST rules into vector database:

```powershell
docker exec gst_app python -c "
import sys; sys.path.insert(0, '/app')
from src.agents.rag_agent import rag_agent
rag_agent.ingest_documents()
"
```

## Example Queries

**Data Queries** (SQL Agent):

- "Show me all invoices from Karnataka"
- "What is the total tax collected?"
- "List vendors in Gujarat"

**Regulatory Queries** (RAG Agent):

- "What is Rule 86B?"
- "Explain ITC eligibility criteria"

**Hybrid Queries** (Both Agents):

- "Are there any invoices violating Rule 86B limits?"
- "Which Karnataka invoices have IGST?"

## Database Schema

### Vendors Table

- `vendor_id`, `vendor_name`, `gstin` (15 chars), `state`

### Invoices Table

- `invoice_id`, `vendor_id`, `date`, `total_amount`, `tax_amount`
- `cgst`, `sgst`, `igst` (GST components)
- `status`, `place_of_supply`

### Invoice Items Table

- `item_id`, `invoice_id`, `description`, `hsn_code`
- `quantity`, `unit_price`, `tax_rate`

**Pre-loaded Data**: 20 vendors, 77 invoices, 57 items

## Tech Stack

- **Language**: Python 3.12
- **LLM**: Google Gemini (gemini-flash-latest)
- **Framework**: LangChain + LangGraph
- **Database**: MySQL 8.0
- **Vector DB**: ChromaDB
- **Containerization**: Docker + Docker Compose

## Project Structure

```
multiagent/
 docker-compose.yml          # Container orchestration
 Dockerfile                  # Python app container
 requirements.txt            # Python dependencies
 README.md                   # This file
 .env                        # API keys (create from template)
 .env.template              # Template for environment variables
 data/
    gst_rules/             # GST PDF/TXT documents (7KB sample included)
    vector_store/          # ChromaDB persistent storage
 src/
     main.py                # CLI entry point
     config.py              # Configuration management
     graph.py               # LangGraph state machine
     agents/
        sql_agent.py       # NLP  SQL conversion
        rag_agent.py       # Document retrieval
        classifier.py      # Query type detection
     database/
        schema.sql         # MySQL schema + seed data
        connection.py      # Database connector
     utils/
         llm.py             # Gemini API wrapper
         logger.py          # Logging configuration
         security.py        # SQL validation + rate limiting
```

## Configuration

### Environment Variables (.env)

```bash
# Google Gemini API
GOOGLE_API_KEY=your_api_key_here

# MySQL Configuration  
MYSQL_ROOT_PASSWORD=rootpassword123
MYSQL_DATABASE=gst_db
MYSQL_USER=gst_user
MYSQL_PASSWORD=gstpassword123
MYSQL_HOST=db
MYSQL_PORT=3306

# Rate Limiting
MAX_REQUESTS_PER_MINUTE=60
```

### Docker Services

**db (MySQL)**:

- Image: `mysql:8.0`
- Auto-initializes schema from `schema.sql`
- Port: `3306`

**app (Python)**:

- Built from Dockerfile
- Depends on `db`
- Keeps running with `sleep infinity`

## How It Works

### LangGraph Flow

1. **Classifier Node**: Analyzes query type

   - Data query  SQL Agent
   - Regulatory query  RAG Agent
   - Hybrid  RAG Agent  SQL Agent
2. **RAG Node** (if needed):

   - Retrieves relevant GST rules from ChromaDB
   - Updates `rag_context` in state
3. **SQL Node**:

   - Generates SQL (using RAG context if available)
   - Validates query (SELECT only, no dangerous keywords)
   - Executes against MySQL
   - Updates `sql_result` in state
4. **Synthesizer Node**:

   - Combines SQL results + RAG context
   - Generates natural language answer

### Security Features

- **Read-only database user**
- **SQL injection prevention** (sqlparse validation)
- **Rate limiting** (configurable RPM)
- **Query whitelist** (SELECT only)

## Troubleshooting

### API Quota Exceeded

```
Error: RESOURCE_EXHAUSTED: 429
```

**Solution**:

- Free tier: 20 requests/day, resets at midnight UTC
- Upgrade to paid tier: https://ai.google.dev/pricing
- Use SQL-only queries (don't require as many API calls)

### Vector Store Empty

```
Warning: Vector store is empty
```

**Solution**: Run document ingestion (see First Time Setup)

### Container Not Running

```bash
# Check status
docker-compose ps

# View logs
docker-compose logs app

# Restart
docker-compose restart
```

## Development

### Run Tests

```powershell
# Full diagnostic
docker exec gst_app python -c "
import sys
sys.path.insert(0, '/app')
from src.database.connection import db
from src.utils.llm import llm
print('Database:', 'OK' if db.health_check() else 'FAIL')
print('LLM:', 'OK' if llm.generate_text('test') else 'FAIL')
"
```

### Access MySQL Directly

```bash
docker exec -it gst_mysql mysql -ugst_user -pgstpassword123 gst_db
```

### View Logs

```bash
docker-compose logs -f app
```

## Use Cases

1. **Compliance Checking**: Verify invoices against GST regulations
2. **Tax Analysis**: Aggregate and analyze tax data across states
3. **Regulatory Query**: Natural language GST rule lookup
4. **Data Exploration**: Business intelligence on invoice data

## License

This project is provided as-is for educational and commercial use.

## Contributing

This is a demonstration project. For production use, consider:

- Adding authentication
- Implementing audit logs
- Scaling vector database
- Adding web UI
- Enhancing error handling

## Support

For issues related to:

- **Gemini API**: https://ai.google.dev/docs
- **LangChain**: https://python.langchain.com/docs
- **Docker**: https://docs.docker.com

---

**Built with  using LangGraph, Gemini, and Docker**
