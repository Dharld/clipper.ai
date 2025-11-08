import { useRef, useState } from 'react';
import { uploadProject } from '../lib/api';
import { Loader2, UploadCloud } from 'lucide-react';

interface UploadCardProps {
  onUploaded: (projectId: string) => void;
}

export function UploadCard({ onUploaded }: UploadCardProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const file = files[0];
    setIsUploading(true);
    setError(null);
    try {
      const response = await uploadProject(file);
      onUploaded(response.projectId);
    } catch (err) {
      console.error(err);
      setError('Upload failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div
      onDragOver={(event) => {
        event.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(event) => {
        event.preventDefault();
        setIsDragging(false);
        handleFiles(event.dataTransfer.files);
      }}
      className={`glass flex flex-1 flex-col items-center justify-center rounded-3xl border-2 border-dashed border-white/10 p-8 text-center transition ${
        isDragging ? 'border-clipper-primary bg-white/10' : ''
      }`}
    >
      <UploadCloud className="h-10 w-10 text-clipper-secondary" />
      <h3 className="mt-4 text-xl font-semibold">Drag & drop your episode</h3>
      <p className="mt-2 max-w-sm text-sm text-slate-400">MP4 or MOV, under 2GB. We’ll transcribe and find your best clips.</p>
      <button
        className="mt-6 rounded-full border border-white/10 px-5 py-2 text-sm font-medium text-white transition hover:border-clipper-primary"
        onClick={() => inputRef.current?.click()}
        disabled={isUploading}
      >
        {isUploading ? (
          <span className="flex items-center gap-2">
            <Loader2 className="h-4 w-4 animate-spin" /> Uploading…
          </span>
        ) : (
          'Select a file'
        )}
      </button>
      <input
        type="file"
        accept="video/*"
        className="hidden"
        ref={inputRef}
        onChange={(event) => handleFiles(event.target.files)}
      />
      {error && <p className="mt-4 text-xs text-red-400">{error}</p>}
    </div>
  );
}
