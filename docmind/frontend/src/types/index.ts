export interface Document {
  id: string;
  filename: string;
  original_name: string;
  status: 'uploading' | 'processing' | 'ready' | 'failed';
  page_count: number;
  chunk_count: number;
  created_at: string;
  file_size: number;
}

export interface SourceChunk {
  document_id: string;
  filename: string;
  content: string;
  page_number: number;
  score: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: SourceChunk[];
  timestamp?: string;
  isStreaming?: boolean;
}

export interface UploadProgress {
  documentId?: string;
  filename: string;
  progress: number;
  status: 'uploading' | 'processing' | 'ready' | 'failed';
  error?: string;
}

export interface ChatSession {
  sessionId: string;
  documentIds: string[];
  messages: ChatMessage[];
  createdAt: string;
}
