const logos = ['The Verge', 'NPR', 'The New York Times', 'Morning Brew', 'HubSpot Podcasts', 'Shopify Studios'];

export function TrustedBySection() {
  return (
    <section className="glass rounded-3xl p-10">
      <p className="text-center text-xs uppercase tracking-[0.35em] text-slate-400">Trusted by teams who sound good</p>
      <div className="mt-8 grid grid-cols-2 gap-6 text-center text-sm font-medium text-slate-300 md:grid-cols-6">
        {logos.map((logo) => (
          <span key={logo} className="rounded-full border border-white/5 bg-white/5 px-4 py-3">
            {logo}
          </span>
        ))}
      </div>
    </section>
  );
}
