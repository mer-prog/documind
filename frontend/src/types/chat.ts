export interface SourceCitation {
  chunk_id: string;
  document_name: string;
  page_number: number | null;
  text_snippet: string;
  relevance_score: number;
}

export interface ChatChunkEvent {
  type: "token" | "sources" | "done" | "error" | "conversation_id";
  content?: string;
  sources?: SourceCitation[];
  conversation_id?: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ModeResponse {
  mode: "demo" | "live";
  model: string | null;
}
