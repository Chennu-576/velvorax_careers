"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { User, Building, Mail, Lock, Phone, MapPin, AlertCircle, ArrowRight, CheckCircle2 } from "lucide-react";
import Logo from "@/components/layout/Logo";
import { API_BASE_URL } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();

  // Exactly two selectable types per Section 6.2: Candidate or Recruiter/HR
  const [accountType, setAccountType] = useState<"Candidate" | "Recruiter/HR">("Candidate");

  // Common & Candidate state
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [country, setCountry] = useState("India");
  const [state, setState] = useState("Telangana");
  const [city, setCity] = useState("Hyderabad");

  // Recruiter specific state
  const [companyName, setCompanyName] = useState("");
  const [companyWebsite, setCompanyWebsite] = useState("");
  const [companyGstin, setCompanyGstin] = useState("");
  const [companyCin, setCompanyCin] = useState("");
  const [companyLocation, setCompanyLocation] = useState("Hyderabad, India");
  const [designation, setDesignation] = useState("Talent Acquisition Specialist");

  const [termsAccepted, setTermsAccepted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (!termsAccepted) {
      setError("You must accept the terms and privacy conditions to proceed.");
      return;
    }

    setLoading(true);

    try {
      if (accountType === "Candidate") {
        const res = await fetch(`${API_BASE_URL}/auth/register/candidate`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            full_name: fullName.trim(),
            email: email.trim(),
            phone: phone.trim() || undefined,
            password,
            confirm_password: confirmPassword,
            country,
            state,
            city,
            terms_accepted: termsAccepted,
          }),
        });

        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.detail || "Candidate registration failed.");
        }

        router.push(`/login?registered=1&email=${encodeURIComponent(data.email)}&verify=${data.verification_required ? "1" : "0"}`);
      } else {
        // Recruiter Registration
        const res = await fetch(`${API_BASE_URL}/auth/register/recruiter`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            full_name: fullName.trim(),
            work_email: email.trim(),
            phone: phone.trim() || undefined,
            company_name: companyName.trim(),
            company_website: companyWebsite.trim() || undefined,
            company_gstin: companyGstin.trim() || undefined,
            company_cin: companyCin.trim() || undefined,
            company_location: companyLocation.trim(),
            designation: designation.trim(),
            password,
            confirm_password: confirmPassword,
            terms_accepted: termsAccepted,
          }),
        });

        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.detail || "Recruiter registration failed.");
        }

        router.push(`/login?registered=1&email=${encodeURIComponent(data.email)}&verify=${data.verification_required ? "1" : "0"}`);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-xl bg-white rounded-3xl border border-brand-border p-8 shadow-md">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="flex justify-center mb-3">
            <Logo />
          </div>
          <h1 className="text-2xl font-extrabold text-brand-deepNavy">
            Create Your VELVORAX Account
          </h1>
          <p className="text-xs text-brand-textSecondary mt-1">
            Join thousands of professionals and hiring organizations on our unified platform.
          </p>
        </div>

        {/* Unified Registration Type Selector (Section 6.2 requirement) */}
        <div className="mb-6">
          <label className="block text-xs font-bold uppercase tracking-wider text-brand-deepNavy mb-2">
            Register As
          </label>
          <div className="grid grid-cols-2 gap-2 p-1.5 bg-brand-softBg rounded-2xl border border-brand-border">
            <button
              type="button"
              onClick={() => {
                setAccountType("Candidate");
                setError(null);
              }}
              className={`py-3 px-4 rounded-xl font-bold text-xs flex items-center justify-center gap-2 transition-all ${
                accountType === "Candidate"
                  ? "bg-brand-deepNavy text-brand-yellow shadow-xs"
                  : "text-brand-textSecondary hover:text-brand-deepNavy"
              }`}
            >
              <User className="w-4 h-4" />
              <span>Job Seeker / Candidate</span>
            </button>

            <button
              type="button"
              onClick={() => {
                setAccountType("Recruiter/HR");
                setError(null);
              }}
              className={`py-3 px-4 rounded-xl font-bold text-xs flex items-center justify-center gap-2 transition-all ${
                accountType === "Recruiter/HR"
                  ? "bg-brand-deepNavy text-brand-yellow shadow-xs"
                  : "text-brand-textSecondary hover:text-brand-deepNavy"
              }`}
            >
              <Building className="w-4 h-4" />
              <span>Recruiter / HR Partner</span>
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-5 p-3.5 bg-red-50 border border-red-200 text-brand-error rounded-xl text-xs flex items-start gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <span className="leading-snug">{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          {/* Full Name & Email */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
            <div>
              <label className="block font-bold text-brand-deepNavy mb-1">
                Full Name
              </label>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="e.g. Rahul Sharma"
                className="w-full px-3.5 py-2.5 rounded-xl border border-brand-border focus:outline-brand-yellow text-xs font-medium"
              />
            </div>

            <div>
              <label className="block font-bold text-brand-deepNavy mb-1">
                {accountType === "Candidate" ? "Email Address" : "Work Email"}
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder={accountType === "Candidate" ? "rahul@email.com" : "rahul@company.com"}
                className="w-full px-3.5 py-2.5 rounded-xl border border-brand-border focus:outline-brand-yellow text-xs font-medium"
              />
            </div>
          </div>

          {/* Phone */}
          <div>
            <label className="block font-bold text-brand-deepNavy mb-1">
              Phone Number
            </label>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+91 9985201116"
              className="w-full px-3.5 py-2.5 rounded-xl border border-brand-border focus:outline-brand-yellow text-xs font-medium"
            />
          </div>

          {/* Conditional Recruiter Company Fields */}
          {accountType === "Recruiter/HR" && (
            <div className="space-y-3.5 p-4 bg-brand-softBg rounded-2xl border border-brand-border">
              <span className="text-xs font-bold text-brand-corpBlue uppercase tracking-wider block">
                Company & Business Information
              </span>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold text-brand-deepNavy mb-1">
                    Company Name
                  </label>
                  <input
                    type="text"
                    required
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    placeholder="e.g. VELVORAX Solutions"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-brand-border bg-white focus:outline-brand-yellow text-xs font-medium"
                  />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block font-bold text-brand-deepNavy mb-1">GSTIN (optional)</label>
                    <input
                      type="text"
                      maxLength={15}
                      value={companyGstin}
                      onChange={(e) => setCompanyGstin(e.target.value.toUpperCase())}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-brand-border bg-white text-xs font-medium"
                    />
                  </div>
                  <div>
                    <label className="block font-bold text-brand-deepNavy mb-1">CIN (optional)</label>
                    <input
                      type="text"
                      maxLength={21}
                      value={companyCin}
                      onChange={(e) => setCompanyCin(e.target.value.toUpperCase())}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-brand-border bg-white text-xs font-medium"
                    />
                  </div>
                </div>

                <div>
                  <label className="block font-bold text-brand-deepNavy mb-1">
                    Company Website
                  </label>
                  <input
                    type="url"
                    value={companyWebsite}
                    onChange={(e) => setCompanyWebsite(e.target.value)}
                    placeholder="https://company.com"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-brand-border bg-white focus:outline-brand-yellow text-xs font-medium"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold text-brand-deepNavy mb-1">
                    Your Designation
                  </label>
                  <input
                    type="text"
                    required
                    value={designation}
                    onChange={(e) => setDesignation(e.target.value)}
                    placeholder="e.g. Lead Talent Acquisition"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-brand-border bg-white focus:outline-brand-yellow text-xs font-medium"
                  />
                </div>

                <div>
                  <label className="block font-bold text-brand-deepNavy mb-1">
                    Headquarters / Location
                  </label>
                  <input
                    type="text"
                    required
                    value={companyLocation}
                    onChange={(e) => setCompanyLocation(e.target.value)}
                    placeholder="Hyderabad, India"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-brand-border bg-white focus:outline-brand-yellow text-xs font-medium"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Candidate Location Fields */}
          {accountType === "Candidate" && (
            <div className="grid grid-cols-3 gap-2.5">
              <div>
                <label className="block font-bold text-brand-deepNavy mb-1">Country</label>
                <input
                  type="text"
                  value={country}
                  onChange={(e) => setCountry(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-brand-border text-xs"
                />
              </div>
              <div>
                <label className="block font-bold text-brand-deepNavy mb-1">State</label>
                <input
                  type="text"
                  value={state}
                  onChange={(e) => setState(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-brand-border text-xs"
                />
              </div>
              <div>
                <label className="block font-bold text-brand-deepNavy mb-1">City</label>
                <input
                  type="text"
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-brand-border text-xs"
                />
              </div>
            </div>
          )}

          {/* Passwords */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
            <div>
              <label className="block font-bold text-brand-deepNavy mb-1">
                Password
              </label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                minLength={8}
                maxLength={72}
                placeholder="At least 8 characters"
                className="w-full px-3.5 py-2.5 rounded-xl border border-brand-border focus:outline-brand-yellow text-xs font-medium"
              />
            </div>

            <div>
              <label className="block font-bold text-brand-deepNavy mb-1">
                Confirm Password
              </label>
              <input
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                minLength={8}
                maxLength={72}
                placeholder="Re-enter password"
                className="w-full px-3.5 py-2.5 rounded-xl border border-brand-border focus:outline-brand-yellow text-xs font-medium"
              />
            </div>
          </div>

          {/* Terms checkbox */}
          <div className="pt-2">
            <label className="flex items-start gap-2 text-brand-textSecondary cursor-pointer text-xs">
              <input
                type="checkbox"
                checked={termsAccepted}
                onChange={(e) => setTermsAccepted(e.target.checked)}
                className="accent-brand-yellow mt-0.5"
              />
              <span className="leading-relaxed">
                I agree to VELVORAX Careers Terms of Service, Privacy Policy, and candidate/recruiter code of conduct.
              </span>
            </label>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-brand-yellow hover:bg-brand-yellowHover text-brand-deepNavy font-extrabold text-sm rounded-xl shadow-xs transition-all active:scale-98 flex items-center justify-center gap-2 mt-4"
          >
            <span>{loading ? "Registering Account..." : `Complete ${accountType} Registration`}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="mt-6 pt-5 border-t border-brand-border text-center text-xs text-brand-textSecondary">
          Already registered?{" "}
          <Link href="/login" className="font-bold text-brand-deepNavy hover:underline">
            Sign In Here
          </Link>
        </div>
      </div>
    </div>
  );
}
