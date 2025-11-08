import axios from 'axios';
import { ProjectSummary } from '../types';

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api'
});

export interface UploadResponse {
  projectId: string;
}

export async function uploadProject(file: File, signal?: AbortSignal): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);
  const response = await client.post('/jobs', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    signal
  });
  return response.data;
}

export async function fetchProject(id: string): Promise<ProjectSummary> {
  const response = await client.get(`/jobs/${id}`);
  return response.data;
}
