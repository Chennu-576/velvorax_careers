"use client";

import { Suspense, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { API_BASE_URL } from "@/lib/api";

function ResetPasswordForm() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setMessage(null);
    if (!token) {
      setError("Invalid password reset link.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/auth/reset-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, new_password: password, confirm_password: confirmPassword }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Password reset failed.");
      setMessage(data.message || "Password updated successfully.");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[70vh] flex items-center justify-center px-4">
      <form onSubmit={handleSubmit} className="w-full max-w-md rounded-3xl border border-brand-border bg-white p-8 shadow-md">
        <h1 className="text-2xl font-extrabold text-brand-deepNavy">Reset Password</h1>
        {error && <p className="mt-4 rounded-xl bg-red-50 p-3 text-xs text-brand-error">{error}</p>}
        {message && <p className="mt-4 rounded-xl bg-emerald-50 p-3 text-xs text-brand-success">{message}</p>}
        <label className="mt-5 block text-xs font-bold text-brand-deepNavy">New password</label>
        <input type="password" required minLength={8} maxLength={72} value={password} onChange={(e) => setPassword(e.target.value)} className="mt-1 w-full rounded-xl border border-brand-border px-3.5 py-3 text-sm" />
        <label className="mt-4 block text-xs font-bold text-brand-deepNavy">Confirm password</label>
        <input type="password" required minLength={8} maxLength={72} value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} className="mt-1 w-full rounded-xl border border-brand-border px-3.5 py-3 text-sm" />
        <button disabled={loading} className="mt-5 w-full rounded-xl bg-brand-yellow px-5 py-3 text-sm font-extrabold text-brand-deepNavy">
          {loading ? "Updating..." : "Reset Password"}
        </button>
        <Link href="/login" className="mt-4 block text-center text-xs font-bold text-brand-corpBlue">Back to login</Link>
      </form>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<div className="p-12 text-center">Loading password reset...</div>}>
      <ResetPasswordForm />
    </Suspense>
  );
}
