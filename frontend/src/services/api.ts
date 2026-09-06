const API_BASE_URL = "http://localhost:8000";

export interface Document {
  document_id: string;
  filename: string;
  created_at: string;
  pages: number;
  chunks: number;
}

interface DocumentsResponse {
  documents: Document[];
}

export async function getDocuments(): Promise<Document[]> {
  const response = await fetch(`${API_BASE_URL}/documents`);

  if (!response.ok) {
    throw new Error("Failed to load documents.");
  }

  const data: DocumentsResponse = await response.json();
  return data.documents;
}

export async function uploadDocument(file: File): Promise<Document> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/documents/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    let message = "Failed to upload document.";

    try {
      const data = await response.json();
      if (data.detail) {
        message = data.detail;
      }
    } catch {
      // Keep the default error message.
    }

    throw new Error(message);
  }

  return response.json();
}

export async function deleteDocument(documentId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error("Failed to delete document.");
  }
}