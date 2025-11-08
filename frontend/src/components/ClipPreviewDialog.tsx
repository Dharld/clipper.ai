import * as Dialog from '@radix-ui/react-dialog';
import { Download, RotateCcw } from 'lucide-react';
import { SuggestedClip } from '../types';

interface ClipPreviewDialogProps {
  clip: SuggestedClip | null;
  onOpenChange: (open: boolean) => void;
}

export function ClipPreviewDialog({ clip, onOpenChange }: ClipPreviewDialogProps) {
  return (
    <Dialog.Root open={Boolean(clip)} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/70 backdrop-blur" />
        <Dialog.Content className="fixed left-1/2 top-1/2 w-[90vw] max-w-3xl -translate-x-1/2 -translate-y-1/2 rounded-3xl border border-white/10 bg-[#111111] p-6 shadow-2xl">
          <div className="flex flex-col gap-6">
            <Dialog.Title className="text-xl font-semibold text-white">{clip?.title ?? 'Preview'}</Dialog.Title>
            <div className="overflow-hidden rounded-2xl border border-white/10 bg-black">
              {clip ? (
                <video src={clip.videoUrl} controls className="h-72 w-full object-cover" />
              ) : (
                <div className="flex h-72 items-center justify-center text-slate-400">Select a clip to preview</div>
              )}
            </div>
            <div className="glass flex flex-col gap-4 rounded-2xl p-4 md:flex-row md:items-center md:justify-between">
              <p className="text-sm text-slate-300">{clip?.transcriptSnippet}</p>
              <div className="flex gap-3">
                <a
                  href={clip?.videoUrl}
                  className="inline-flex items-center gap-2 rounded-full border border-white/10 px-4 py-2 text-sm font-medium text-white transition hover:border-clipper-primary"
                >
                  <Download className="h-4 w-4" /> Download
                </a>
                <button className="inline-flex items-center gap-2 rounded-full border border-white/10 px-4 py-2 text-sm font-medium text-white transition hover:border-clipper-primary">
                  <RotateCcw className="h-4 w-4" /> Regenerate
                </button>
              </div>
            </div>
            <Dialog.Close className="self-end rounded-full border border-white/10 px-4 py-1 text-xs uppercase tracking-[0.35em] text-slate-300 hover:border-clipper-primary">
              Close
            </Dialog.Close>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
