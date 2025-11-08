export type ProjectStatus = 'queued' | 'processing' | 'preview' | 'done' | 'error';

export interface SuggestedClip {
  id: string;
  title: string;
  score: number;
  thumbnailUrl: string;
  videoUrl: string;
  transcriptSnippet: string;
  duration: number;
}

export interface ProjectSummary {
  id: string;
  status: ProjectStatus;
  createdAt: string;
  clips: SuggestedClip[];
}

export interface JobProgress {
  steps: { id: ProjectStatus; label: string; description: string }[];
  current: ProjectStatus;
}
