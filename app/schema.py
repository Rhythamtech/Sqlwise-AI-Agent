from pydantic import BaseModel

class SqlResponse(BaseModel):
    query: str
    explanation: str