"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { API_BASE_URL } from "@/lib/api";

function VerifyEmailForm() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const [status, setStatus] = useState<"loading" | "success" | "error">(token ? "loading" : "error");
  const [message, setMessage] = useState(token ? "Verifying your email..." : "Invalid verification link.");

  useEffect(() => {
    if (!token) return;

    const verify = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/auth/verify-email`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Verification failed.");
        setStatus("success");
        setMessage(data.message || "Email verified successfully.");
      } catch (error: any) {
        setStatus("error");
        setMessage(error.message);
      }

    };

    verify();
  }, [token]);

  return (
    <div className="min-h-[70vh] flex items-center justify-center px-4">
      <div className="w-full max-w-md rounded-3xl border border-brand-border bg-white p-8 text-center shadow-md">
        <h1 className="text-2xl font-extrabold text-brand-deepNavy">Email Verification</h1>
        <p className={`mt-4 text-sm ${status === "success" ? "text-brand-success" : status === "error" ? "text-brand-error" : "text-brand-textSecondary"}`}>
          {message}
        </p>
        <Link href="/login" className="mt-6 inline-flex rounded-xl bg-brand-yellow px-5 py-3 text-sm font-extrabold text-brand-deepNavy">
          Continue to Login
        </Link>
      </div>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={<div className="p-12 text-center">Verifying email...</div>}>
      <VerifyEmailForm />
    </Suspense>
  );
}
