# Multi-Agent GST System Architecture

This document provides a detailed visual representation of the system architecture, component interactions, and data flow.

## 📐 System Architecture Overview

```mermaid
graph TB
    User[👤 User CLI] --> Orchestrator[🧠 Orchestrator<br/>LangGraph State Machine]
    
    Orchestrator --> Classifier[📋 Classifier Node<br/>Query Type Detection]
    
    Classifier -->|Data Query| SQL[💾 SQL Agent<br/>NLP → SQL]
    Classifier -->|Regulatory Query| RAG[📚 RAG Agent<br/>Document Retrieval]
    Classifier -->|Hybrid Query| RAG
    
    RAG --> |Context Retrieved| SQL
    RAG --> Synthesizer[🎯 Synthesizer Node<br/>Answer Generation]
    
    SQL --> |Results| Synthesizer
    
    SQL --> MySQL[(MySQL Database<br/>Invoices & Vendors)]
    RAG --> ChromaDB[(ChromaDB<br/>Vector Store)]
    
    Synthesizer --> User
    
    Gemini[🤖 Google Gemini API<br/>gemini-flash-latest] -.->|LLM Calls| Classifier
    Gemini -.->|SQL Generation| SQL
    Gemini -.->|Embeddings| RAG
    Gemini -.->|Synthesis| Synthesizer
    
    style User fill:#e1f5ff
    style Orchestrator fill:#fff4e1
    style Gemini fill:#f0e1ff
    style MySQL fill:#e1ffe1
    style ChromaDB fill:#ffe1e1
```

## 🔄 LangGraph State Machine Flow

```mermaid
stateDiagram-v2
    [*] --> ClassifierNode: User Query
    
    ClassifierNode --> QueryAnalysis: Analyze Intent
    
    QueryAnalysis --> RAGNode: Regulatory/Hybrid
    QueryAnalysis --> SQLNode: Data Only
    
    RAGNode --> RetrieveContext: Query Vector DB
    RetrieveContext --> SQLNode: Has SQL Component?
    RetrieveContext --> SynthesizerNode: Regulatory Only
    
    SQLNode --> GenerateSQL: Create SQL Query
    GenerateSQL --> ValidateSQL: Security Check
    ValidateSQL --> ExecuteSQL: Execute Query
    ExecuteSQL --> SynthesizerNode: Return Results
    
    SynthesizerNode --> GenerateAnswer: Combine Context + Results
    GenerateAnswer --> [*]: Final Answer
    
    note right of ClassifierNode
        Determines query type:
        - data
        - regulatory  
        - hybrid
    end note
    
    note right of RAGNode
        Retrieves GST rules
        from ChromaDB using
        semantic search
    end note
    
    note right of SQLNode
        Converts NL to SQL
        Validates for safety
        Executes read-only
    end note
```

## 🗄️ Database Schema Architecture

```mermaid
erDiagram
    VENDORS ||--o{ INVOICES : "has many"
    INVOICES ||--o{ INVOICE_ITEMS : "contains"
    
    VENDORS {
        int vendor_id PK
        varchar vendor_name
        varchar gstin "15 chars"
        varchar state
    }
    
    INVOICES {
        int invoice_id PK
        int vendor_id FK
        date date
        decimal total_amount
        decimal tax_amount
        decimal cgst "Central GST"
        decimal sgst "State GST"
        decimal igst "Integrated GST"
        enum status "PAID/UNPAID"
        varchar place_of_supply
    }
    
    INVOICE_ITEMS {
        int item_id PK
        int invoice_id FK
        varchar description
        varchar hsn_code
        int quantity
        decimal unit_price
        decimal tax_rate
    }
```

## 🎯 Agent Interaction Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant L as LangGraph
    participant C as Classifier
    participant R as RAG Agent
    participant S as SQL Agent
    participant G as Gemini API
    participant DB as MySQL
    participant V as ChromaDB
    participant SY as Synthesizer
    
    U->>L: Submit Query
    L->>C: Classify Intent
    C->>G: Analyze Query Type
    G-->>C: Classification Result
    
    alt Hybrid Query Path
        C->>R: Retrieve Regulatory Context
        R->>V: Semantic Search
        V-->>R: Relevant Documents
        R->>G: Generate Embeddings
        G-->>R: Embeddings
        R->>S: Pass Context
        
        S->>G: Generate SQL with Context
        G-->>S: SQL Query
        S->>S: Validate SQL
        S->>DB: Execute SELECT
        DB-->>S: Query Results
        
        S->>SY: Results + Context
    else Data-Only Query Path
        C->>S: Direct to SQL
        S->>G: Generate SQL
        G-->>S: SQL Query
        S->>DB: Execute
        DB-->>S: Results
        S->>SY: Results Only
    else Regulatory-Only Query Path
        C->>R: Retrieve Rules
        R->>V: Search
        V-->>R: Documents
        R->>SY: Context Only
    end
    
    SY->>G: Synthesize Answer
    G-->>SY: Natural Language
    SY->>L: Final Answer
    L->>U: Display Response
```

## 🐳 Docker Container Architecture

```mermaid
graph LR
    subgraph Docker Network
        subgraph App Container
            Python[Python 3.12]
            LangChain[LangChain + LangGraph]
            Agents[SQL + RAG + Classifier]
            ChromaDB_Local[ChromaDB Files]
        end
        
        subgraph DB Container
            MySQL[MySQL 8.0]
            Schema[Schema + Seed Data]
        end
        
        Python --> MySQL
        Agents --> ChromaDB_Local
        Agents -.-> GeminiAPI[☁️ Google Gemini API]
    end
    
    Host[💻 Host Machine] -->|Port 3306| MySQL
    Host -->|docker exec| Python
    Host -->|Volumes| ChromaDB_Local
    
    style App Container fill:#e3f2fd
    style DB Container fill:#f1f8e9
    style GeminiAPI fill:#fff3e0
```

## 🔐 Security Architecture

```mermaid
graph TB
    Query[User Query] --> RateLimiter[⏱️ Rate Limiter<br/>60 RPM]
    RateLimiter --> SQLValidator[🛡️ SQL Validator]
    
    SQLValidator --> Check1{Multiple<br/>Statements?}
    Check1 -->|Yes| Reject1[❌ Reject]
    Check1 -->|No| Check2{SELECT<br/>Only?}
    
    Check2 -->|No| Reject2[❌ Reject]
    Check2 -->|Yes| Check3{Dangerous<br/>Keywords?}
    
    Check3 -->|Found| Reject3[❌ Reject]
    Check3 -->|Clean| Execute[✅ Execute on<br/>Read-Only User]
    
    Execute --> MySQL[(MySQL)]
    
    Reject1 --> Error[Return Error]
    Reject2 --> Error
    Reject3 --> Error
    
    style SQLValidator fill:#fff3cd
    style Execute fill:#d4edda
    style Error fill:#f8d7da
```

## 📦 Component Dependency Graph

```mermaid
graph TD
    Main[main.py<br/>CLI Entry] --> Graph[graph.py<br/>LangGraph]
    Main --> Config[config.py<br/>Environment]
    
    Graph --> Classifier[classifier.py]
    Graph --> SQLAgent[sql_agent.py]
    Graph --> RAGAgent[rag_agent.py]
    
    SQLAgent --> LLM[llm.py<br/>Gemini Wrapper]
    RAGAgent --> LLM
    Classifier --> LLM
    
    SQLAgent --> DBConn[connection.py<br/>MySQL]
    SQLAgent --> Security[security.py<br/>Validation]
    
    RAGAgent --> ChromaDB_Lib[ChromaDB Library]
    
    LLM --> LangChainLib[LangChain Google GenAI]
    
    DBConn --> SchemaSQL[schema.sql]
    
    Config --> EnvFile[.env]
    
    style Main fill:#e1f5ff
    style Graph fill:#fff4e1
    style LLM fill:#f0e1ff
    style Security fill:#ffe1e1
```

## 💾 Data Flow Architecture

```mermaid
graph LR
    subgraph Input
        Query[Natural Language Query]
    end
    
    subgraph Processing
        Embedding[🔢 Query Embedding]
        SQLGen[💻 SQL Generation]
        Retrieval[🔍 Vector Search]
    end
    
    subgraph Storage
        VectorDB[(ChromaDB<br/>GST Rules)]
        RDBMS[(MySQL<br/>Invoice Data)]
    end
    
    subgraph Output
        Context[📄 Retrieved Context]
        Results[📊 SQL Results]
        Answer[💬 Final Answer]
    end
    
    Query --> Embedding
    Query --> SQLGen
    
    Embedding --> VectorDB
    VectorDB --> Retrieval
    Retrieval --> Context
    
    SQLGen --> RDBMS
    RDBMS --> Results
    
    Context --> Answer
    Results --> Answer
    
    style VectorDB fill:#ffe1f5
    style RDBMS fill:#e1ffe1
    style Answer fill:#fff4e1
```

## 🚀 Deployment Architecture

```mermaid
graph TB
    subgraph Development Environment
        DevMachine[💻 Developer Machine]
        
        subgraph Docker Compose
            AppContainer[🐳 gst_app<br/>Python Application]
            DBContainer[🐳 gst_mysql<br/>MySQL 8.0]
        end
        
        LocalVolumes[📁 Local Volumes<br/>data/vector_store]
    end
    
    subgraph External Services
        GeminiCloud[☁️ Google Gemini API<br/>Cloud Service]
    end
    
    DevMachine -->|docker-compose up| Docker Compose
    AppContainer --> DBContainer
    AppContainer --> LocalVolumes
    AppContainer -.->|API Calls| GeminiCloud
    
    DevMachine -->|CLI Access| AppContainer
    DevMachine -->|Port 3306| DBContainer
    
    style AppContainer fill:#42a5f5
    style DBContainer fill:#66bb6a
    style GeminiCloud fill:#ffa726
```

## 📊 Technology Stack Layers

```mermaid
graph TB
    subgraph Presentation Layer
        CLI[Command Line Interface<br/>Colorama + Interactive]
    end
    
    subgraph Orchestration Layer
        LangGraph[LangGraph State Machine<br/>Workflow Management]
    end
    
    subgraph Agent Layer
        Classifier[Classifier Agent]
        SQL[SQL Agent]
        RAG[RAG Agent]
        Synth[Synthesizer]
    end
    
    subgraph Service Layer
        LLM[Gemini LLM Service<br/>ChatGoogleGenerativeAI]
        Embed[Embedding Service<br/>GoogleGenerativeAIEmbeddings]
        Validate[SQL Validator<br/>sqlparse]
    end
    
    subgraph Data Layer
        MySQL[(MySQL 8.0<br/>Structured Data)]
        Chroma[(ChromaDB<br/>Vector Data)]
    end
    
    CLI --> LangGraph
    LangGraph --> Classifier
    LangGraph --> SQL
    LangGraph --> RAG
    LangGraph --> Synth
    
    Classifier --> LLM
    SQL --> LLM
    SQL --> Validate
    RAG --> Embed
    Synth --> LLM
    
    SQL --> MySQL
    RAG --> Chroma
    
    style Presentation Layer fill:#e3f2fd
    style Orchestration Layer fill:#f3e5f5
    style Agent Layer fill:#fff3e0
    style Service Layer fill:#e8f5e9
    style Data Layer fill:#fce4ec
```

## 🎯 Key Architectural Decisions

### 1. **Sequential Reasoning (Option A)**
- **Decision**: Use sequential agent execution for hybrid queries
- **Rationale**: Higher accuracy by using RAG context to inform SQL generation
- **Trade-off**: Slightly slower than parallel execution, but more intelligent

### 2. **LangGraph for Orchestration**
- **Decision**: Use LangGraph instead of LangChain's AgentExecutor
- **Rationale**: Better control over state management and conditional routing
- **Benefit**: Clear visualization of agent interactions

### 3. **Docker Containerization**
- **Decision**: Separate containers for app and database
- **Rationale**: Clean deployment, easy scaling, reproducible environments
- **Benefit**: Portable across development/production

### 4. **ChromaDB for Vector Storage**
- **Decision**: Use ChromaDB instead of FAISS
- **Rationale**: Built-in persistence, simpler API, production-ready
- **Benefit**: No manual save/load of vector indices

### 5. **Read-Only Database Access**
- **Decision**: SQL agent uses read-only MySQL user
- **Rationale**: Prevent accidental data modification
- **Benefit**: Enhanced security for production use

---

**Architecture designed for**: Scalability, Security, Maintainability, and Intelligent Multi-Step Reasoning
