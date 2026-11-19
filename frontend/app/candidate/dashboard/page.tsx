"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  User,
  FileText,
  Briefcase,
  Bookmark,
  Bell,
  UploadCloud,
  Trash2,
  CheckCircle2,
  Clock,
  Calendar,
  AlertCircle,
  ExternalLink,
  ChevronRight,
  ShieldCheck,
  Building
} from "lucide-react";
import { API_BASE_URL, formatISTDate, getAuthToken, getAuthUser, clearAuth } from "@/lib/api";

export default function CandidateDashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [profile, setProfile] = useState<any>(null);
  const [applications, setApplications] = useState<any[]>([]);
  const [savedJobs, setSavedJobs] = useState<any[]>([]);
  const [resumes, setResumes] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<"overview" | "profile" | "resumes" | "applications" | "saved">("overview");

  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);

  // Profile Edit State
  const [headline, setHeadline] = useState("");
  const [summary, setSummary] = useState("");
  const [expectedSalary, setExpectedSalary] = useState<number | "">("");
  const [noticePeriod, setNoticePeriod] = useState<number | "">("");
  const [linkedinUrl, setLinkedinUrl] = useState("");
  const [githubUrl, setGithubUrl] = useState("");
  const [savingProfile, setSavingProfile] = useState(false);
  const [profileSavedMsg, setProfileSavedMsg] = useState(false);
  const [certifications, setCertifications] = useState<any[]>([]);
  const [certificationName, setCertificationName] = useState("");
  const [certificationIssuer, setCertificationIssuer] = useState("");
  const [certificationId, setCertificationId] = useState("");
  const [certificationMessage, setCertificationMessage] = useState<string | null>(null);

  useEffect(() => {
    const token = getAuthToken();
    const authUser = getAuthUser();

    if (!token || !authUser) {
      router.push("/login?redirect=/candidate/dashboard");
      return;
    }

    if (authUser.role !== "CANDIDATE") {
      if (authUser.role === "RECRUITER") router.push("/recruiter/dashboard");
      else router.push("/admin/dashboard");
      return;
    }

    setUser(authUser);
    loadAllData(token);
  }, []);

  const loadAllData = async (token: string) => {
    setLoading(true);
    try {
      const [profRes, appsRes, savedRes, resumesRes] = await Promise.all([
        fetch(`${API_BASE_URL}/candidates/me`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API_BASE_URL}/applications/my`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API_BASE_URL}/candidates/me/saved-jobs`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API_BASE_URL}/candidates/me/resumes`, { headers: { Authorization: `Bearer ${token}` } }),
      ]);

      if (profRes.ok) {
        const p = await profRes.json();
        setProfile(p);
        setCertifications(p.certifications || []);
        setHeadline(p.headline || "");
        setSummary(p.summary || "");
        setExpectedSalary(p.expected_salary || "");
        setNoticePeriod(p.notice_period_days || 30);
        setLinkedinUrl(p.linkedin_url || "");
        setGithubUrl(p.github_url || "");
      }

      if (appsRes.ok) setApplications(await appsRes.json());
      if (savedRes.ok) setSavedJobs(await savedRes.json());
      if (resumesRes.ok) setResumes(await resumesRes.json());
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadError(null);
    setUploadSuccess(null);

    // Frontend pre-check: 2MB limit (Section 21)
    if (file.size > 2 * 1024 * 1024) {
      setUploadError("File exceeds 2 MB limit. Please upload a smaller file.");
      setUploading(false);
      return;
    }

    const token = getAuthToken();
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_BASE_URL}/candidates/me/resumes`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Failed to upload resume.");
      }

      setUploadSuccess(`Uploaded ${file.name} successfully to private storage.`);
      // Reload resumes
      const rRes = await fetch(`${API_BASE_URL}/candidates/me/resumes`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (rRes.ok) setResumes(await rRes.json());
    } catch (err: any) {
      setUploadError(err.message);
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const handleDeleteResume = async (resumeId: number) => {
    if (!confirm("Are you sure you want to delete this resume?")) return;
    const token = getAuthToken();
    try {
      const res = await fetch(`${API_BASE_URL}/candidates/me/resumes/${resumeId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        setResumes(resumes.filter((r) => r.id !== resumeId));
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingProfile(true);
    setProfileSavedMsg(false);
    const token = getAuthToken();

    try {
      const res = await fetch(`${API_BASE_URL}/candidates/me`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          headline,
          summary,
          expected_salary: expectedSalary === "" ? null : Number(expectedSalary),
          notice_period_days: noticePeriod === "" ? 30 : Number(noticePeriod),
          linkedin_url: linkedinUrl,
          github_url: githubUrl,
        }),
      });

      if (res.ok) {
        const updated = await res.json();
        setProfile(updated);
        setProfileSavedMsg(true);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setSavingProfile(false);
    }
  };

  const handleAddCertification = async (event: React.FormEvent) => {
    event.preventDefault();
    setCertificationMessage(null);
    try {
      const res = await fetch(`${API_BASE_URL}/candidates/me/certifications`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${getAuthToken()}`,
        },
        body: JSON.stringify({
          name: certificationName.trim(),
          issuing_organization: certificationIssuer.trim(),
          credential_id: certificationId.trim() || undefined,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Unable to save certification.");
      setCertifications((current) => [...current, data]);
      setCertificationName("");
      setCertificationIssuer("");
      setCertificationId("");
      setCertificationMessage("Certification saved.");
    } catch (error) {
      setCertificationMessage(error instanceof Error ? error.message : "Unable to save certification.");
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 text-center">
        <p className="text-sm font-semibold text-brand-textSecondary">
          Loading Candidate Dashboard...
        </p>
      </div>
    );
  }

  // Real Database Metrics
  const totalApps = applications.length;
  const underReview = applications.filter((a) => a.status === "UNDER_REVIEW").length;
  const shortlisted = applications.filter((a) => a.status === "SHORTLISTED").length;
  const interviewsScheduled = applications.filter((a) => a.status === "INTERVIEW_SCHEDULED").length;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Top Banner */}
      <div className="bg-white rounded-3xl border border-brand-border p-6 sm:p-8 shadow-xs mb-8 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-brand-deepNavy text-brand-yellow font-extrabold text-2xl flex items-center justify-center">
            {user?.full_name?.charAt(0) || "C"}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-black text-brand-deepNavy">
                {user?.full_name}
              </h1>
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-brand-yellow text-brand-deepNavy">
                Candidate
              </span>
            </div>
            <p className="text-xs text-brand-textSecondary mt-1">
              {headline || "Complete your profile headline to stand out to verified recruiters."}
            </p>
          </div>
        </div>

        <Link
          href="/jobs"
          className="px-6 py-3 bg-brand-yellow hover:bg-brand-yellowHover text-brand-deepNavy font-extrabold text-xs rounded-xl shadow-xs transition-all text-center"
        >
          Explore New Opportunities
        </Link>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 pb-4 mb-6 border-b border-brand-border overflow-x-auto text-xs font-bold">
        {[
          { key: "overview", label: "Dashboard Overview" },
          { key: "applications", label: `My Applications (${totalApps})` },
          { key: "resumes", label: `Resume Vault (${resumes.length})` },
          { key: "profile", label: "Profile & Preferences" },
          { key: "saved", label: `Saved Jobs (${savedJobs.length})` },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            className={`px-4 py-2.5 rounded-xl transition-all whitespace-nowrap ${
              activeTab === tab.key
                ? "bg-brand-deepNavy text-brand-yellow shadow-xs"
                : "text-brand-textSecondary hover:text-brand-deepNavy hover:bg-brand-softBg"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* OVERVIEW TAB */}
      {activeTab === "overview" && (
        <div className="space-y-8">
          {/* Stat Cards (Real DB counts) */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white p-5 rounded-2xl border border-brand-border shadow-xs">
              <span className="text-xs text-brand-textSecondary font-semibold">Total Applications</span>
              <span className="text-3xl font-black text-brand-deepNavy block mt-1">{totalApps}</span>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-brand-border shadow-xs">
              <span className="text-xs text-brand-textSecondary font-semibold">Under Review</span>
              <span className="text-3xl font-black text-brand-corpBlue block mt-1">{underReview}</span>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-brand-border shadow-xs">
              <span className="text-xs text-brand-textSecondary font-semibold">Shortlisted</span>
              <span className="text-3xl font-black text-brand-warning block mt-1">{shortlisted}</span>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-brand-border shadow-xs">
              <span className="text-xs text-brand-textSecondary font-semibold">Interviews Invited</span>
              <span className="text-3xl font-black text-brand-success block mt-1">{interviewsScheduled}</span>
            </div>
          </div>

          {/* Recent Applications Feed */}
          <div className="bg-white rounded-3xl border border-brand-border p-6 shadow-xs">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-brand-border">
              <h3 className="font-bold text-sm text-brand-deepNavy">Recent Application Status</h3>
              <button
                onClick={() => setActiveTab("applications")}
                className="text-xs font-bold text-brand-corpBlue hover:underline"
              >
                View All
              </button>
            </div>

            {applications.length > 0 ? (
              <div className="divide-y divide-brand-border">
                {applications.slice(0, 5).map((app) => (
                  <div key={app.id} className="py-3.5 flex items-center justify-between">
                    <div>
                      <h4 className="font-bold text-xs text-brand-deepNavy">{app.job?.title}</h4>
                      <span className="text-[11px] text-brand-textSecondary">
                        {app.job?.company?.name} • Applied on{" "}
                        {formatISTDate(app.applied_at)}
                      </span>
                    </div>
                    <span className="px-3 py-1 rounded-full text-[10px] font-extrabold uppercase bg-brand-softBg text-brand-deepNavy border border-brand-border">
                      {app.status}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-brand-textSecondary py-4">
                You haven&apos;t applied to any positions yet.
              </p>
            )}
          </div>
        </div>
      )}

      {/* APPLICATIONS TAB */}
      {activeTab === "applications" && (
        <div className="bg-white rounded-3xl border border-brand-border p-6 shadow-xs">
          <h3 className="font-bold text-base text-brand-deepNavy mb-4">
            Tracked Applications Pipeline
          </h3>

          {applications.length > 0 ? (
            <div className="space-y-4">
              {applications.map((app) => (
                <div
                  key={app.id}
                  className="p-5 rounded-2xl border border-brand-border bg-brand-softBg flex flex-col md:flex-row md:items-center justify-between gap-4"
                >
                  <div>
                    <span className="text-[10px] font-bold text-brand-corpBlue uppercase tracking-wider">
                      Application #{app.id}
                    </span>
                    <h4 className="font-bold text-sm text-brand-deepNavy mt-0.5">
                      {app.job?.title}
                    </h4>
                    <p className="text-xs text-brand-textSecondary mt-0.5">
                      {app.job?.company?.name} • {app.job?.city || app.job?.country}
                    </p>

                    {/* Interview Notification Banner if scheduled */}
                    {app.interviews && app.interviews.length > 0 && (
                      <div className="mt-3 p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-800 flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                        <span>
                          Interview scheduled:{" "}
                          <strong>
                            {formatISTDate(app.interviews[0].scheduled_time, true)}
                          </strong>{" "}
                          ({app.interviews[0].interview_type})
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center gap-4 flex-shrink-0">
                    <span
                      className={`px-3 py-1.5 rounded-full text-xs font-bold ${
                        app.status === "INTERVIEW_SCHEDULED"
                          ? "bg-emerald-100 text-emerald-800"
                          : app.status === "SHORTLISTED"
                          ? "bg-amber-100 text-amber-800"
                          : "bg-slate-200 text-slate-800"
                      }`}
                    >
                      {app.status}
                    </span>
                    <Link
                      href={`/jobs/${app.job?.slug}`}
                      className="text-xs font-bold text-brand-corpBlue hover:underline"
                    >
                      Job Details →
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-brand-textSecondary py-8 text-center">
              No applications submitted yet.
            </p>
          )}
        </div>
      )}

      {/* RESUME VAULT TAB */}
      {activeTab === "resumes" && (
        <div className="bg-white rounded-3xl border border-brand-border p-6 sm:p-8 shadow-xs space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-brand-border">
            <div>
              <h3 className="font-bold text-base text-brand-deepNavy flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-brand-success" />
                <span>Private Resume Vault</span>
              </h3>
              <p className="text-xs text-brand-textSecondary mt-0.5">
                Strict 2 MB ceiling, verified magic-byte headers, encrypted object storage.
              </p>
            </div>

            {/* Upload Button */}
            <label className="cursor-pointer px-5 py-2.5 bg-brand-yellow hover:bg-brand-yellowHover text-brand-deepNavy font-bold text-xs rounded-xl shadow-xs transition-all flex items-center gap-2">
              <UploadCloud className="w-4 h-4" />
              <span>{uploading ? "Inspecting File..." : "Upload New Resume"}</span>
              <input
                type="file"
                accept=".pdf,.docx"
                onChange={handleFileUpload}
                disabled={uploading}
                className="hidden"
              />
            </label>
          </div>

          {uploadError && (
            <div className="p-3.5 bg-red-50 border border-red-200 text-brand-error rounded-xl text-xs font-medium">
              {uploadError}
            </div>
          )}

          {uploadSuccess && (
            <div className="p-3.5 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-xs font-medium">
              {uploadSuccess}
            </div>
          )}

          {resumes.length > 0 ? (
            <div className="space-y-3">
              {resumes.map((r) => (
                <div
                  key={r.id}
                  className="p-4 rounded-2xl border border-brand-border bg-brand-softBg flex items-center justify-between gap-4"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-white border border-brand-border flex items-center justify-center text-brand-corpBlue">
                      <FileText className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="font-bold text-xs text-brand-deepNavy">
                        {r.original_filename}
                      </h4>
                      <span className="text-[11px] text-brand-textSecondary">
                        {(r.file_size_bytes / 1024).toFixed(1)} KB • Uploaded{" "}
                        {formatISTDate(r.created_at)}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    {r.is_default && (
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-brand-yellow text-brand-deepNavy">
                        Default
                      </span>
                    )}
                    <button
                      onClick={() => handleDeleteResume(r.id)}
                      className="p-2 text-slate-400 hover:text-brand-error transition-colors"
                      title="Delete Resume"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-12 text-center text-xs text-brand-textSecondary">
              <UploadCloud className="w-10 h-10 text-slate-300 mx-auto mb-2" />
              <p>No resumes uploaded yet. Upload a PDF or DOCX file (up to 2MB).</p>
            </div>
          )}
        </div>
      )}

      {/* PROFILE TAB */}
      {activeTab === "profile" && (
        <div className="bg-white rounded-3xl border border-brand-border p-6 sm:p-8 shadow-xs max-w-2xl">
          <h3 className="font-bold text-base text-brand-deepNavy mb-4">
            Candidate Professional Profile
          </h3>

          {profileSavedMsg && (
            <div className="mb-4 p-3 bg-emerald-50 text-emerald-800 rounded-xl text-xs font-semibold">
              Profile updated successfully in PostgreSQL database!
            </div>
          )}

          <form onSubmit={handleSaveProfile} className="space-y-4 text-xs">
            <div>
              <label className="block font-bold text-brand-deepNavy mb-1">Professional Headline</label>
              <input
                type="text"
                value={headline}
                onChange={(e) => setHeadline(e.target.value)}
                placeholder="e.g. Senior Full-Stack Engineer | Python, React, Next.js"
                className="w-full px-3.5 py-2.5 rounded-xl border border-brand-border focus:outline-brand-yellow text-xs font-medium"
              />
            </div>

            <div>
              <label className="block font-bold text-brand-deepNavy mb-1">Career Summary</label>
              <textarea
                rows={4}
                value={summary}
                onChange={(e) => setSummary(e.target.value)}
                placeholder="Brief summary of your technical background, career goals, and key achievements..."
                className="w-full p-3 rounded-xl border border-brand-border focus:outline-brand-yellow"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block font-bold text-brand-deepNavy mb-1">Expected Annual Salary (INR)</label>
                <input
                  type="number"
                  value={expectedSalary}
                  onChange={(e) => setExpectedSalary(e.target.value === "" ? "" : Number(e.target.value))}
                  placeholder="e.g. 1800000"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-brand-border"
                />
              </div>

              <div>
                <label className="block font-bold text-brand-deepNavy mb-1">Notice Period (Days)</label>
                <input
                  type="number"
                  value={noticePeriod}
                  onChange={(e) => setNoticePeriod(e.target.value === "" ? "" : Number(e.target.value))}
                  placeholder="e.g. 30"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-brand-border"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block font-bold text-brand-deepNavy mb-1">LinkedIn Profile</label>
                <input
                  type="url"
                  value={linkedinUrl}
                  onChange={(e) => setLinkedinUrl(e.target.value)}
                  placeholder="https://linkedin.com/in/..."
                  className="w-full px-3.5 py-2.5 rounded-xl border border-brand-border"
                />
              </div>

              <div>
                <label className="block font-bold text-brand-deepNavy mb-1">GitHub / Portfolio</label>
                <input
                  type="url"
                  value={githubUrl}
                  onChange={(e) => setGithubUrl(e.target.value)}
                  placeholder="https://github.com/..."
                  className="w-full px-3.5 py-2.5 rounded-xl border border-brand-border"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={savingProfile}
              className="px-6 py-2.5 bg-brand-yellow hover:bg-brand-yellowHover text-brand-deepNavy font-bold rounded-xl text-xs shadow-xs"
            >
              {savingProfile ? "Saving Profile..." : "Save Profile Details"}
            </button>
          </form>

          <div className="mt-8 border-t border-brand-border pt-6">
            <h4 className="font-bold text-sm text-brand-deepNavy">Certifications</h4>
            <ul className="my-3 space-y-2 text-xs">
              {certifications.map((cert) => (
                <li key={cert.id} className="rounded-xl bg-brand-softBg p-3">
                  <strong>{cert.name}</strong> — {cert.issuing_organization}
                </li>
              ))}
            </ul>
            <form onSubmit={handleAddCertification} className="grid gap-3 sm:grid-cols-2">
              <input
                required
                value={certificationName}
                onChange={(event) => setCertificationName(event.target.value)}
                placeholder="Certification name"
                className="rounded-xl border border-brand-border px-3 py-2.5"
              />
              <input
                required
                value={certificationIssuer}
                onChange={(event) => setCertificationIssuer(event.target.value)}
                placeholder="Issuing organization"
                className="rounded-xl border border-brand-border px-3 py-2.5"
              />
              <input
                value={certificationId}
                onChange={(event) => setCertificationId(event.target.value)}
                placeholder="Credential ID (optional)"
                className="rounded-xl border border-brand-border px-3 py-2.5"
              />
              <button className="rounded-xl bg-brand-deepNavy px-4 py-2.5 text-xs font-bold text-white">
                Add certification
              </button>
            </form>
            {certificationMessage && (
              <p className="mt-2 text-xs text-brand-corpBlue" role="status">{certificationMessage}</p>
            )}
          </div>
        </div>
      )}

      {/* SAVED JOBS TAB */}
      {activeTab === "saved" && (
        <div className="bg-white rounded-3xl border border-brand-border p-6 shadow-xs">
          <h3 className="font-bold text-base text-brand-deepNavy mb-4">
            Saved Opportunities ({savedJobs.length})
          </h3>

          {savedJobs.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {savedJobs.map((job) => (
                <div key={job.id} className="p-4 rounded-2xl border border-brand-border bg-brand-softBg">
                  <h4 className="font-bold text-sm text-brand-deepNavy">{job.title}</h4>
                  <span className="text-xs text-brand-textSecondary block mt-0.5">
                    {job.company?.name} • {job.city || job.country}
                  </span>
                  <div className="mt-3 flex items-center justify-between">
                    <Link
                      href={`/jobs/${job.slug}`}
                      className="text-xs font-bold text-brand-corpBlue hover:underline"
                    >
                      View & Apply →
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-brand-textSecondary py-8 text-center">
              No saved jobs yet.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
