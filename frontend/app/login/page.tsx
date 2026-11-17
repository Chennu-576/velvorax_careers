"use client";

import React, { useState, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Shield, Lock, Mail, Eye, EyeOff, AlertCircle, ArrowRight, UserCheck } from "lucide-react";
import Logo from "@/components/layout/Logo";
import { API_BASE_URL, saveAuth } from "@/lib/api";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const returnUrl = searchParams.get("redirect");

  // Single common role selector with 3 options: Admin, Recruiter/HR, Candidate
  const [selectedRole, setSelectedRole] = useState<"Admin" | "Recruiter/HR" | "Candidate">("Candidate");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: email.trim(),
          password,
          role: selectedRole,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Authentication failed. Please verify credentials and selected portal.");
      }

      // Save token & user profile
      saveAuth(data.access_token, data.user);

      // Role-based redirects per Section 6.1
      if (returnUrl && returnUrl.startsWith("/")) {
        router.push(returnUrl);
      } else {
        if (data.role === "ADMIN" || data.role === "SUPER_ADMIN") {
          router.push("/admin/dashboard");
        } else if (data.role === "RECRUITER") {
          router.push("/recruiter/dashboard");
        } else {
          router.push("/candidate/dashboard");
        }
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md bg-white rounded-3xl border border-brand-border p-8 shadow-md">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="flex justify-center mb-3">
            <Logo />
          </div>
          <h1 className="text-2xl font-extrabold text-brand-deepNavy">
            Sign In to VELVORAX
          </h1>
          <p className="text-xs text-brand-textSecondary mt-1">
            One unified portal for candidates, recruiters, and platform administrators.
          </p>
        </div>

        {/* Unified Role Selector (Section 6.1 mandatory requirement) */}
        <div className="mb-6">
          <label className="block text-xs font-bold uppercase tracking-wider text-brand-deepNavy mb-2">
            Select Your Account Role
          </label>
          <div className="grid grid-cols-3 gap-1.5 p-1 bg-brand-softBg rounded-2xl border border-brand-border">
            {(["Candidate", "Recruiter/HR", "Admin"] as const).map((role) => (
              <button
                key={role}
                type="button"
                onClick={() => {
                  setSelectedRole(role);
                  setError(null);
                }}
                className={`py-2 text-xs font-bold rounded-xl transition-all ${
                  selectedRole === role
                    ? "bg-brand-deepNavy text-brand-yellow shadow-xs"
                    : "text-brand-textSecondary hover:text-brand-deepNavy"
                }`}
              >
                {role}
              </button>
            ))}
          </div>
          <p className="text-[11px] text-slate-500 mt-1.5 text-center">
            Logging in as: <strong className="text-brand-deepNavy">{selectedRole}</strong>
          </p>
        </div>

        {error && (
          <div className="mb-5 p-3.5 bg-red-50 border border-red-200 text-brand-error rounded-xl text-xs flex items-start gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <span className="leading-snug">{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <div>
            <label className="block font-bold text-brand-deepNavy mb-1">
              Email Address
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@company.com"
                className="w-full pl-10 pr-3.5 py-3 rounded-xl border border-brand-border focus:outline-brand-yellow text-sm font-medium"
              />
            </div>
          </div>

          <div>
            <label className="block font-bold text-brand-deepNavy mb-1">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type={showPassword ? "text" : "password"}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full pl-10 pr-10 py-3 rounded-xl border border-brand-border focus:outline-brand-yellow text-sm font-medium"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-brand-deepNavy"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <div className="flex items-center justify-between text-xs pt-1">
            <label className="flex items-center gap-1.5 text-brand-textSecondary cursor-pointer">
              <input type="checkbox" className="accent-brand-yellow" defaultChecked />
              <span>Remember me</span>
            </label>
            <span className="text-brand-corpBlue font-semibold hover:underline cursor-pointer">
              Forgot password?
            </span>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-brand-yellow hover:bg-brand-yellowHover text-brand-deepNavy font-extrabold text-sm rounded-xl shadow-xs transition-all active:scale-98 flex items-center justify-center gap-2 mt-2"
          >
            <span>{loading ? "Verifying Credentials..." : `Login as ${selectedRole}`}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="mt-6 pt-5 border-t border-brand-border text-center text-xs text-brand-textSecondary">
          Don&apos;t have an account yet?{" "}
          <Link href="/register" className="font-bold text-brand-deepNavy hover:underline">
            Register Here
          </Link>
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="p-12 text-center">Loading authentication...</div>}>
      <LoginForm />
    </Suspense>
  );
}
