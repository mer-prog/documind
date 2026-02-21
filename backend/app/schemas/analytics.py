from pydantic import BaseModel


class UsageDataPoint(BaseModel):
    date: str
    queries: int
    tokens_prompt: int
    tokens_completion: int
    avg_latency_ms: float


class UsageResponse(BaseModel):
    data: list[UsageDataPoint]
    total_queries: int
    total_tokens: int


class TopQuery(BaseModel):
    query: str
    count: int


class TopQueriesResponse(BaseModel):
    queries: list[TopQuery]
