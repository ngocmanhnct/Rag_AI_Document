import client from './client';

export const listDocuments = () => client.get('/documents');

export const uploadDocument = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return client.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const deleteDocument = (id) => client.delete(`/documents/${id}`);