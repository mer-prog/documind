# DocuMind API Documentation

The DocuMind API provides programmatic access to document management, intelligent search, and AI-powered chat capabilities. All API endpoints require authentication and return JSON responses unless otherwise specified.

## Authentication

All API requests must include a valid JWT token in the Authorization header using the Bearer scheme.

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Tokens are obtained by authenticating through the login endpoint. Tokens expire after 24 hours, after which a new token must be obtained. Include the token in every subsequent request to authenticated endpoints.

### POST /api/auth/login

Authenticate a user with email and password credentials. Returns user information that can be used to generate a JWT token through the client-side authentication flow.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "your-password"
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "admin",
  "workspace_id": "660e8400-e29b-41d4-a716-446655440001"
}
```

**Error Responses:**
- `401 Unauthorized` — Invalid email or password
- `422 Unprocessable Entity` — Missing or malformed request body

### POST /api/auth/register

Create a new user account and workspace. The first user in a workspace is automatically assigned the admin role.

**Request Body:**
```json
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "password": "secure-password-123"
}
```

**Response (200 OK):**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "email": "jane@example.com",
  "name": "Jane Smith",
  "role": "admin",
  "workspace_id": "880e8400-e29b-41d4-a716-446655440003"
}
```

**Error Responses:**
- `400 Bad Request` — User with this email already exists

### POST /api/auth/verify

Verify the current JWT token and return the authenticated user's information. Use this endpoint to validate that a token is still valid and to retrieve up-to-date user details.

**Headers:** Requires `Authorization: Bearer <token>`

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "admin",
  "workspace_id": "660e8400-e29b-41d4-a716-446655440001"
}
```

## Documents API

The Documents API manages file uploads, retrieval, and processing within a workspace. All document operations are scoped to the authenticated user's workspace.

### GET /api/documents

List all documents in the current workspace with pagination support.

**Query Parameters:**
- `skip` (integer, default: 0) — Number of documents to skip
- `limit` (integer, default: 50) — Maximum number of documents to return

**Response (200 OK):**
```json
{
  "documents": [
    {
      "id": "990e8400-e29b-41d4-a716-446655440004",
      "filename": "company-handbook.md",
      "file_type": "md",
      "file_size": 15234,
      "status": "completed",
      "page_count": null,
      "chunk_count": 24,
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:31:45Z"
    }
  ],
  "total": 1
}
```

### POST /api/documents

Upload a new document to the workspace. The request must use `multipart/form-data` encoding. Supported file types are Markdown (.md), PDF (.pdf), and Word (.docx).

**Request:** `Content-Type: multipart/form-data` with a `file` field containing the document.

**Response (200 OK):** Returns the created document object with status set to "pending". The document must be ingested separately using the ingest endpoint before it becomes searchable.

**Error Responses:**
- `400 Bad Request` — Unsupported file type or missing filename
- `413 Payload Too Large` — File exceeds maximum upload size (50MB)

### DELETE /api/documents/{document_id}

Delete a document and all its associated chunks from the workspace. This action is permanent and cannot be undone.

**Response:** `204 No Content` on success

**Error Responses:**
- `404 Not Found` — Document does not exist or belongs to a different workspace

### POST /api/documents/{document_id}/ingest

Trigger the document processing pipeline for an uploaded document. This endpoint initiates text extraction, semantic chunking, embedding generation, and vector storage. The process runs synchronously and returns when complete.

**Processing Pipeline:**
1. Extract text from the document based on its file type
2. Split text into semantic chunks (~500 tokens each with 50-token overlap)
3. Generate embeddings using OpenAI text-embedding-3-small
4. Store chunks and embeddings in PostgreSQL with pgvector

**Response (200 OK):**
```json
{
  "document_id": "990e8400-e29b-41d4-a716-446655440004",
  "status": "completed",
  "chunk_count": 24
}
```

**Error Responses:**
- `404 Not Found` — Document not found
- `400 Bad Request` — Document has no file content

## Chat API

The Chat API enables AI-powered conversations about your documents. Responses are streamed using Server-Sent Events (SSE) for real-time display.

### POST /api/chat

Send a message and receive a streaming AI response with source citations. The response uses the `text/event-stream` content type and sends multiple event types during a single response.

**Request Body:**
```json
{
  "message": "What is the company's remote work policy?",
  "conversation_id": "aab0c000-e29b-41d4-a716-446655440005"
}
```

The `conversation_id` field is optional. If omitted, a new conversation is created automatically. If provided, the message is added to the existing conversation and previous context is used to inform the response.

**Response (SSE Stream):**

Events are sent in the following order:

1. **conversation_id** — Sent first with the conversation identifier
```
data: {"type": "conversation_id", "conversation_id": "aab0c000-..."}
```

2. **sources** — Retrieved document chunks relevant to the query
```
data: {"type": "sources", "sources": [{"chunk_id": "...", "document_name": "company-handbook.md", "page_number": null, "text_snippet": "...", "relevance_score": 0.85}]}
```

3. **token** — Individual tokens of the AI response, sent as they are generated
```
data: {"type": "token", "content": "The"}
data: {"type": "token", "content": " company"}
data: {"type": "token", "content": " offers"}
```

4. **done** — Signals the end of the response
```
data: {"type": "done"}
```

5. **error** — Sent if an error occurs during processing
```
data: {"type": "error", "content": "Error description"}
```

**Implementation Notes:**
- Use `@microsoft/fetch-event-source` on the frontend for POST-based SSE connections, as the native `EventSource` API only supports GET requests
- Include `Cache-Control: no-cache` and `Connection: keep-alive` headers
- The AI response includes source citations in `[Source: document_name, Page X]` format

## Conversations API

The Conversations API provides access to chat history and conversation management.

### GET /api/conversations

List all conversations for the authenticated user, ordered by most recently updated.

**Response (200 OK):**
```json
[
  {
    "id": "aab0c000-e29b-41d4-a716-446655440005",
    "title": "Remote work policy questions",
    "message_count": 6,
    "updated_at": "2025-01-20T14:30:00Z"
  }
]
```

### GET /api/conversations/{conversation_id}

Retrieve a complete conversation including all messages and their source citations.

**Response (200 OK):**
```json
{
  "id": "aab0c000-e29b-41d4-a716-446655440005",
  "title": "Remote work policy questions",
  "messages": [
    {
      "id": "bbc0d000-...",
      "role": "user",
      "content": "What is the company's remote work policy?",
      "sources": null,
      "created_at": "2025-01-20T14:25:00Z"
    },
    {
      "id": "ccd0e000-...",
      "role": "assistant",
      "content": "DocuMind is a remote-first company...",
      "sources": [
        {
          "chunk_id": "...",
          "document_name": "company-handbook.md",
          "page_number": null,
          "text_snippet": "DocuMind is a remote-first company...",
          "relevance_score": 0.92
        }
      ],
      "created_at": "2025-01-20T14:25:03Z"
    }
  ]
}
```

## Rate Limits and Errors

API requests are rate-limited to prevent abuse and ensure fair usage across all users.

**Rate Limits:**
- Authentication endpoints: 10 requests per minute per IP address
- Document upload: 20 requests per minute per workspace
- Chat: 30 requests per minute per user
- Read endpoints (GET): 100 requests per minute per user

When a rate limit is exceeded, the API returns a `429 Too Many Requests` response with a `Retry-After` header indicating how many seconds to wait before retrying.

**Standard Error Format:**
```json
{
  "detail": "Human-readable error description"
}
```

**Common HTTP Status Codes:**
- `200 OK` — Request succeeded
- `204 No Content` — Request succeeded with no response body (e.g., DELETE)
- `400 Bad Request` — Invalid request parameters or body
- `401 Unauthorized` — Missing or invalid authentication token
- `403 Forbidden` — Authenticated but not authorized for this action
- `404 Not Found` — Resource does not exist
- `422 Unprocessable Entity` — Request body validation failed
- `429 Too Many Requests` — Rate limit exceeded
- `500 Internal Server Error` — Unexpected server error

## Webhooks

DocuMind supports webhooks for real-time notifications about events in your workspace. Configure webhook URLs through the workspace settings page.

**Supported Events:**
- `document.uploaded` — A new document was uploaded
- `document.ingested` — A document completed processing
- `document.failed` — Document processing failed
- `conversation.created` — A new conversation was started

**Webhook Payload:**
```json
{
  "event": "document.ingested",
  "timestamp": "2025-01-15T10:31:45Z",
  "workspace_id": "660e8400-e29b-41d4-a716-446655440001",
  "data": {
    "document_id": "990e8400-e29b-41d4-a716-446655440004",
    "filename": "company-handbook.md",
    "chunk_count": 24
  }
}
```

Webhook requests include an `X-DocuMind-Signature` header containing an HMAC-SHA256 signature of the payload for verification. Your endpoint must respond with a 2xx status code within 10 seconds or the delivery will be retried up to 3 times with exponential backoff.

## SDKs and Client Libraries

Official client libraries are available for popular programming languages to simplify API integration:

- **JavaScript/TypeScript**: `npm install @documind/sdk` — Full-featured client with TypeScript types, SSE streaming support, and automatic token refresh
- **Python**: `pip install documind` — Async-first client built on httpx with streaming support
- **Go**: `go get github.com/documind/go-sdk` — Lightweight client with context-based cancellation

All SDKs provide type-safe wrappers around the REST API, handle authentication automatically, and include built-in retry logic for transient errors. Check the respective SDK documentation for usage examples and configuration options.
