import Image from "next/image";

import logo from "../../../codex/logo.png";

export function BrandLogo({ compact = false }: { compact?: boolean }) {
  return (
    <span
      className={`relative block shrink-0 overflow-hidden rounded-lg border border-white/10 bg-[#B8B9BB] ${
        compact ? "h-8 w-24" : "h-10 w-32"
      }`}
    >
      <Image
        alt="AXON"
        className="scale-[3.8] object-contain"
        fill
        sizes={compact ? "96px" : "128px"}
        src={logo}
      />
    </span>
  );
}
