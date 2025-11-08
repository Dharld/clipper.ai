import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';

interface HeroSectionProps {
  onGetStarted: () => void;
}

export function HeroSection({ onGetStarted }: HeroSectionProps) {
  return (
    <section className="flex flex-col gap-10">
      <motion.div
        initial={{ opacity: 0, y: 32 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, ease: 'easeOut' }}
        className="flex flex-col gap-6"
      >
        <span className="text-sm uppercase tracking-[0.35em] text-clipper-accent">Introducing Clipper.ai</span>
        <h1 className="text-4xl font-semibold leading-tight md:text-6xl">
          Turn your podcast into viral clips. Instantly.
        </h1>
        <p className="max-w-2xl text-lg text-slate-300">
          Upload a full episode, grab coffee, and return to ready-to-share clips. No clutter, no busywork —
          just the moments that matter.
        </p>
      </motion.div>

      <motion.div
        className="flex flex-col gap-4 md:flex-row"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <button
          onClick={onGetStarted}
          className="inline-flex items-center justify-center rounded-full bg-gradient-to-r from-clipper-primary to-clipper-secondary px-8 py-4 text-base font-semibold text-white shadow-glow transition hover:opacity-90"
        >
          Upload a video → Watch it get clipped
        </button>
        <div className="glass flex flex-1 items-center justify-between rounded-3xl px-6 py-5">
          <div className="space-y-1">
            <p className="text-sm uppercase tracking-[0.35em] text-slate-400">Live status</p>
            <p className="text-base text-slate-200">Analyzing audio… detecting highlights…</p>
          </div>
          <ArrowRight className="hidden h-5 w-5 text-clipper-accent md:block" />
        </div>
      </motion.div>

      <motion.div
        className="relative overflow-hidden rounded-3xl border border-white/5 bg-gradient-glass p-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.35 }}
      >
        <div className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_20%_20%,rgba(109,93,252,0.35),transparent_55%),radial-gradient(circle_at_80%_10%,rgba(93,205,241,0.25),transparent_45%)]" />
        <div className="flex flex-col gap-6 md:flex-row md:items-center">
          <div className="space-y-3 md:w-1/2">
            <p className="text-sm uppercase tracking-[0.25em] text-clipper-accent">How it works</p>
            <h2 className="text-2xl font-semibold">AI editing that stays out of your way.</h2>
            <p className="text-slate-300">
              Clipper listens for peaks, cuts out filler, and returns cinematic clips with transcripts, scores, and
              instant downloads — all while keeping the interface clean and calm.
            </p>
          </div>
          <div className="md:w-1/2">
            <div className="glass grid grid-cols-2 gap-4 rounded-3xl p-6">
              {['Magic highlights', 'Text-based editing', 'Instant downloads', 'Waveform intelligence'].map(
                (feature) => (
                  <div key={feature} className="space-y-2 rounded-2xl border border-white/5 bg-white/5 p-4">
                    <p className="text-sm font-medium text-white">{feature}</p>
                    <p className="text-xs text-slate-400">Powered by Clipper’s calm AI engine.</p>
                  </div>
                )
              )}
            </div>
          </div>
        </div>
      </motion.div>
    </section>
  );
}
