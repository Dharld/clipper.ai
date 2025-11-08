import { clsx } from 'clsx';
import { JobProgress } from '../types';

interface StatusStepperProps {
  progress: JobProgress;
}

export function StatusStepper({ progress }: StatusStepperProps) {
  return (
    <div className="glass flex flex-wrap gap-4 rounded-3xl p-5">
      {progress.steps.map((step, index) => {
        const isActive = step.id === progress.current;
        const isCompleted = progress.steps.findIndex((s) => s.id === progress.current) > index;
        return (
          <div
            key={step.id}
            className={clsx(
              'flex flex-1 min-w-[160px] flex-col gap-1 rounded-2xl border border-white/5 px-4 py-3',
              isActive && 'border-clipper-primary bg-white/10',
              isCompleted && 'border-white/10 bg-white/5 opacity-70'
            )}
          >
            <span className="text-xs uppercase tracking-[0.25em] text-slate-400">{step.label}</span>
            <p className="text-sm text-white">{step.description}</p>
          </div>
        );
      })}
    </div>
  );
}
