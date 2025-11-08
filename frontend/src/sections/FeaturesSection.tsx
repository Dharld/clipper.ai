const features = [
  {
    title: 'Magic Highlights',
    description:
      'Clipper pinpoints the spikes in energy, the laugh-out-loud moments, and the quotable lines, packaging them into perfect social snippets.',
    metric: '3-5 clips'
  },
  {
    title: 'Text-first Editing',
    description:
      'Skim the transcript, tap to trim, regenerate with a prompt. No timeline anxiety — just words guiding the edit.',
    metric: '90% faster'
  },
  {
    title: 'Instant Downloads',
    description:
      'Export vertical, square, or wide. Captions burned in. Ready for TikTok, Reels, YouTube, and your newsletter.',
    metric: 'Multi-format'
  }
];

export function FeaturesSection() {
  return (
    <section className="flex flex-col gap-10">
      <div className="flex flex-col gap-3">
        <h2 className="text-3xl font-semibold md:text-4xl">The calmest way to cut a show.</h2>
        <p className="max-w-2xl text-slate-300">
          Built for podcasters, streamers, and creators who want premium clips without drowning in timelines or noisy
          dashboards.
        </p>
      </div>
      <div className="grid gap-6 md:grid-cols-3">
        {features.map((feature) => (
          <div key={feature.title} className="glass flex flex-col gap-4 rounded-3xl p-6">
            <p className="text-sm uppercase tracking-[0.2em] text-clipper-accent">{feature.metric}</p>
            <h3 className="text-xl font-semibold">{feature.title}</h3>
            <p className="text-sm text-slate-300">{feature.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
