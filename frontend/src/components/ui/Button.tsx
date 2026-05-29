import Link from "next/link";
import type { ButtonHTMLAttributes, ReactNode } from "react";

type Variant = "primary" | "secondary" | "ghost";

type CommonProps = {
  children: ReactNode;
  className?: string;
  variant?: Variant;
};

type ButtonProps = CommonProps &
  ButtonHTMLAttributes<HTMLButtonElement> & { href?: never };

type LinkButtonProps = CommonProps & {
  href: string;
  onClick?: never;
};

const variants: Record<Variant, string> = {
  primary:
    "bg-[#F4F4F5] text-[#0B0F14] hover:bg-white hover:shadow-[0_10px_30px_rgba(255,255,255,0.08)]",
  secondary:
    "border border-white/[0.12] bg-white/[0.04] text-[#F4F4F5] hover:border-white/[0.2] hover:bg-white/[0.08]",
  ghost: "text-[#A1A1AA] hover:bg-white/[0.05] hover:text-[#F4F4F5]",
};

export function Button(props: ButtonProps | LinkButtonProps) {
  const { children, variant = "primary", className = "", ...rest } = props;
  const styles = `inline-flex items-center justify-center rounded-full px-6 py-3.5 text-sm font-semibold transition duration-300 ${variants[variant]} ${className}`;

  if ("href" in rest && rest.href) {
    return (
      <Link className={styles} href={rest.href}>
        {children}
      </Link>
    );
  }

  return (
    <button className={styles} {...(rest as ButtonHTMLAttributes<HTMLButtonElement>)}>
      {children}
    </button>
  );
}
