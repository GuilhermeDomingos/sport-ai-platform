import Link from "next/link";

import { BrandLogo } from "@/components/layout/BrandLogo";
import { Button } from "@/components/ui/Button";

export function Header() {
  return (
    <header className="sticky top-0 z-30 border-b border-white/[0.06] bg-[#0B0F14]/86 backdrop-blur-xl">
      <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-6 lg:px-8">
        <Link className="flex items-center gap-3" href="/" aria-label="AXON Sport AI">
          <BrandLogo />
          <span className="hidden text-[0.62rem] font-medium uppercase tracking-[0.26em] text-[#A1A1AA] xl:inline">
            Sport Intelligence
          </span>
        </Link>
        <nav className="hidden items-center gap-9 text-sm text-[#A1A1AA] md:flex">
          <Link className="transition hover:text-[#F4F4F5]" href="/#como-funciona">
            Como funciona
          </Link>
          <Link className="transition hover:text-[#F4F4F5]" href="/#metricas">
            Métricas
          </Link>
          <Link className="transition hover:text-[#F4F4F5]" href="/#upload">
            Upload
          </Link>
        </nav>
        <Button className="px-5 py-3" href="/#upload">
          Analisar treino
        </Button>
      </div>
    </header>
  );
}
