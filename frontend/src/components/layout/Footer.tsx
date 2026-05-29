import { BrandLogo } from "@/components/layout/BrandLogo";

export function Footer() {
  return (
    <footer className="border-t border-white/[0.07] px-6 py-9 text-sm text-[#A1A1AA] lg:px-8">
      <div className="mx-auto flex max-w-7xl flex-col justify-between gap-5 sm:flex-row sm:items-center">
        <BrandLogo compact />
        <p>Crossfit biomechanics analysis powered by intelligent video processing.</p>
      </div>
    </footer>
  );
}
