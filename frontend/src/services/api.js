const API_BASE_URL = '/api/v1';

export const api = {
  /**
   * Retrieves all uploaded documents.
   */
  async listDocuments() {
    const response = await fetch(`${API_BASE_URL}/documents`);
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.message || 'Failed to fetch documents.');
    }
    return response.json();
  },

  /**
   * Deletes a document by ID.
   */
  async deleteDocument(id) {
    const response = await fetch(`${API_BASE_URL}/documents/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.message || 'Failed to delete document.');
    }
    return response.json();
  },

  /**
   * Uploads a PDF with progress callbacks.
   */
  uploadDocument(file, onProgress) {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.open('POST', `${API_BASE_URL}/documents/upload`);

      // Monitor request upload progress
      if (xhr.upload && onProgress) {
        xhr.upload.addEventListener('progress', (event) => {
          if (event.lengthComputable) {
            const percentage = Math.round((event.loaded * 100) / event.total);
            onProgress(percentage);
          }
        });
      }

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const res = JSON.parse(xhr.responseText);
            resolve(res);
          } catch (e) {
            reject(new Error('Invalid response payload from server.'));
          }
        } else {
          try {
            const err = JSON.parse(xhr.responseText);
            reject(new Error(err.message || 'Upload failed.'));
          } catch (e) {
            reject(new Error(`Upload failed with status code ${xhr.status}`));
          }
        }
      };

      xhr.onerror = () => {
        reject(new Error('Network connectivity error occurred.'));
      };

      const formData = new FormData();
      formData.append('file', file);
      xhr.send(formData);
    });
  }
};
