import { useState } from 'react';
import { HeroSection } from './sections/HeroSection';
import { FeaturesSection } from './sections/FeaturesSection';
import { TrustedBySection } from './sections/TrustedBySection';
import { DashboardSection } from './sections/DashboardSection';
import { FooterSection } from './sections/FooterSection';
import { ClipPreviewDialog } from './components/ClipPreviewDialog';
import { SuggestedClip } from './types';

function App() {
  const [activeClip, setActiveClip] = useState<SuggestedClip | null>(null);

  return (
    <div className="min-h-screen bg-[#0B0C10] text-slate-100">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-32 px-6 pb-24 pt-12 md:px-12">
        <HeroSection onGetStarted={() => {
          const dashboard = document.getElementById('dashboard');
          if (dashboard) {
            dashboard.scrollIntoView({ behavior: 'smooth' });
          }
        }} />
        <FeaturesSection />
        <TrustedBySection />
        <DashboardSection onOpenClip={setActiveClip} />
      </div>
      <FooterSection />
      <ClipPreviewDialog clip={activeClip} onOpenChange={(open) => !open && setActiveClip(null)} />
    </div>
  );
}

export default App;
