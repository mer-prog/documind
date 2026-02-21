export interface Document {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  status: "pending" | "processing" | "completed" | "failed";
  page_count: number | null;
  chunk_count: number;
  created_at: string;
  updated_at: string;
}

export interface DocumentListResponse {
  documents: Document[];
  total: number;
}

export interface IngestResponse {
  document_id: string;
  status: string;
  chunk_count: number;
}
