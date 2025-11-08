import { Play, Wand2, Download } from 'lucide-react';
import { SuggestedClip } from '../types';

interface ClipCardProps {
  clip: SuggestedClip;
  onPreview: (clip: SuggestedClip) => void;
}

export function ClipCard({ clip, onPreview }: ClipCardProps) {
  return (
    <div className="glass flex flex-col gap-4 rounded-3xl p-5">
      <div className="relative overflow-hidden rounded-2xl border border-white/5">
        <img src={clip.thumbnailUrl} alt={clip.title} className="h-40 w-full object-cover" />
        <button
          onClick={() => onPreview(clip)}
          className="absolute inset-0 flex items-center justify-center bg-black/40 text-white opacity-0 transition hover:opacity-100"
        >
          <Play className="h-6 w-6" />
        </button>
        <span className="absolute left-4 top-4 inline-flex items-center gap-2 rounded-full bg-black/50 px-3 py-1 text-xs font-medium text-white">
          <Wand2 className="h-3.5 w-3.5" /> Score {Math.round(clip.score * 100)}%
        </span>
      </div>
      <div className="flex flex-col gap-2">
        <h4 className="text-lg font-semibold text-white">{clip.title}</h4>
        <p className="text-xs text-slate-400">{clip.transcriptSnippet}</p>
      </div>
      <div className="flex items-center justify-between text-xs text-slate-400">
        <span>{Math.round(clip.duration)}s</span>
        <a
          href={clip.videoUrl}
          className="inline-flex items-center gap-2 rounded-full border border-white/10 px-3 py-1 text-xs font-medium text-white hover:border-clipper-primary"
        >
          <Download className="h-3 w-3" /> Download
        </a>
      </div>
    </div>
  );
}
