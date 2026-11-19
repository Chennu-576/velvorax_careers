"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { API_BASE_URL } from "@/lib/api";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setMessage(null);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim() }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Unable to submit the password reset request.");
      }
      setMessage(data.message);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to submit the password reset request."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[70vh] flex items-center justify-center px-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md rounded-3xl border border-brand-border bg-white p-8 shadow-md"
      >
        <h1 className="text-2xl font-extrabold text-brand-deepNavy">Forgot Password</h1>
        <p className="mt-2 text-sm text-brand-textSecondary">
          Enter your account email to request a password reset link.
        </p>
        {error && <p role="alert" className="mt-4 rounded-xl bg-red-50 p-3 text-xs text-brand-error">{error}</p>}
        {message && <p role="status" className="mt-4 rounded-xl bg-emerald-50 p-3 text-xs text-brand-success">{message}</p>}
        <label htmlFor="reset-email" className="mt-5 block text-xs font-bold text-brand-deepNavy">
          Email address
        </label>
        <input
          id="reset-email"
          type="email"
          required
          autoComplete="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          className="mt-1 w-full rounded-xl border border-brand-border px-3.5 py-3 text-sm"
        />
        <button
          type="submit"
          disabled={loading}
          className="mt-5 w-full rounded-xl bg-brand-yellow px-5 py-3 text-sm font-extrabold text-brand-deepNavy disabled:opacity-50"
        >
          {loading ? "Submitting..." : "Request reset link"}
        </button>
        <Link href="/login" className="mt-4 block text-center text-xs font-bold text-brand-corpBlue">
          Back to login
        </Link>
      </form>
    </div>
  );
}
