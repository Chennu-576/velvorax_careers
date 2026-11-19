"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ShieldAlert,
  Users,
  Building,
  Briefcase,
  FileCheck,
  DollarSign,
  TrendingUp,
  CheckCircle2,
  XCircle,
  Eye,
  Send,
  Layers,
  History,
  AlertTriangle
} from "lucide-react";
import { API_BASE_URL, formatISTDate, getAuthToken, getAuthUser } from "@/lib/api";

export default function AdminDashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);
  const [users, setUsers] = useState<any[]>([]);
  const [companies, setCompanies] = useState<any[]>([]);
  const [recruiters, setRecruiters] = useState<any[]>([]);
  const [employerRequests, setEmployerRequests] = useState<any[]>([]);
  const [invoices, setInvoices] = useState<any[]>([]);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [pendingJobs, setPendingJobs] = useState<any[]>([]);

  const [activeTab, setActiveTab] = useState<"overview" | "moderation" | "users" | "companies" | "requests" | "finance" | "audit">("overview");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getAuthToken();
    const authUser = getAuthUser();

    if (!token || !authUser) {
      router.push("/login?redirect=/admin/dashboard");
      return;
    }

    if (authUser.role !== "ADMIN" && authUser.role !== "SUPER_ADMIN") {
      router.push("/login");
      return;
    }

    setUser(authUser);
    loadAdminData(token);
  }, []);

  const loadAdminData = async (token: string) => {
    setLoading(true);
    try {
      const [sRes, uRes, cRes, recruiterRes, rRes, fRes, aRes, jRes] = await Promise.all([
        fetch(`${API_BASE_URL}/admin/dashboard/stats`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API_BASE_URL}/admin/users`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API_BASE_URL}/admin/companies`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API_BASE_URL}/admin/recruiters`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API_BASE_URL}/admin/employer-requests`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API_BASE_URL}/admin/finance/invoices`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API_BASE_URL}/admin/audit-logs`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API_BASE_URL}/admin/jobs/pending`, { headers: { Authorization: `Bearer ${token}` } }),
      ]);

      if (sRes.ok) setStats(await sRes.json());
      if (uRes.ok) setUsers(await uRes.json());
      if (cRes.ok) setCompanies(await cRes.json());
      if (recruiterRes.ok) setRecruiters(await recruiterRes.json());
      if (rRes.ok) setEmployerRequests(await rRes.json());
      if (fRes.ok) setInvoices(await fRes.json());
      if (aRes.ok) setAuditLogs(await aRes.json());
      if (jRes.ok) setPendingJobs(await jRes.json());
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleUserStatus = async (userId: number, currentActive: boolean) => {
    const token = getAuthToken();
    try {
      const res = await fetch(`${API_BASE_URL}/admin/users/${userId}/status?is_active=${!currentActive}`, {
        method: "PATCH",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        setUsers(users.map((u) => (u.id === userId ? { ...u, is_active: !currentActive } : u)));
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleVerifyCompany = async (companyId: number, currentVerified: boolean) => {
    const verificationNotes = window.prompt(
      currentVerified
        ? "Why are you revoking this company's verification?"
        : "Record the manual verification notes and documents checked:"
    );
    if (verificationNotes === null || !verificationNotes.trim()) return;

    const token = getAuthToken();
    try {
      const params = new URLSearchParams({
        is_verified: String(!currentVerified),
        is_hiring_partner: String(!currentVerified),
        verification_notes: verificationNotes.trim(),
      });
      const res = await fetch(`${API_BASE_URL}/admin/companies/${companyId}/verify?${params}`, {
        method: "PATCH",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        setCompanies(companies.map((c) => (c.id === companyId ? {
          ...c,
          is_verified: !currentVerified,
          is_hiring_partner: !currentVerified,
          verification_notes: verificationNotes.trim(),
        } : c)));
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleRecruiterApproval = async (
    recruiterProfileId: number,
    currentApproved: boolean
  ) => {
    const token = getAuthToken();
    try {
      const params = new URLSearchParams({
        is_approved: String(!currentApproved),
      });
      const response = await fetch(
        `${API_BASE_URL}/admin/recruiters/${recruiterProfileId}/approval?${params}`,
        {
          method: "PATCH",
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Unable to update recruiter approval.");
      }
      setRecruiters((currentRecruiters) => currentRecruiters.map((recruiter) => (
        recruiter.id === recruiterProfileId
          ? { ...recruiter, is_approved: !currentApproved }
          : recruiter
      )));
    } catch (error) {
      console.error("Recruiter approval update failed.", error);
      window.alert("Unable to update recruiter approval. Check recruiter email and company verification status.");
    }
  };

  const handleUpdateRequestStatus = async (reqId: number, newStatus: string) => {
    const token = getAuthToken();
    try {
      const res = await fetch(`${API_BASE_URL}/admin/employer-requests/${reqId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ status: newStatus }),
      });
      if (res.ok) {
        const updated = await res.json();
        setEmployerRequests(employerRequests.map((r) => (r.id === reqId ? updated : r)));
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleApproveJob = async (jobId: number) => {
    const token = getAuthToken();
    try {
      const res = await fetch(`${API_BASE_URL}/admin/jobs/${jobId}/approve`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        setPendingJobs(pendingJobs.filter((j) => j.id !== jobId));
        if (stats) setStats({ ...stats, published_jobs: (stats.published_jobs || 0) + 1, pending_jobs: Math.max(0, (stats.pending_jobs || 1) - 1) });
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleRejectJob = async (jobId: number) => {
    const reason = window.prompt("Please enter a mandatory rejection reason for this vacancy:");
    if (!reason || reason.trim().length < 3) {
      alert("A specific rejection reason is required to reject a vacancy.");
      return;
    }
    const token = getAuthToken();
    try {
      const res = await fetch(`${API_BASE_URL}/admin/jobs/${jobId}/reject`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ reason: reason.trim() }),
      });
      if (res.ok) {
        setPendingJobs(pendingJobs.filter((j) => j.id !== jobId));
      }
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 text-center">
        <p className="text-sm font-semibold text-brand-textSecondary">
          Loading Admin Control Center...
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
            <ShieldAlert className="w-8 h-8 text-brand-yellow" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-black text-brand-deepNavy">
                VELVORAX Platform Administration
              </h1>
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-brand-deepNavy text-brand-yellow">
                Admin Center
              </span>
            </div>
            <p className="text-xs text-brand-textSecondary mt-1">
              Logged in as <strong>{user?.full_name}</strong> ({user?.email}) • Full Operations Scope
            </p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 pb-4 mb-6 border-b border-brand-border overflow-x-auto text-xs font-bold">
        {[
          { key: "overview", label: "Executive Overview" },
          { key: "moderation", label: `Vacancy Moderation (${pendingJobs.length})` },
          { key: "users", label: `Platform Users (${users.length})` },
          { key: "companies", label: `Companies & Partners (${companies.length})` },
          { key: "requests", label: `Employer Requests (${employerRequests.length})` },
          { key: "finance", label: `Invoices & Billing (${invoices.length})` },
          { key: "audit", label: `Audit Trail (${auditLogs.length})` },
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


      {/* OVERVIEW TAB (Real DB statistics per Section 9) */}
      {activeTab === "overview" && (
        <div className="space-y-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white p-5 rounded-2xl border border-brand-border shadow-xs">
              <span className="text-xs text-brand-textSecondary font-semibold">Total Accounts</span>
              <span className="text-3xl font-black text-brand-deepNavy block mt-1">{stats?.total_users ?? 0}</span>
              <span className="text-[11px] text-brand-textSecondary block mt-0.5">
                {stats?.total_candidates ?? 0} candidates • {stats?.total_recruiters ?? 0} recruiters
              </span>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-brand-border shadow-xs">
              <span className="text-xs text-brand-textSecondary font-semibold">Active Jobs</span>
              <span className="text-3xl font-black text-brand-corpBlue block mt-1">{stats?.published_jobs ?? 0}</span>
              <span className="text-[11px] text-brand-textSecondary block mt-0.5">
                {stats?.total_jobs ?? 0} total created
              </span>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-brand-border shadow-xs">
              <span className="text-xs text-brand-textSecondary font-semibold">Application Submissions</span>
              <span className="text-3xl font-black text-brand-warning block mt-1">{stats?.total_applications ?? 0}</span>
              <span className="text-[11px] text-brand-textSecondary block mt-0.5">
                {stats?.total_interviews ?? 0} interviews conducted
              </span>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-brand-border shadow-xs">
              <span className="text-xs text-brand-textSecondary font-semibold">Financial Invoiced</span>
              <span className="text-3xl font-black text-brand-success block mt-1">
                ₹{((stats?.total_invoiced_amount || 0) / 1000).toFixed(0)}k
              </span>
              <span className="text-[11px] text-brand-textSecondary block mt-0.5">
                Verified billing records
              </span>
            </div>
          </div>
        </div>
      )}

      {/* VACANCY MODERATION TAB */}
      {activeTab === "moderation" && (
        <div className="bg-white rounded-3xl border border-brand-border p-6 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-base text-brand-deepNavy">
                Recruiter Vacancy Verification & Moderation
              </h3>
              <p className="text-xs text-brand-textSecondary mt-0.5">
                Review submitted employer positions. Approved vacancies are published globally; rejected vacancies require mandatory guidance.
              </p>
            </div>
            <span className="px-3 py-1 rounded-full text-xs font-bold bg-amber-50 text-amber-800 border border-amber-200">
              {pendingJobs.length} Pending Approval
            </span>
          </div>

          {pendingJobs.length > 0 ? (
            <div className="divide-y divide-brand-border">
              {pendingJobs.map((job) => (
                <div key={job.id} className="py-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-brand-deepNavy text-brand-yellow">
                        {job.job_type}
                      </span>
                      <h4 className="font-bold text-sm text-brand-deepNavy">{job.title}</h4>
                    </div>
                    <p className="text-xs text-brand-textSecondary">
                      Company: <strong>{job.company?.name || "Direct Recruiter"}</strong> • {job.experience_level} • {job.employment_type} • {job.work_arrangement}
                    </p>
                    <p className="text-xs text-brand-textSecondary">
                      Location: {job.city || "Remote"}, {job.state || ""}, {job.country} • Salary: ₹{job.salary_min ? (job.salary_min / 100000).toFixed(1) + 'L' : 'Best in Market'} - ₹{job.salary_max ? (job.salary_max / 100000).toFixed(1) + 'L' : ''}
                    </p>
                    {job.skills && job.skills.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1">
                        {job.skills.map((s: any, idx: number) => (
                          <span key={idx} className="px-2 py-0.5 rounded-md text-[10px] font-medium bg-brand-softBg text-brand-deepNavy">
                            {s.skill_name || s}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="flex items-center gap-2.5 shrink-0">
                    <button
                      onClick={() => handleApproveJob(job.id)}
                      className="px-4 py-2 text-xs font-bold bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl shadow-xs flex items-center gap-1.5 transition-all"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Approve & Publish</span>
                    </button>
                    <button
                      onClick={() => handleRejectJob(job.id)}
                      className="px-4 py-2 text-xs font-bold bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 rounded-xl flex items-center gap-1.5 transition-all"
                    >
                      <XCircle className="w-3.5 h-3.5 text-rose-600" />
                      <span>Reject with Reason</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-12 text-center text-xs text-brand-textSecondary">
              <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2 opacity-80" />
              <p className="font-semibold text-brand-deepNavy">All clear! No vacancies currently pending moderation.</p>
              <p className="mt-1">When recruiters submit new job positions, they will appear here for verification.</p>
            </div>
          )}
        </div>
      )}

      {/* USERS TAB */}
      {activeTab === "users" && (

        <div className="bg-white rounded-3xl border border-brand-border p-6 shadow-xs">
          <h3 className="font-bold text-base text-brand-deepNavy mb-4">
            User Accounts Management
          </h3>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-brand-border text-brand-textSecondary uppercase tracking-wider">
                  <th className="pb-3 font-bold">User</th>
                  <th className="pb-3 font-bold">Role</th>
                  <th className="pb-3 font-bold">Status</th>
                  <th className="pb-3 font-bold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-brand-border">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-brand-softBg">
                    <td className="py-3 font-semibold text-brand-deepNavy">
                      <div>{u.full_name}</div>
                      <div className="text-[11px] text-brand-textSecondary font-normal">{u.email}</div>
                    </td>
                    <td className="py-3">
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-brand-softBg text-brand-deepNavy border border-brand-border">
                        {u.role}
                      </span>
                    </td>
                    <td className="py-3">
                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          u.is_active ? "bg-emerald-100 text-emerald-800" : "bg-red-100 text-red-800"
                        }`}
                      >
                        {u.is_active ? "Active" : "Suspended"}
                      </span>
                    </td>
                    <td className="py-3 text-right">
                      <button
                        onClick={() => handleToggleUserStatus(u.id, u.is_active)}
                        className="text-xs font-bold text-brand-corpBlue hover:underline"
                      >
                        {u.is_active ? "Deactivate" : "Activate"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* COMPANIES TAB */}
      {activeTab === "companies" && (
        <div className="bg-white rounded-3xl border border-brand-border p-6 shadow-xs">
          <h3 className="font-bold text-base text-brand-deepNavy mb-4">
            Hiring Partners & Corporate Directory
          </h3>

          <div className="space-y-3">
            {companies.map((c) => (
              <div
                key={c.id}
                className="p-4 rounded-2xl border border-brand-border bg-brand-softBg space-y-4"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div>
                    <h4 className="font-bold text-xs text-brand-deepNavy">{c.name}</h4>
                    <span className="text-[11px] text-brand-textSecondary">
                      {c.city || c.country || "Global"} •{" "}
                      {c.is_verified ? "Verified Partner" : "Unverified"}
                    </span>
                    <p className="mt-1 text-[11px] text-brand-textSecondary">
                      GSTIN: {c.gstin || "Not provided"} • CIN: {c.cin || "Not provided"}
                    </p>
                    {c.verification_notes && (
                      <p className="mt-1 text-[11px] text-brand-textSecondary">
                        Review notes: {c.verification_notes}
                      </p>
                    )}
                  </div>

                  <button
                    onClick={() => handleVerifyCompany(c.id, c.is_verified)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                      c.is_verified
                        ? "bg-emerald-100 text-emerald-800 hover:bg-emerald-200"
                        : "bg-brand-yellow text-brand-deepNavy hover:bg-brand-yellowHover"
                    }`}
                  >
                    {c.is_verified ? "Verified ✓" : "Verify Partner"}
                  </button>
                </div>

                <div className="border-t border-brand-border pt-3">
                  <h5 className="text-[11px] font-bold uppercase tracking-wide text-brand-deepNavy">
                    Recruiter approvals
                  </h5>
                  <div className="mt-2 space-y-2">
                    {recruiters.filter((recruiter) => recruiter.company_id === c.id).map((recruiter) => (
                      <div key={recruiter.id} className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 rounded-xl bg-white px-3 py-2">
                        <div>
                          <p className="text-xs font-semibold text-brand-deepNavy">{recruiter.full_name}</p>
                          <p className="text-[11px] text-brand-textSecondary">
                            {recruiter.email} · {recruiter.is_verified ? "Email verified" : "Email pending"}
                          </p>
                        </div>
                        <button
                          disabled={!recruiter.is_approved && (!c.is_verified || !recruiter.is_verified || !recruiter.is_active)}
                          onClick={() => handleRecruiterApproval(recruiter.id, recruiter.is_approved)}
                          className="rounded-lg border border-brand-border px-3 py-1.5 text-[11px] font-bold text-brand-deepNavy disabled:cursor-not-allowed disabled:opacity-50"
                        >
                          {recruiter.is_approved ? "Revoke approval" : "Approve recruiter"}
                        </button>
                      </div>
                    ))}
                    {!recruiters.some((recruiter) => recruiter.company_id === c.id) && (
                      <p className="text-[11px] text-brand-textSecondary">No recruiter accounts for this company.</p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* EMPLOYER REQUESTS TAB (Section 13.3 workflow) */}
      {activeTab === "requests" && (
        <div className="bg-white rounded-3xl border border-brand-border p-6 shadow-xs">
          <h3 className="font-bold text-base text-brand-deepNavy mb-4">
            Employer Hiring Requirements Workflow
          </h3>

          {employerRequests.length > 0 ? (
            <div className="space-y-4">
              {employerRequests.map((req) => (
                <div
                  key={req.id}
                  className="p-5 rounded-2xl border border-brand-border bg-brand-softBg flex flex-col md:flex-row md:items-start justify-between gap-4"
                >
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-brand-corpBlue">
                      Request #{req.id} • {req.company_name}
                    </span>
                    <h4 className="font-bold text-sm text-brand-deepNavy mt-0.5">
                      {req.job_title} ({req.vacancies_count} vacancies)
                    </h4>
                    <p className="text-xs text-brand-textSecondary mt-0.5">
                      Contact: {req.contact_person} ({req.contact_email} {req.phone})
                    </p>
                    <p className="text-xs text-brand-textPrimary mt-2 bg-white p-3 rounded-xl border border-brand-border">
                      {req.job_description}
                    </p>
                  </div>

                  <div className="flex flex-col gap-2 flex-shrink-0">
                    <span className="px-3 py-1 rounded-full text-xs font-bold text-center bg-brand-deepNavy text-brand-yellow">
                      {req.status}
                    </span>
                    {req.status !== "CONVERTED_TO_JOB" && (
                      <button
                        onClick={() => handleUpdateRequestStatus(req.id, "CONVERTED_TO_JOB")}
                        className="px-3 py-1.5 bg-brand-yellow hover:bg-brand-yellowHover text-brand-deepNavy font-bold rounded-xl text-xs"
                      >
                        Convert to Public Job
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-brand-textSecondary py-8 text-center">
              No employer hiring requests submitted yet.
            </p>
          )}
        </div>
      )}

      {/* FINANCE TAB */}
      {activeTab === "finance" && (
        <div className="bg-white rounded-3xl border border-brand-border p-6 shadow-xs">
          <h3 className="font-bold text-base text-brand-deepNavy mb-4">
            Corporate Invoices & Payment Audit
          </h3>

          <div className="space-y-3">
            {invoices.map((inv) => (
              <div
                key={inv.id}
                className="p-4 rounded-2xl border border-brand-border bg-brand-softBg flex items-center justify-between"
              >
                <div>
                  <h4 className="font-bold text-xs text-brand-deepNavy">{inv.invoice_number}</h4>
                  <span className="text-[11px] text-brand-textSecondary">
                    Customer: {inv.customer_name} • Total: {inv.currency} {inv.total_amount?.toLocaleString()}
                  </span>
                </div>
                <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">
                  {inv.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AUDIT TRAIL TAB */}
      {activeTab === "audit" && (
        <div className="bg-white rounded-3xl border border-brand-border p-6 shadow-xs">
          <h3 className="font-bold text-base text-brand-deepNavy mb-4">
            System Security & Operations Audit Trail
          </h3>

          <div className="space-y-2 text-xs">
            {auditLogs.map((log) => (
              <div key={log.id} className="p-3 bg-brand-softBg rounded-xl border border-brand-border flex items-start justify-between">
                <div>
                  <strong className="text-brand-deepNavy">{log.action}</strong>
                  <span className="text-brand-textSecondary block mt-0.5">{log.details}</span>
                </div>
                <span className="text-[10px] text-slate-400 font-mono">
                  {formatISTDate(log.created_at, true)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
