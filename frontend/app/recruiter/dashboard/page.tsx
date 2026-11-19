"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Briefcase,
  Users,
  Building2,
  Calendar,
  PlusCircle,
  Clock,
  CheckCircle2,
  XCircle,
  FileText,
  Video,
  Send,
  Eye,
  Settings,
  AlertCircle
} from "lucide-react";
import { API_BASE_URL, formatISTDate, getAuthToken, getAuthUser } from "@/lib/api";

export default function RecruiterDashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);
  const [company, setCompany] = useState<any>(null);
  const [jobs, setJobs] = useState<any[]>([]);
  const [applications, setApplications] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);

  const [activeTab, setActiveTab] = useState<"overview" | "jobs" | "applicants" | "post-job" | "company">("overview");
  const [loading, setLoading] = useState(true);

  // New Job Form State
  const [jobTitle, setJobTitle] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [jobType, setJobType] = useState("IT");
  const [employmentType, setEmploymentType] = useState("Full-time");
  const [workArrangement, setWorkArrangement] = useState("Hybrid");
  const [experienceLevel, setExperienceLevel] = useState("Mid-level");
  const [experienceMinYears, setExperienceMinYears] = useState(3.0);
  const [salaryMin, setSalaryMin] = useState(1200000);
  const [salaryMax, setSalaryMax] = useState(2000000);
  const [salaryCurrency, setSalaryCurrency] = useState("INR");
  const [country, setCountry] = useState("India");
  const [state, setState] = useState("Telangana");
  const [city, setCity] = useState("Hyderabad");
  const [jobDesc, setJobDesc] = useState("");
  const [skillsStr, setSkillsStr] = useState("Python, React, TypeScript, SQL");
  const [creatingJob, setCreatingJob] = useState(false);
  const [jobCreatedMsg, setJobCreatedMsg] = useState(false);
  const [companyUpdateMessage, setCompanyUpdateMessage] = useState<string | null>(null);

  // Interview Schedule Modal State
  const [interviewModalOpen, setInterviewModalOpen] = useState(false);
  const [targetAppId, setTargetAppId] = useState<number | null>(null);
  const [interviewType, setInterviewType] = useState("Technical");
  const [scheduledTime, setScheduledTime] = useState("");
  const [meetingLink, setMeetingLink] = useState("");
  const [scheduling, setScheduling] = useState(false);

  useEffect(() => {
    const token = getAuthToken();
    const authUser = getAuthUser();

    if (!token || !authUser) {
      router.push("/login?redirect=/recruiter/dashboard");
      return;
    }

    if (authUser.role !== "RECRUITER" && authUser.role !== "ADMIN" && authUser.role !== "SUPER_ADMIN") {
      router.push("/candidate/dashboard");
      return;
    }

    setUser(authUser);
    loadRecruiterData(token);
  }, []);

  const loadRecruiterData = async (token: string) => {
    setLoading(true);
    try {
      const [statsRes, compRes, jobsRes, appsRes, catsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/recruiters/dashboard`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API_BASE_URL}/recruiters/company`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API_BASE_URL}/recruiters/jobs`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API_BASE_URL}/recruiter/applications`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API_BASE_URL}/categories`),
      ]);

      if (statsRes.ok) setStats(await statsRes.json());
      if (compRes.ok) setCompany(await compRes.json());
      if (jobsRes.ok) setJobs(await jobsRes.json());
      if (appsRes.ok) setApplications(await appsRes.json());
      if (catsRes.ok) {
        const c = await catsRes.json();
        setCategories(c);
        if (c.length > 0) setCategoryId(c[0].id.toString());
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateJob = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreatingJob(true);
    setJobCreatedMsg(false);
    const token = getAuthToken();

    try {
      const skillsArr = skillsStr.split(",").map((s) => s.trim()).filter(Boolean);
      const res = await fetch(`${API_BASE_URL}/jobs`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          title: jobTitle,
          category_id: parseInt(categoryId),
          job_type: jobType,
          employment_type: employmentType,
          work_arrangement: workArrangement,
          experience_level: experienceLevel,
          experience_min_years: experienceMinYears,
          salary_min: salaryMin,
          salary_max: salaryMax,
          salary_currency: salaryCurrency,
          country,
          state,
          city,
          description: jobDesc,
          skills: skillsArr,
        }),
      });

      if (res.ok) {
        setJobCreatedMsg(true);
        // Reset form
        setJobTitle("");
        setJobDesc("");
        // Reload jobs
        const jRes = await fetch(`${API_BASE_URL}/recruiters/jobs`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (jRes.ok) setJobs(await jRes.json());
      }
    } catch (err) {
      console.error(err);
    } finally {
      setCreatingJob(false);
    }
  };

  const handleUpdateCompanyRegistration = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const token = getAuthToken();
    setCompanyUpdateMessage(null);

    try {
      const res = await fetch(`${API_BASE_URL}/recruiters/company`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          gstin: String(formData.get("gstin") || "").trim() || null,
          cin: String(formData.get("cin") || "").trim() || null,
          registration_number: String(formData.get("registration_number") || "").trim() || null,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Unable to update company registration details.");
      setCompany(data);
      setCompanyUpdateMessage(
        "Registration details saved. An administrator must review changes before job posting is enabled."
      );
    } catch (error) {
      setCompanyUpdateMessage(error instanceof Error ? error.message : "Unable to update company details.");
    }
  };

  const handleUpdateStatus = async (appId: number, newStatus: string) => {
    const token = getAuthToken();
    try {
      const res = await fetch(`${API_BASE_URL}/applications/${appId}/status`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ status: newStatus }),
      });
      if (res.ok) {
        // Update local state
        setApplications(
          applications.map((a) => (a.id === appId ? { ...a, status: newStatus } : a))
        );
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleScheduleInterview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetAppId) return;
    setScheduling(true);
    const token = getAuthToken();

    try {
      const res = await fetch(`${API_BASE_URL}/interviews`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          application_id: targetAppId,
          interview_type: interviewType,
          scheduled_time: new Date(`${scheduledTime}:00+05:30`).toISOString(),
          timezone_str: "Asia/Kolkata",
          meeting_link: meetingLink,
        }),
      });

      if (res.ok) {
        setInterviewModalOpen(false);
        // Refresh apps
        const aRes = await fetch(`${API_BASE_URL}/recruiter/applications`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (aRes.ok) setApplications(await aRes.json());
      }
    } catch (err) {
      console.error(err);
    } finally {
      setScheduling(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 text-center">
        <p className="text-sm font-semibold text-brand-textSecondary">
          Loading Recruiter ATS Workspace...
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Top Banner */}
      <div className="bg-white rounded-3xl border border-brand-border p-6 sm:p-8 shadow-xs mb-8 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-brand-deepNavy text-brand-yellow font-extrabold text-2xl flex items-center justify-center">
            <Building2 className="w-8 h-8 text-brand-yellow" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-black text-brand-deepNavy">
                {company?.name || "Corporate Recruiter Portal"}
              </h1>
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-brand-yellow text-brand-deepNavy">
                Recruiter ATS
              </span>
            </div>
            <p className="text-xs text-brand-textSecondary mt-1">
              Logged in as <strong>{user?.full_name}</strong> • Authorized Hiring Partner
            </p>
          </div>
        </div>

        <button
          onClick={() => setActiveTab("post-job")}
          className="px-6 py-3 bg-brand-yellow hover:bg-brand-yellowHover text-brand-deepNavy font-extrabold text-xs rounded-xl shadow-xs transition-all flex items-center justify-center gap-2"
        >
          <PlusCircle className="w-4 h-4" />
          <span>Post New Vacancy</span>
        </button>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 pb-4 mb-6 border-b border-brand-border overflow-x-auto text-xs font-bold">
        {[
          { key: "overview", label: "Dashboard Metrics" },
          { key: "applicants", label: `Applicants (${applications.length})` },
          { key: "jobs", label: `Active Jobs (${jobs.length})` },
          { key: "post-job", label: "Post a Job" },
          { key: "company", label: "Company Profile" },
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
          {/* Stat Cards (Real Database statistics per Section 8) */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white p-5 rounded-2xl border border-brand-border shadow-xs">
              <span className="text-xs text-brand-textSecondary font-semibold">Published Positions</span>
              <span className="text-3xl font-black text-brand-deepNavy block mt-1">
                {stats?.published_jobs ?? 0}
              </span>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-brand-border shadow-xs">
              <span className="text-xs text-brand-textSecondary font-semibold">Total Applicants</span>
              <span className="text-3xl font-black text-brand-corpBlue block mt-1">
                {stats?.total_applicants ?? 0}
              </span>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-brand-border shadow-xs">
              <span className="text-xs text-brand-textSecondary font-semibold">Shortlisted Candidates</span>
              <span className="text-3xl font-black text-brand-warning block mt-1">
                {stats?.shortlisted_candidates ?? 0}
              </span>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-brand-border shadow-xs">
              <span className="text-xs text-brand-textSecondary font-semibold">Interviews Scheduled</span>
              <span className="text-3xl font-black text-brand-success block mt-1">
                {stats?.interviews_scheduled ?? 0}
              </span>
            </div>
          </div>

          {/* Quick Applicant Review Feed */}
          <div className="bg-white rounded-3xl border border-brand-border p-6 shadow-xs">
            <h3 className="font-bold text-sm text-brand-deepNavy mb-4 pb-3 border-b border-brand-border">
              Candidate Applications Pipeline
            </h3>
            {applications.length > 0 ? (
              <div className="divide-y divide-brand-border">
                {applications.slice(0, 5).map((app) => (
                  <div key={app.id} className="py-3.5 flex items-center justify-between">
                    <div>
                      <h4 className="font-bold text-xs text-brand-deepNavy">
                        {app.candidate_summary?.full_name || "Applicant"}
                      </h4>
                      <span className="text-[11px] text-brand-textSecondary">
                        Applied for <strong>{app.job?.title}</strong> •{" "}
                        {formatISTDate(app.applied_at)}
                      </span>
                    </div>
                    <span className="px-3 py-1 rounded-full text-[10px] font-bold uppercase bg-brand-softBg text-brand-deepNavy">
                      {app.status}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-brand-textSecondary py-4">No candidates applied yet.</p>
            )}
          </div>
        </div>
      )}

      {/* APPLICANTS TAB */}
      {activeTab === "applicants" && (
        <div className="bg-white rounded-3xl border border-brand-border p-6 shadow-xs">
          <h3 className="font-bold text-base text-brand-deepNavy mb-4">
            Candidate Pipeline & Evaluation ATS
          </h3>

          {applications.length > 0 ? (
            <div className="space-y-4">
              {applications.map((app) => (
                <div
                  key={app.id}
                  className="p-5 rounded-2xl border border-brand-border bg-brand-softBg flex flex-col md:flex-row md:items-center justify-between gap-4"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <h4 className="font-bold text-sm text-brand-deepNavy">
                        {app.candidate_summary?.full_name || "Candidate"}
                      </h4>
                      <span className="text-xs text-slate-500">
                        ({app.candidate_summary?.email})
                      </span>
                    </div>
                    <p className="text-xs text-brand-textSecondary">
                      Applied for: <strong className="text-brand-deepNavy">{app.job?.title}</strong>
                    </p>
                    {app.resume && (
                      <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-brand-corpBlue">
                        <FileText className="w-3.5 h-3.5" />
                        Attached Resume: {app.resume.original_filename} ({(app.resume.file_size_bytes / 1024).toFixed(1)} KB)
                      </span>
                    )}
                  </div>

                  {/* Recruiter Action Controls */}
                  <div className="flex items-center gap-2 flex-wrap">
                    <select
                      value={app.status}
                      onChange={(e) => handleUpdateStatus(app.id, e.target.value)}
                      className="px-3 py-1.5 text-xs font-bold rounded-xl border border-brand-border bg-white text-brand-deepNavy"
                    >
                      <option value="APPLIED">APPLIED</option>
                      <option value="UNDER_REVIEW">UNDER_REVIEW</option>
                      <option value="SHORTLISTED">SHORTLISTED</option>
                      <option value="INTERVIEW_SCHEDULED">INTERVIEW_SCHEDULED</option>
                      <option value="SELECTED">SELECTED</option>
                      <option value="REJECTED">REJECTED</option>
                    </select>

                    <button
                      onClick={() => {
                        setTargetAppId(app.id);
                        setInterviewModalOpen(true);
                      }}
                      className="px-3.5 py-1.5 text-xs font-bold bg-brand-deepNavy text-brand-yellow rounded-xl shadow-xs flex items-center gap-1.5"
                    >
                      <Video className="w-3.5 h-3.5" />
                      <span>Schedule</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-brand-textSecondary py-8 text-center">
              No applications received for your company vacancies yet.
            </p>
          )}
        </div>
      )}

      {/* JOBS TAB */}
      {activeTab === "jobs" && (
        <div className="bg-white rounded-3xl border border-brand-border p-6 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-base text-brand-deepNavy">
              Published Company Vacancies
            </h3>
            <button
              onClick={() => setActiveTab("post-job")}
              className="text-xs font-bold text-brand-corpBlue hover:underline"
            >
              + Create New
            </button>
          </div>

          {jobs.length > 0 ? (
            <div className="divide-y divide-brand-border">
              {jobs.map((job) => (
                <div key={job.id} className="py-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-bold text-sm text-brand-deepNavy">{job.title}</h4>
                      <span className="text-xs text-brand-textSecondary">
                        {job.experience_level} • {job.employment_type} • {job.work_arrangement} •{" "}
                        {job.views_count} views • {job.applications_count} applicants
                      </span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span
                        className={`px-3 py-1 rounded-full text-[11px] font-bold ${
                          job.status === "PUBLISHED"
                            ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                            : job.status === "PENDING_APPROVAL"
                            ? "bg-amber-50 text-amber-800 border border-amber-200"
                            : job.status === "REJECTED"
                            ? "bg-rose-50 text-rose-700 border border-rose-200"
                            : "bg-brand-softBg text-brand-deepNavy"
                        }`}
                      >
                        {job.status === "PENDING_APPROVAL"
                          ? "⏳ Pending Admin Approval"
                          : job.status === "PUBLISHED"
                          ? "✓ Published / Live"
                          : job.status === "REJECTED"
                          ? "✕ Rejected by Admin"
                          : job.status}
                      </span>
                      {job.status === "PUBLISHED" && (
                        <Link
                          href={`/jobs/${job.slug}`}
                          className="text-xs font-bold text-brand-corpBlue hover:underline"
                        >
                          View Live →
                        </Link>
                      )}
                    </div>
                  </div>
                  {job.status === "REJECTED" && job.rejection_reason && (
                    <div className="mt-2.5 p-3 rounded-xl bg-rose-50/70 border border-rose-100 text-xs text-rose-800 flex items-start gap-2">
                      <AlertCircle className="w-4 h-4 text-rose-600 mt-0.5 shrink-0" />
                      <div>
                        <strong>Admin Rejection Feedback:</strong> {job.rejection_reason}
                        <div className="text-[11px] text-rose-600 mt-0.5">
                          Edit this vacancy to revise requirements and resubmit for Admin approval.
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-brand-textSecondary py-8 text-center">
              No jobs posted yet. Click &apos;Post a Job&apos; to create one.
            </p>
          )}
        </div>
      )}

      {/* POST A JOB TAB */}
      {activeTab === "post-job" && (
        <div className="bg-white rounded-3xl border border-brand-border p-6 sm:p-8 shadow-xs max-w-3xl">
          <h3 className="font-bold text-base text-brand-deepNavy mb-2">
            Submit Vacancy for Verification & Publishing
          </h3>
          <p className="text-xs text-brand-textSecondary mb-6">
            To ensure zero spam and authentic candidate discovery, submitted vacancies are placed into{" "}
            <strong>Pending Approval</strong> and promptly reviewed by VELVORAX platform administrators before going live.
          </p>

          {jobCreatedMsg && (
            <div className="mb-6 p-4 bg-amber-50 text-amber-900 border border-amber-200 rounded-2xl text-xs font-bold flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-amber-600 shrink-0" />
              <span>Vacancy submitted successfully! It is now pending Admin approval and will appear on public portals upon verification.</span>
            </div>
          )}

          <form onSubmit={handleCreateJob} className="space-y-4 text-xs">
            <div>
              <label className="block font-bold text-brand-deepNavy mb-1">Job Title</label>
              <input
                type="text"
                required
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                placeholder="e.g. Senior Frontend Engineer (React/Next.js)"
                className="w-full px-3.5 py-2.5 rounded-xl border border-brand-border focus:outline-brand-yellow font-medium"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block font-bold text-brand-deepNavy mb-1">Category</label>
                <select
                  value={categoryId}
                  onChange={(e) => setCategoryId(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-brand-border"
                >
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name} ({c.category_type})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-bold text-brand-deepNavy mb-1">Classification</label>
                <select
                  value={jobType}
                  onChange={(e) => setJobType(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-brand-border"
                >
                  <option value="IT">IT</option>
                  <option value="NON_IT">Non-IT</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="block font-bold text-brand-deepNavy mb-1">Employment Type</label>
                <select
                  value={employmentType}
                  onChange={(e) => setEmploymentType(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-brand-border"
                >
                  <option value="Full-time">Full-time</option>
                  <option value="Part-time">Part-time</option>
                  <option value="Contract">Contract</option>
                  <option value="Internship">Internship</option>
                </select>
              </div>

              <div>
                <label className="block font-bold text-brand-deepNavy mb-1">Work Arrangement</label>
                <select
                  value={workArrangement}
                  onChange={(e) => setWorkArrangement(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-brand-border"
                >
                  <option value="Remote">Remote</option>
                  <option value="Hybrid">Hybrid</option>
                  <option value="On-site">On-site</option>
                </select>
              </div>

              <div>
                <label className="block font-bold text-brand-deepNavy mb-1">Experience Level</label>
                <select
                  value={experienceLevel}
                  onChange={(e) => setExperienceLevel(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-brand-border"
                >
                  <option value="Fresher">Fresher</option>
                  <option value="Junior">Junior</option>
                  <option value="Mid-level">Mid-level</option>
                  <option value="Senior">Senior</option>
                  <option value="Lead">Lead</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block font-bold text-brand-deepNavy mb-1">Salary Min (INR)</label>
                <input
                  type="number"
                  value={salaryMin}
                  onChange={(e) => setSalaryMin(Number(e.target.value))}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-brand-border"
                />
              </div>

              <div>
                <label className="block font-bold text-brand-deepNavy mb-1">Salary Max (INR)</label>
                <input
                  type="number"
                  value={salaryMax}
                  onChange={(e) => setSalaryMax(Number(e.target.value))}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-brand-border"
                />
              </div>
            </div>

            <div>
              <label className="block font-bold text-brand-deepNavy mb-1">Required Skills (Comma separated)</label>
              <input
                type="text"
                value={skillsStr}
                onChange={(e) => setSkillsStr(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl border border-brand-border"
              />
            </div>

            <div>
              <label className="block font-bold text-brand-deepNavy mb-1">Job Description & Responsibilities</label>
              <textarea
                rows={5}
                required
                value={jobDesc}
                onChange={(e) => setJobDesc(e.target.value)}
                placeholder="Detail role objectives, expectations, and day-to-day responsibilities..."
                className="w-full p-3 rounded-xl border border-brand-border"
              />
            </div>

            <button
              type="submit"
              disabled={creatingJob}
              className="px-8 py-3 bg-brand-yellow hover:bg-brand-yellowHover text-brand-deepNavy font-extrabold text-xs rounded-xl shadow-xs"
            >
              {creatingJob ? "Publishing Position..." : "Publish Job Vacancy"}
            </button>
          </form>
        </div>
      )}

      {/* COMPANY PROFILE TAB */}
      {activeTab === "company" && (
        <div className="bg-white rounded-3xl border border-brand-border p-6 sm:p-8 shadow-xs max-w-2xl space-y-4">
          <h3 className="font-bold text-base text-brand-deepNavy">
            Company Record & Verification
          </h3>
          <div className="p-4 bg-brand-softBg rounded-2xl border border-brand-border space-y-2 text-xs">
            <div>
              <span className="text-brand-textSecondary block">Company Name</span>
              <strong className="text-brand-deepNavy text-sm">{company?.name}</strong>
            </div>
            <div>
              <span className="text-brand-textSecondary block">Industry</span>
              <span className="text-brand-deepNavy">{company?.industry || "Software & Technology"}</span>
            </div>
            <div>
              <span className="text-brand-textSecondary block">Headquarters</span>
              <span className="text-brand-deepNavy">{company?.headquarters || "Hyderabad, India"}</span>
            </div>
            <div>
              <span className="text-brand-textSecondary block">Verification Status</span>
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                {company?.is_verified ? "Verified Hiring Partner" : "Verification Pending"}
              </span>
            </div>
          </div>
          <form onSubmit={handleUpdateCompanyRegistration} className="space-y-3">
            <p className="text-xs text-brand-textSecondary">
              Provide company registration details for manual administrator review.
            </p>
            {(["gstin", "cin", "registration_number"] as const).map((field) => (
              <label key={field} className="block text-xs font-bold text-brand-deepNavy">
                {field === "gstin" ? "GSTIN" : field === "cin" ? "CIN" : "Other registration number"}
                <input
                  name={field}
                  maxLength={field === "gstin" ? 15 : field === "cin" ? 21 : 100}
                  defaultValue={company?.[field] || ""}
                  className="mt-1 w-full rounded-xl border border-brand-border px-3 py-2.5 font-medium"
                />
              </label>
            ))}
            {companyUpdateMessage && (
              <p className="text-xs text-brand-corpBlue" role="status">{companyUpdateMessage}</p>
            )}
            <button className="rounded-xl bg-brand-yellow px-4 py-2.5 text-xs font-extrabold text-brand-deepNavy">
              Save registration details
            </button>
          </form>
        </div>
      )}

      {/* INTERVIEW SCHEDULING MODAL */}
      {interviewModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-xs">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl border border-brand-border">
            <div className="flex items-center justify-between pb-3 border-b border-brand-border">
              <h3 className="font-bold text-sm text-brand-deepNavy">Schedule Candidate Interview</h3>
              <button onClick={() => setInterviewModalOpen(false)} className="text-slate-400">✕</button>
            </div>

            <form onSubmit={handleScheduleInterview} className="mt-4 space-y-3.5 text-xs">
              <div>
                <label className="block font-bold text-brand-deepNavy mb-1">Interview Round</label>
                <select
                  value={interviewType}
                  onChange={(e) => setInterviewType(e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-brand-border"
                >
                  <option value="Technical">Technical Round</option>
                  <option value="Screening">HR Screening</option>
                  <option value="Managerial">Managerial Round</option>
                  <option value="Executive">Executive Leadership</option>
                </select>
              </div>

              <div>
                <label className="block font-bold text-brand-deepNavy mb-1">Date & Time</label>
                <input
                  type="datetime-local"
                  required
                  value={scheduledTime}
                  onChange={(e) => setScheduledTime(e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-brand-border"
                />
              </div>

              <div>
                <label className="block font-bold text-brand-deepNavy mb-1">Meeting Link (Google Meet / Zoom)</label>
                <input
                  type="url"
                  placeholder="https://meet.google.com/..."
                  value={meetingLink}
                  onChange={(e) => setMeetingLink(e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-brand-border"
                />
              </div>

              <button
                type="submit"
                disabled={scheduling}
                className="w-full py-2.5 bg-brand-yellow hover:bg-brand-yellowHover text-brand-deepNavy font-bold rounded-xl text-xs shadow-xs"
              >
                {scheduling ? "Scheduling..." : "Confirm & Send Invitation"}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
