"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Menu, X, UserCircle, LogOut, LayoutDashboard, ArrowRight } from "lucide-react";
import Logo from "./Logo";
import { getAuthToken, getAuthUser, clearAuth, User } from "@/lib/api";

export default function Header() {
  const pathname = usePathname();
  const router = useRouter();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    setUser(getAuthUser());
  }, [pathname]);

  const handleLogout = () => {
    clearAuth();
    setUser(null);
    router.push("/login");
  };

  const navLinks = [
    { label: "Home", href: "/" },
    { label: "About", href: "/about" },
    { label: "Browse Jobs", href: "/jobs" },
    { label: "IT Jobs", href: "/it-jobs" },
    { label: "Non-IT Jobs", href: "/non-it-jobs" },
    { label: "Job Categories", href: "/job-categories" },
    { label: "Global Opportunities", href: "/global-jobs" },
  ];

  const getDashboardUrl = () => {
    if (!user) return "/login";
    if (user.role === "ADMIN" || user.role === "SUPER_ADMIN") return "/admin/dashboard";
    if (user.role === "RECRUITER") return "/recruiter/dashboard";
    return "/candidate/dashboard";
  };

  return (
    <header className="sticky top-0 z-50 w-full bg-white/95 backdrop-blur-md border-b border-brand-border shadow-xs transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        {/* Left Side: VELVORAX Logo */}
        <div className="flex-shrink-0">
          <Logo />
        </div>

        {/* Center / Right Nav Links (Desktop) */}
        <nav className="hidden lg:flex items-center gap-1 xl:gap-2">
          {navLinks.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`relative px-3 py-2 text-sm font-semibold transition-colors rounded-lg ${
                  isActive
                    ? "text-brand-deepNavy font-bold"
                    : "text-brand-textSecondary hover:text-brand-deepNavy hover:bg-brand-softBg"
                }`}
              >
                {link.label}
                {isActive && (
                  <span className="absolute bottom-0 left-3 right-3 h-0.5 bg-brand-yellow rounded-full" />
                )}
              </Link>
            );
          })}
        </nav>

        {/* Right-side Actions */}
        <div className="hidden lg:flex items-center gap-3">
          {user ? (
            <div className="flex items-center gap-3">
              <Link
                href={getDashboardUrl()}
                className="flex items-center gap-2 px-4 py-2 text-sm font-semibold bg-brand-deepNavy text-white rounded-xl shadow-xs hover:bg-brand-secondaryNavy transition-all"
              >
                <LayoutDashboard className="w-4 h-4 text-brand-yellow" />
                <span>
                  {user.role === "ADMIN" || user.role === "SUPER_ADMIN"
                    ? "Admin Portal"
                    : user.role === "RECRUITER"
                    ? "Recruiter Portal"
                    : "My Dashboard"}
                </span>
              </Link>
              <button
                onClick={handleLogout}
                className="p-2 text-brand-textSecondary hover:text-brand-error transition-colors"
                title="Logout"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <Link
                href="/login"
                className="px-4 py-2 text-sm font-semibold text-brand-deepNavy hover:text-brand-corpBlue transition-colors"
              >
                Login
              </Link>
              <Link
                href="/register"
                className="flex items-center gap-1.5 px-4 py-2 text-sm font-bold bg-brand-yellow text-brand-deepNavy rounded-xl shadow-xs hover:bg-brand-yellowHover transition-all transform active:scale-95"
              >
                <span>Create Account</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          )}
        </div>

        {/* Mobile Menu Hamburger */}
        <div className="lg:hidden flex items-center">
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-lg text-brand-textPrimary hover:bg-brand-softBg"
            aria-label="Toggle mobile menu"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-b border-brand-border bg-white px-4 pt-2 pb-6 space-y-2 animate-fadeIn">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              onClick={() => setMobileMenuOpen(false)}
              className={`block px-3 py-2.5 rounded-lg text-base font-medium ${
                pathname === link.href
                  ? "bg-brand-yellow/15 text-brand-deepNavy font-bold"
                  : "text-brand-textPrimary hover:bg-brand-softBg"
              }`}
            >
              {link.label}
            </Link>
          ))}
          <div className="pt-4 border-t border-brand-border flex flex-col gap-2">
            {user ? (
              <>
                <Link
                  href={getDashboardUrl()}
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-bold bg-brand-deepNavy text-white rounded-xl shadow-xs"
                >
                  <LayoutDashboard className="w-4 h-4 text-brand-yellow" />
                  <span>Enter Dashboard</span>
                </Link>
                <button
                  onClick={() => {
                    setMobileMenuOpen(false);
                    handleLogout();
                  }}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-brand-error hover:bg-red-50 rounded-lg"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Logout</span>
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full text-center px-4 py-2.5 text-sm font-semibold border border-brand-border rounded-xl"
                >
                  Login
                </Link>
                <Link
                  href="/register"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full text-center px-4 py-2.5 text-sm font-bold bg-brand-yellow text-brand-deepNavy rounded-xl shadow-xs"
                >
                  Create Account
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
