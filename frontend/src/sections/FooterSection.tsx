export function FooterSection() {
  return (
    <footer className="border-t border-white/5 bg-[#050507] py-10">
      <div className="mx-auto flex w-full max-w-6xl flex-col items-center justify-between gap-4 px-6 text-xs text-slate-500 md:flex-row md:px-12">
        <p>© {new Date().getFullYear()} Clipper.ai — Crafted for calm creators.</p>
        <nav className="flex gap-4">
          {['Projects', 'Exports', 'Settings', 'Privacy'].map((item) => (
            <a key={item} href="#" className="transition hover:text-clipper-primary">
              {item}
            </a>
          ))}
        </nav>
      </div>
    </footer>
  );
}
