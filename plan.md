

## 📌 Starter Pseudo‑Code For Each File

---

### **src/config.py**

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    VECTOR_DB_PATH: str
    LLM_MODEL: str = "gpt-4o-mini"

    class Config:
        env_file = ".env"

settings = Settings()
```

> Environment file `.env`:

```
OPENAI_API_KEY=your_api_key_here
VECTOR_DB_PATH=./data/vectors
LLM_MODEL=gpt-4o-mini
```

---

### **src/retriever.py**

```python
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from src.config import settings

def get_retriever(k: int = 8):
    """
    Load existing vector DB and return retriever.
    Assumes vector DB already populated.
    """
    embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
    vectordb = Chroma(
        persist_directory=settings.VECTOR_DB_PATH,
        embedding_function=embeddings
    )
    return vectordb.as_retriever(search_kwargs={"k": k})
```

---

### **src/llm.py**

```python
from langchain import OpenAI
from src.config import settings

def get_llm():
    """
    Initialize LLM client with API key and model.
    """
    return OpenAI(api_key=settings.OPENAI_API_KEY, model=settings.LLM_MODEL)
```

---

### **src/prompts.py**

```python
# Central prompt templates for RAG

QA_PROMPT = """
Use the context to accurately answer the question.

Context:
{context}

Question:
{question}

Answer:
"""
```

---

### **src/rag.py**

```python
from langchain.chains import RetrievalQA
from src.llm import get_llm
from src.retriever import get_retriever

def build_rag_agent():
    """
    Build RAG chain: LLM + retriever
    """
    llm = get_llm()
    retriever = get_retriever()
    
    rag = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )
    return rag

def handle_query(question: str):
    """
    Query RAG chain and return answer + sources.
    """
    agent = build_rag_agent()
    result = agent({"query": question})
    return result["result"], result["source_documents"]
```

---

### **src/schema.py**

```python
from pydantic import BaseModel
from typing import List

class QueryRequest(BaseModel):
    question: str

class Source(BaseModel):
    id: int
    text: str

class AnswerResponse(BaseModel):
    answer: str
    sources: List[Source]
```

---

### **app/router/routes.py**

```python
from fastapi import APIRouter
from src.schema import QueryRequest, AnswerResponse
from src.rag import handle_query

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/ask", response_model=AnswerResponse)
def ask(q: QueryRequest):
    answer, sources = handle_query(q.question)
    return {
        "answer": answer,
        "sources": [
            {"id": idx, "text": s.page_content}
            for idx, s in enumerate(sources, 1)
        ]
    }
```

---

### **src/main.py**

```python
from fastapi import FastAPI
from app.router.routes import router

app = FastAPI(title="RAG Service")

app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## ⚙️ Other Files

---

### **.gitignore**

```
__pycache__/
.env
data/
*.pyc
```

---

### **pyproject.toml**

```toml
[tool.poetry]
name = "my_rag_app"
version = "0.1.0"
description = "RAG API project"

[tool.poetry.dependencies]
python = "^3.10"
fastapi = "*"
uvicorn = "*"
langchain = "*"
openai = "*"
chromadb = "*"
pydantic = "*"
```

---

### **Dockerfile**

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### **README.md**

```
# RAG API

## Setup

1. Create .env:
```

OPENAI_API_KEY=your_key
VECTOR_DB_PATH=./data/vectors
LLM_MODEL=gpt-4o-mini

```

2. Install dependencies:
```

poetry install

```

3. Run:
```

uvicorn src.main:app --reload

```

4. Use endpoint:
POST /api/ask

Payload:
```

{"question":"Your text here"}

```
```

---

## 🧠 Notes

✅ All required modules are present
✅ Config + retriever logic added
✅ Clean separation of concerns
✅ API ready to expand (agents, analytics, feedback)

---

If you want, I can also generate **unit test templates** and **CI/CD workflows** next! 🚀
