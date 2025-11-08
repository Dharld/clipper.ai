import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchProject } from '../lib/api';
import { UploadCard } from '../components/UploadCard';
import { ClipCard } from '../components/ClipCard';
import { StatusStepper } from '../components/StatusStepper';
import { WaveformVisualizer } from '../components/WaveformVisualizer';
import { JobProgress, SuggestedClip } from '../types';

interface DashboardSectionProps {
  onOpenClip: (clip: SuggestedClip) => void;
}

const progressSteps: JobProgress['steps'] = [
  { id: 'queued', label: 'Queued', description: 'File received' },
  { id: 'processing', label: 'Processing', description: 'Transcribing & extracting audio' },
  { id: 'preview', label: 'Preview', description: 'Highlights ready' },
  { id: 'done', label: 'Done', description: 'Clips ready to download' }
];

type StepId = JobProgress['steps'][number]['id'];

export function DashboardSection({ onOpenClip }: DashboardSectionProps) {
  const [projectId, setProjectId] = useState<string | null>(null);

  const { data, isFetching } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => fetchProject(projectId as string),
    enabled: Boolean(projectId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (!status || status === 'done' || status === 'error') return false;
      return 4000;
    }
  });

  const clips = useMemo(() => {
    if (data?.clips?.length) return data.clips;
    return demoClips;
  }, [data?.clips]);

  const currentStatus = (data?.status ?? 'queued') as StepId;

  return (
    <section id="dashboard" className="flex flex-col gap-10">
      <div className="flex flex-col gap-4">
        <h2 className="text-3xl font-semibold md:text-4xl">Dashboard</h2>
        <p className="max-w-2xl text-slate-300">
          Upload to see the calm pipeline in action. We’ll keep you updated from ingest to final clips.
        </p>
      </div>
      <div className="glass grid gap-6 rounded-3xl p-6 md:grid-cols-[1.2fr_1fr]">
        <div className="flex flex-col gap-6">
          <UploadCard onUploaded={setProjectId} />
          <StatusStepper progress={{ steps: progressSteps, current: currentStatus }} />
        </div>
        <div className="glass rounded-3xl p-6">
          <h3 className="text-sm uppercase tracking-[0.3em] text-clipper-accent">Pipeline</h3>
          <p className="mt-3 text-sm text-slate-300">
            {projectId
              ? isFetching
                ? 'Syncing with Clipper.ai…'
                : `Status: ${data?.status ?? 'queued'}`
              : 'Upload a file to start the pipeline.'}
          </p>
          <div className="mt-6 rounded-2xl border border-white/10 bg-black/40 p-4">
            <WaveformVisualizer />
          </div>
        </div>
      </div>
      <div className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <h3 className="text-xl font-semibold">Clip suggestions</h3>
          <p className="text-xs uppercase tracking-[0.35em] text-slate-400">
            {projectId ? `Project ${projectId}` : 'Demo view'}
          </p>
        </div>
        <div className="grid gap-6 md:grid-cols-3">
          {clips.map((clip) => (
            <ClipCard key={clip.id} clip={clip} onPreview={onOpenClip} />
          ))}
        </div>
      </div>
    </section>
  );
}

const demoClips: SuggestedClip[] = [
  {
    id: 'demo-1',
    title: 'You already have everything you need to start',
    score: 0.92,
    thumbnailUrl: 'https://images.unsplash.com/photo-1525182008055-f88b95ff7980?auto=format&fit=crop&w=600&q=80',
    videoUrl: 'https://storage.googleapis.com/coverr-main/mp4/Mt_Baker.mp4',
    transcriptSnippet: '…that’s the moment you hear the smile in their voice. So we keep the mic rolling and hit publish.',
    duration: 38
  },
  {
    id: 'demo-2',
    title: 'Cut the noise, keep the spark',
    score: 0.87,
    thumbnailUrl: 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=600&q=80',
    videoUrl: 'https://storage.googleapis.com/coverr-main/mp4/Night-City.mp4',
    transcriptSnippet: 'Clipper watches for laughs, hooks, or the sentence that hits home. Then it hands you the perfect outtake.',
    duration: 31
  },
  {
    id: 'demo-3',
    title: 'From raw conversation to release-ready',
    score: 0.9,
    thumbnailUrl: 'https://images.unsplash.com/photo-1529158062015-cad636e69505?auto=format&fit=crop&w=600&q=80',
    videoUrl: 'https://storage.googleapis.com/coverr-main/mp4/Nature-Sky.mp4',
    transcriptSnippet: 'While you take a breath, Clipper is polishing intros, trimming filler, and surfacing quotables.',
    duration: 42
  }
];
