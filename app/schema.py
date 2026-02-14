from pydantic import BaseModel
from typing import List, Optional

class SqlResponse(BaseModel):
    query: str
    explanation: str

class QueryPlan(BaseModel):
    tables_needed: List[str]
    join_strategy: str
    filters: str
    aggregations: str
    sorting: str
    computed_columns: str
    full_plan: str