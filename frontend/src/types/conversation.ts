import type { SourceCitation } from "./chat";

export interface ConversationSummary {
  id: string;
  title: string;
  message_count: number;
  updated_at: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources: SourceCitation[] | null;
  created_at: string;
}

export interface ConversationDetail {
  id: string;
  title: string;
  messages: Message[];
}
