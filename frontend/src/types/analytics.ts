export interface UsageDataPoint {
  date: string;
  queries: number;
  tokens_prompt: number;
  tokens_completion: number;
  avg_latency_ms: number;
}

export interface UsageResponse {
  data: UsageDataPoint[];
  total_queries: number;
  total_tokens: number;
}

export interface TopQuery {
  query: string;
  count: number;
}

export interface TopQueriesResponse {
  queries: TopQuery[];
}
