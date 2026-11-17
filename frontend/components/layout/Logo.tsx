import React from "react";
import Link from "next/link";

interface LogoProps {
  className?: string;
  variant?: "dark" | "light";
}

export default function Logo({ className = "", variant = "dark" }: LogoProps) {
  const isLight = variant === "light";

  return (
    <Link href="/" className={`flex items-center gap-2.5 group ${className}`}>
      {/* Official Geometric Monogram Icon */}
      <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-brand-deepNavy border border-brand-border/20 shadow-md group-hover:scale-105 transition-all">
        <svg
          viewBox="0 0 40 40"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="w-6 h-6"
        >
          {/* V shaped dynamic polygon with #FACC15 primary accent */}
          <path
            d="M8 10L20 32L32 10H25L20 22L15 10H8Z"
            fill="#FACC15"
          />
          <path
            d="M17 10L20 16L23 10H17Z"
            fill="#FFFFFF"
            fillOpacity="0.8"
          />
        </svg>
        {/* Glow point */}
        <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-brand-yellow animate-pulse" />
      </div>

      <div className="flex flex-col">
        <div className="flex items-center tracking-wider">
          <span
            className={`font-black text-xl tracking-tight ${
              isLight ? "text-white" : "text-brand-deepNavy"
            }`}
          >
            VELVORAX
          </span>
          <span className="text-brand-yellow font-extrabold text-xl ml-0.5">.</span>
        </div>
        <span
          className={`text-[9px] uppercase tracking-widest font-semibold -mt-1 ${
            isLight ? "text-slate-400" : "text-brand-textSecondary"
          }`}
        >
          Careers Portal
        </span>
      </div>
    </Link>
  );
}
