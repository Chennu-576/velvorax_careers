"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import {
  MapPin,
  Briefcase,
  DollarSign,
  Calendar,
  Building2,
  CheckCircle2,
  Share2,
  Bookmark,
  Send,
  AlertCircle,
  FileText,
  Clock,
  ArrowLeft,
  Check
} from "lucide-react";
import { API_BASE_URL, getAuthToken, getAuthUser } from "@/lib/api";

export default function JobDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const jobSlug = params.jobSlug as string;

  const [job, setJob] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Application Modal state
  const [applyModalOpen, setApplyModalOpen] = useState(false);
  const [resumes, setResumes] = useState<any[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState<number | null>(null);
  const [coverLetter, setCoverLetter] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [appliedSuccess, setAppliedSuccess] = useState(false);
  const [applyError, setApplyError] = useState<string | null>(null);

  // Saved job state
  const [isSaved, setIsSaved] = useState(false);

  useEffect(() => {
    async function loadJob() {
      try {
        const res = await fetch(`${API_BASE_URL}/jobs/${jobSlug}`);
        if (!res.ok) {
          throw new Error("Job not found.");
        }
        const data = await res.json();
        setJob(data);
      } catch (err: any) {
        setError(err.message || "Failed to load job details.");
      } finally {
        setLoading(false);
      }
    }
    if (jobSlug) {
      loadJob();
    }
  }, [jobSlug]);

  // Load candidate resumes if logged in
  const handleOpenApplyModal = async () => {
    const token = getAuthToken();
    const user = getAuthUser();

    if (!token || !user) {
      // Redirect to unified login with return URL
      router.push(`/login?redirect=/jobs/${jobSlug}`);
      return;
    }

    if (user.role !== "CANDIDATE") {
      alert("Only registered candidate accounts can apply for job postings.");
      return;
    }

    setApplyModalOpen(true);
    setApplyError(null);

    try {
      const res = await fetch(`${API_BASE_URL}/candidates/me/resumes`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setResumes(data);
        const def = data.find((r: any) => r.is_default);
        if (def) setSelectedResumeId(def.id);
        else if (data.length > 0) setSelectedResumeId(data[0].id);
      }
    } catch (err) {
      console.error("Error loading resumes:", err);
    }
  };

  const handleApplySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setApplyError(null);

    const token = getAuthToken();
    try {
      const res = await fetch(`${API_BASE_URL}/applications`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          job_id: job.id,
          resume_id: selectedResumeId,
          cover_letter: coverLetter,
        }),
      });

      if (!res.ok) {
        const errJson = await res.json();
        throw new Error(errJson.detail || "Application submission failed.");
      }

      setAppliedSuccess(true);
    } catch (err: any) {
      setApplyError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleSaveJobToggle = async () => {
    const token = getAuthToken();
    if (!token) {
      router.push(`/login?redirect=/jobs/${jobSlug}`);
      return;
    }

    try {
      if (isSaved) {
        await fetch(`${API_BASE_URL}/candidates/me/saved-jobs/${job.id}`, {
          method: "DELETE",
          headers: { Authorization: `Bearer ${token}` },
        });
        setIsSaved(false);
      } else {
        await fetch(`${API_BASE_URL}/candidates/me/saved-jobs/${job.id}`, {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
        });
        setIsSaved(true);
      }
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center">
        <p className="text-sm font-semibold text-brand-textSecondary">
          Loading position details...
        </p>
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-20 text-center">
        <AlertCircle className="w-12 h-12 text-brand-error mx-auto mb-3" />
        <h2 className="text-xl font-bold text-brand-deepNavy">Position Unavailable</h2>
        <p className="text-xs text-brand-textSecondary mt-1">{error}</p>
        <Link
          href="/jobs"
          className="mt-6 inline-flex items-center gap-2 px-5 py-2.5 bg-brand-yellow font-bold text-xs text-brand-deepNavy rounded-xl"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Browse Active Jobs</span>
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Back button */}
      <Link
        href="/jobs"
        className="inline-flex items-center gap-1.5 text-xs font-bold text-brand-textSecondary hover:text-brand-deepNavy mb-6 transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        <span>Back to Opportunities</span>
      </Link>

      {/* Main Header Card */}
      <div className="bg-white rounded-3xl border border-brand-border p-6 sm:p-8 shadow-xs mb-8">
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-6 pb-6 border-b border-brand-border">
          <div className="flex items-start gap-4">
            <div className="w-16 h-16 rounded-2xl bg-brand-softBg border border-brand-border flex items-center justify-center overflow-hidden flex-shrink-0">
              {job.company?.logo_url ? (
                <img
                  src={job.company.logo_url}
                  alt={job.company.name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <Building2 className="w-8 h-8 text-brand-corpBlue" />
              )}
            </div>

            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-brand-deepNavy">
                  {job.company?.name || "VELVORAX Software Solutions"}
                </span>
                {job.company?.is_verified && (
                  <span title="Verified Hiring Partner">
                    <CheckCircle2 className="w-4 h-4 text-brand-success" />
                  </span>
                )}
              </div>
              <h1 className="text-2xl sm:text-3xl font-black text-brand-deepNavy mt-1">
                {job.title}
              </h1>
              <div className="flex flex-wrap items-center gap-4 text-xs text-brand-textSecondary mt-2">
                <span className="flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5 text-slate-400" />
                  {job.city ? `${job.city}, ${job.country}` : job.country}
                </span>
                <span className="flex items-center gap-1">
                  <Briefcase className="w-3.5 h-3.5 text-slate-400" />
                  {job.employment_type} • {job.work_arrangement}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5 text-slate-400" />
                  Posted {new Date(job.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>

          {/* Action CTAs */}
          <div className="flex items-center gap-3 flex-shrink-0">
            <button
              onClick={handleSaveJobToggle}
              className={`p-3 rounded-xl border transition-all ${
                isSaved
                  ? "bg-brand-yellow/20 text-brand-deepNavy border-brand-yellow"
                  : "bg-white text-slate-400 border-brand-border hover:text-brand-deepNavy"
              }`}
              title={isSaved ? "Saved" : "Save Job"}
            >
              <Bookmark className="w-5 h-5" />
            </button>
            <button
              onClick={handleOpenApplyModal}
              className="px-7 py-3 bg-brand-yellow hover:bg-brand-yellowHover text-brand-deepNavy font-extrabold text-sm rounded-xl shadow-xs transition-all active:scale-95"
            >
              Apply for this Position
            </button>
          </div>
        </div>

        {/* Highlight Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-6 text-xs">
          <div className="p-3.5 bg-brand-softBg rounded-xl">
            <span className="text-brand-textSecondary block">Experience Level</span>
            <span className="font-bold text-brand-deepNavy text-sm mt-0.5 block">
              {job.experience_level} ({job.experience_min_years}+ yrs)
            </span>
          </div>

          <div className="p-3.5 bg-brand-softBg rounded-xl">
            <span className="text-brand-textSecondary block">Offered Compensation</span>
            <span className="font-bold text-brand-deepNavy text-sm mt-0.5 block">
              {job.salary_min
                ? `${job.salary_currency} ${job.salary_min.toLocaleString()} - ${
                    job.salary_max ? job.salary_max.toLocaleString() : ""
                  }`
                : "Negotiable / Standard"}
            </span>
          </div>

          <div className="p-3.5 bg-brand-softBg rounded-xl">
            <span className="text-brand-textSecondary block">Work Arrangement</span>
            <span className="font-bold text-brand-deepNavy text-sm mt-0.5 block">
              {job.work_arrangement}
            </span>
          </div>

          <div className="p-3.5 bg-brand-softBg rounded-xl">
            <span className="text-brand-textSecondary block">Vacancies</span>
            <span className="font-bold text-brand-deepNavy text-sm mt-0.5 block">
              {job.openings} Openings
            </span>
          </div>
        </div>
      </div>

      {/* Main Content Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Job Description & Qualifications */}
        <div className="lg:col-span-2 space-y-8 bg-white p-8 rounded-3xl border border-brand-border shadow-xs">
          <div>
            <h3 className="text-base font-bold text-brand-deepNavy uppercase tracking-wider mb-3">
              Role Overview
            </h3>
            <p className="text-sm text-brand-textPrimary leading-relaxed whitespace-pre-line">
              {job.description}
            </p>
          </div>

          {job.responsibilities && (
            <div>
              <h3 className="text-base font-bold text-brand-deepNavy uppercase tracking-wider mb-3">
                Key Responsibilities
              </h3>
              <p className="text-sm text-brand-textPrimary leading-relaxed whitespace-pre-line">
                {job.responsibilities}
              </p>
            </div>
          )}

          {job.qualifications && (
            <div>
              <h3 className="text-base font-bold text-brand-deepNavy uppercase tracking-wider mb-3">
                Required Qualifications & Skills
              </h3>
              <p className="text-sm text-brand-textPrimary leading-relaxed whitespace-pre-line">
                {job.qualifications}
              </p>
            </div>
          )}

          {job.benefits && (
            <div>
              <h3 className="text-base font-bold text-brand-deepNavy uppercase tracking-wider mb-3">
                Compensation & Perks
              </h3>
              <p className="text-sm text-brand-textPrimary leading-relaxed whitespace-pre-line">
                {job.benefits}
              </p>
            </div>
          )}
        </div>

        {/* Right Column: Company Info & Required Skills */}
        <div className="space-y-6">
          {/* Skills Pill Box */}
          <div className="bg-white p-6 rounded-2xl border border-brand-border shadow-xs">
            <h4 className="text-xs font-bold uppercase tracking-wider text-brand-deepNavy mb-3">
              Core Technologies & Skills
            </h4>
            <div className="flex flex-wrap gap-2">
              {job.skills && job.skills.length > 0 ? (
                job.skills.map((s: any, idx: number) => (
                  <span
                    key={idx}
                    className="px-3 py-1 rounded-lg text-xs font-semibold bg-brand-softBg text-brand-deepNavy border border-brand-border"
                  >
                    {s.skill_name}
                  </span>
                ))
              ) : (
                <span className="text-xs text-brand-textSecondary">Standard domain skills</span>
              )}
            </div>
          </div>

          {/* Hiring Company Details */}
          <div className="bg-white p-6 rounded-2xl border border-brand-border shadow-xs space-y-4">
            <h4 className="text-xs font-bold uppercase tracking-wider text-brand-deepNavy">
              About the Organization
            </h4>
            <div>
              <h5 className="font-bold text-sm text-brand-deepNavy">
                {job.company?.name || "VELVORAX Software Solutions"}
              </h5>
              <p className="text-xs text-brand-textSecondary mt-1 leading-relaxed">
                {job.company?.description ||
                  "AI-powered automation and CRM enterprise technology solutions."}
              </p>
            </div>
            {job.company?.website && (
              <a
                href={job.company.website}
                target="_blank"
                rel="noreferrer"
                className="inline-block text-xs font-bold text-brand-corpBlue hover:underline"
              >
                Visit Company Website →
              </a>
            )}
          </div>
        </div>
      </div>

      {/* APPLICATION MODAL WORKFLOW */}
      {applyModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-xs">
          <div className="bg-white rounded-3xl max-w-lg w-full p-6 sm:p-8 shadow-2xl border border-brand-border">
            <div className="flex items-center justify-between pb-4 border-b border-brand-border">
              <div>
                <h3 className="text-lg font-bold text-brand-deepNavy">
                  Apply for {job.title}
                </h3>
                <span className="text-xs text-brand-textSecondary">
                  {job.company?.name} • {job.city || job.country}
                </span>
              </div>
              <button
                onClick={() => setApplyModalOpen(false)}
                className="text-slate-400 hover:text-brand-deepNavy text-xl"
              >
                ✕
              </button>
            </div>

            {appliedSuccess ? (
              <div className="py-8 text-center space-y-3">
                <CheckCircle2 className="w-14 h-14 text-brand-success mx-auto" />
                <h4 className="text-lg font-bold text-brand-deepNavy">Application Submitted!</h4>
                <p className="text-xs text-brand-textSecondary max-w-xs mx-auto">
                  Your profile and resume were saved in the PostgreSQL database. The hiring team has been notified.
                </p>
                <div className="pt-4 flex gap-3 justify-center">
                  <Link
                    href="/candidate/dashboard"
                    className="px-5 py-2.5 bg-brand-deepNavy text-white font-bold text-xs rounded-xl"
                  >
                    View My Applications
                  </Link>
                  <button
                    onClick={() => {
                      setApplyModalOpen(false);
                      setAppliedSuccess(false);
                    }}
                    className="px-4 py-2.5 border border-brand-border text-brand-deepNavy font-semibold text-xs rounded-xl"
                  >
                    Close
                  </button>
                </div>
              </div>
            ) : (
              <form onSubmit={handleApplySubmit} className="mt-5 space-y-4 text-xs">
                {applyError && (
                  <div className="p-3 bg-red-50 text-brand-error rounded-xl font-medium">
                    {applyError}
                  </div>
                )}

                {/* Resume Selection */}
                <div>
                  <label className="block font-bold text-brand-deepNavy mb-2">
                    Select Resume from Vault
                  </label>
                  {resumes.length > 0 ? (
                    <div className="space-y-2">
                      {resumes.map((r) => (
                        <label
                          key={r.id}
                          className={`flex items-center justify-between p-3 rounded-xl border cursor-pointer transition-all ${
                            selectedResumeId === r.id
                              ? "bg-brand-yellow/15 border-brand-yellow font-bold text-brand-deepNavy"
                              : "border-brand-border hover:bg-brand-softBg"
                          }`}
                        >
                          <div className="flex items-center gap-2">
                            <input
                              type="radio"
                              name="selectedResume"
                              checked={selectedResumeId === r.id}
                              onChange={() => setSelectedResumeId(r.id)}
                              className="accent-brand-yellow"
                            />
                            <FileText className="w-4 h-4 text-brand-corpBlue" />
                            <span>{r.original_filename}</span>
                          </div>
                          <span className="text-[11px] text-brand-textSecondary">
                            {(r.file_size_bytes / 1024).toFixed(1)} KB
                          </span>
                        </label>
                      ))}
                    </div>
                  ) : (
                    <div className="p-4 bg-brand-softBg rounded-xl border border-brand-border text-center">
                      <p className="text-brand-textSecondary mb-2">
                        No resumes found in your vault.
                      </p>
                      <Link
                        href="/candidate/dashboard"
                        className="text-brand-corpBlue font-bold underline"
                      >
                        Upload a Resume in Candidate Dashboard
                      </Link>
                    </div>
                  )}
                </div>

                {/* Cover letter */}
                <div>
                  <label className="block font-bold text-brand-deepNavy mb-1">
                    Cover Letter or Note to Recruiter (Optional)
                  </label>
                  <textarea
                    rows={4}
                    value={coverLetter}
                    onChange={(e) => setCoverLetter(e.target.value)}
                    placeholder="Highlight your relevant experience, project links, or availability..."
                    className="w-full p-3 rounded-xl border border-brand-border focus:outline-brand-yellow"
                  />
                </div>

                <div className="pt-2">
                  <button
                    type="submit"
                    disabled={submitting}
                    className="w-full py-3 bg-brand-yellow hover:bg-brand-yellowHover text-brand-deepNavy font-bold rounded-xl shadow-xs transition-all text-sm"
                  >
                    {submitting ? "Transmitting Application..." : "Confirm & Submit Application"}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
