"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Search,
  MapPin,
  Briefcase,
  ArrowRight,
  Sparkles,
  CheckCircle,
  Building,
  TrendingUp,
  ShieldCheck,
  Send
} from "lucide-react";
import JobCard from "@/components/jobs/JobCard";
import { API_BASE_URL } from "@/lib/api";

export default function HomePage() {
  const router = useRouter();
  const [keyword, setKeyword] = useState("");
  const [category, setCategory] = useState("");
  const [location, setLocation] = useState("");

  const [featuredJobs, setFeaturedJobs] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Employer hiring request modal / mini-form
  const [empModalOpen, setEmpModalOpen] = useState(false);
  const [empForm, setEmpForm] = useState({
    company_name: "",
    contact_person: "",
    contact_email: "",
    phone: "",
    job_title: "",
    vacancies_count: 1,
    job_description: "",
  });
  const [empSuccess, setEmpSuccess] = useState(false);
  const [empSubmitting, setEmpSubmitting] = useState(false);

  useEffect(() => {
    async function loadData() {
      try {
        const [jobsRes, catsRes] = await Promise.all([
          fetch(`${API_BASE_URL}/jobs?is_featured=true&page_size=6`),
          fetch(`${API_BASE_URL}/categories`),
        ]);

        if (jobsRes.ok) {
          const jobsData = await jobsRes.json();
          setFeaturedJobs(jobsData.items || []);
        }

        if (catsRes.ok) {
          const catsData = await catsRes.json();
          setCategories(catsData || []);
        }
      } catch (err) {
        console.error("Error fetching homepage data:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams();
    if (keyword) params.set("q", keyword);
    if (category) params.set("category_id", category);
    if (location) params.set("city", location);
    router.push(`/jobs?${params.toString()}`);
  };

  const handleEmployerSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setEmpSubmitting(true);
    try {
      const res = await fetch(`${API_BASE_URL}/employer-requests`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(empForm),
      });
      if (res.ok) {
        setEmpSuccess(true);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setEmpSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      {/* HERO SECTION */}
      <section className="relative bg-brand-deepNavy text-white py-20 lg:py-28 overflow-hidden">
        {/* Subtle geometric background accents */}
        <div className="absolute inset-0 opacity-10 bg-[radial-gradient(#FACC15_1px,transparent_1px)] [background-size:24px_24px]" />
        <div className="absolute top-1/4 -right-20 w-96 h-96 bg-brand-corpBlue/30 rounded-full blur-3xl pointer-events-none" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-brand-secondaryNavy border border-brand-border/20 text-brand-yellow text-xs font-semibold mb-6 animate-pulse">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI-Driven Recruitment & Career Development Platform</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight text-white max-w-4xl mx-auto leading-tight">
            Build Your Future With{" "}
            <span className="text-brand-yellow">VELVORAX</span>
          </h1>

          <p className="mt-5 text-base sm:text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed">
            Discover verified opportunities, connect directly with hiring companies, and accelerate your professional career trajectory.
          </p>

          {/* Search Box Form */}
          <div className="mt-10 max-w-4xl mx-auto">
            <form
              onSubmit={handleSearch}
              className="bg-white p-3 rounded-2xl shadow-xl border border-brand-border/60 flex flex-col md:flex-row gap-2.5 text-brand-textPrimary"
            >
              <div className="flex-1 flex items-center gap-2.5 px-3 py-2 border-b md:border-b-0 md:border-r border-brand-border">
                <Search className="w-5 h-5 text-slate-400 flex-shrink-0" />
                <input
                  type="text"
                  placeholder="Job title, keywords, or skills..."
                  value={keyword}
                  onChange={(e) => setKeyword(e.target.value)}
                  className="w-full bg-transparent focus:outline-none text-sm font-medium"
                />
              </div>

              <div className="flex-1 flex items-center gap-2.5 px-3 py-2 border-b md:border-b-0 md:border-r border-brand-border">
                <Briefcase className="w-5 h-5 text-slate-400 flex-shrink-0" />
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full bg-transparent focus:outline-none text-sm font-medium text-slate-600"
                >
                  <option value="">All Categories</option>
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex-1 flex items-center gap-2.5 px-3 py-2">
                <MapPin className="w-5 h-5 text-slate-400 flex-shrink-0" />
                <input
                  type="text"
                  placeholder="Location or remote..."
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="w-full bg-transparent focus:outline-none text-sm font-medium"
                />
              </div>

              <button
                type="submit"
                className="px-7 py-3 bg-brand-yellow hover:bg-brand-yellowHover text-brand-deepNavy font-bold text-sm rounded-xl transition-all shadow-md flex items-center justify-center gap-2"
              >
                <span>Search Jobs</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </form>
          </div>

          {/* Quick Links */}
          <div className="mt-8 flex flex-wrap items-center justify-center gap-4 text-xs text-slate-400">
            <span className="font-semibold text-slate-300">Popular Searches:</span>
            <Link href="/it-jobs" className="hover:text-brand-yellow transition-colors underline">
              Full-Stack Developer
            </Link>
            <Link href="/it-jobs" className="hover:text-brand-yellow transition-colors underline">
              Python FastAPI
            </Link>
            <Link href="/it-jobs" className="hover:text-brand-yellow transition-colors underline">
              AI Automation
            </Link>
            <Link href="/non-it-jobs" className="hover:text-brand-yellow transition-colors underline">
              Talent Acquisition
            </Link>
          </div>
        </div>
      </section>

      {/* FEATURED JOBS SECTION */}
      <section className="py-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-10">
          <div>
            <span className="text-xs font-bold uppercase tracking-widest text-brand-corpBlue">
              Verified Hiring
            </span>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-brand-deepNavy mt-1">
              Featured Opportunities
            </h2>
            <p className="text-sm text-brand-textSecondary mt-1">
              Hand-picked openings from VELVORAX and certified hiring partners.
            </p>
          </div>
          <Link
            href="/jobs"
            className="mt-4 sm:mt-0 inline-flex items-center gap-1.5 text-sm font-bold text-brand-deepNavy hover:text-brand-corpBlue transition-colors group"
          >
            <span>View All Jobs</span>
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="h-64 bg-slate-200 animate-pulse rounded-2xl" />
            ))}
          </div>
        ) : featuredJobs.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {featuredJobs.map((job) => (
              <JobCard
                key={job.id}
                id={job.id}
                title={job.title}
                slug={job.slug}
                companyName={job.company?.name || "VELVORAX Software Solutions"}
                companyLogo={job.company?.logo_url}
                isVerified={job.company?.is_verified}
                location={`${job.city || ""}, ${job.country}`}
                employmentType={job.employment_type}
                workArrangement={job.work_arrangement}
                experienceLevel={job.experience_level}
                salary={
                  job.salary_min
                    ? `${job.salary_currency} ${job.salary_min.toLocaleString()} - ${
                        job.salary_max ? job.salary_max.toLocaleString() : ""
                      }`
                    : "Competitive"
                }
                skills={job.skills?.map((s: any) => s.skill_name) || []}
                postedDate={new Date(job.created_at).toLocaleDateString()}
                descriptionPreview={job.description}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-12 bg-white rounded-2xl border border-brand-border">
            <p className="text-brand-textSecondary">No featured jobs found at the moment.</p>
          </div>
        )}
      </section>

      {/* DYNAMIC JOB CATEGORIES DIRECTORY */}
      <section className="py-16 bg-white border-y border-brand-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <span className="text-xs font-bold uppercase tracking-widest text-brand-corpBlue">
              Comprehensive Directory
            </span>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-brand-deepNavy mt-1">
              Explore by Department & Category
            </h2>
            <p className="text-sm text-brand-textSecondary mt-2">
              Browse dynamically managed career opportunities across specialized IT and enterprise Non-IT domains.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {categories.slice(0, 8).map((cat) => (
              <Link
                key={cat.id}
                href={`/job-categories/${cat.slug}`}
                className="group p-5 rounded-2xl border border-brand-border hover:border-brand-yellow/80 hover:shadow-md transition-all bg-brand-softBg hover:bg-white flex flex-col justify-between"
              >
                <div>
                  <div className="w-10 h-10 rounded-xl bg-white border border-brand-border flex items-center justify-center text-brand-deepNavy group-hover:bg-brand-yellow transition-colors mb-3">
                    <Briefcase className="w-5 h-5" />
                  </div>
                  <h3 className="font-bold text-sm text-brand-deepNavy group-hover:text-brand-corpBlue">
                    {cat.name}
                  </h3>
                  <p className="text-xs text-brand-textSecondary mt-1 line-clamp-2">
                    {cat.description || "Explore specialized positions and career paths."}
                  </p>
                </div>
                <div className="mt-4 pt-3 border-t border-brand-border/60 flex items-center justify-between text-xs">
                  <span className="font-semibold text-brand-deepNavy">
                    {cat.active_jobs_count} Open Jobs
                  </span>
                  <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-brand-deepNavy group-hover:translate-x-0.5 transition-all" />
                </div>
              </Link>
            ))}
          </div>

          <div className="mt-8 text-center">
            <Link
              href="/job-categories"
              className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl border border-brand-border text-xs font-bold text-brand-deepNavy hover:bg-brand-softBg transition-colors"
            >
              <span>Explore All Categories</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </section>

      {/* WHY VELVORAX & HOW IT WORKS */}
      <section className="py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div>
            <span className="text-xs font-bold uppercase tracking-widest text-brand-corpBlue">
              The VELVORAX Advantage
            </span>
            <h2 className="text-3xl font-extrabold text-brand-deepNavy mt-1 leading-snug">
              Why Professionals Choose VELVORAX Careers
            </h2>
            <p className="text-sm text-brand-textSecondary mt-3 leading-relaxed">
              We connect ambitious professionals directly with vetted hiring partners through verified salary disclosures, transparent interview scheduling, and intelligent skill matchmaking.
            </p>

            <div className="mt-8 space-y-4">
              {[
                {
                  title: "Direct Access to Verified Partners",
                  desc: "Zero spam recruiters. Only authenticated corporate entities and verified enterprise hiring managers.",
                },
                {
                  title: "Transparent Recruitment Pipeline",
                  desc: "Real-time application status tracking from submission to technical interview and offer release.",
                },
                {
                  title: "Global & Domestic Opportunities",
                  desc: "From local Hyderabad innovation hubs to remote worldwide engineering opportunities.",
                },
                {
                  title: "Strict Candidate Privacy Vault",
                  desc: "Your resumes and credentials are secure in private object storage, never leaked to third parties.",
                },
              ].map((item, idx) => (
                <div key={idx} className="flex items-start gap-3.5">
                  <div className="w-6 h-6 rounded-full bg-brand-yellow/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <CheckCircle className="w-4 h-4 text-brand-deepNavy" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-brand-deepNavy">{item.title}</h4>
                    <p className="text-xs text-brand-textSecondary mt-0.5">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white p-8 rounded-3xl border border-brand-border shadow-md">
            <span className="text-xs font-bold uppercase tracking-widest text-brand-yellow">
              Candidate Journey
            </span>
            <h3 className="text-xl font-bold text-brand-deepNavy mt-1 mb-6">
              How It Works
            </h3>

            <div className="space-y-6">
              {[
                { step: "01", title: "Create Your Unified Account", text: "Register in under 60 seconds with candidate profile details." },
                { step: "02", title: "Upload Verified Resume", text: "Securely upload your PDF or DOCX resume to our private vault." },
                { step: "03", title: "Discover & Apply", text: "Filter by location, role, and salary, then apply with one click." },
                { step: "04", title: "Track & Interview", text: "Receive real interview invites and status updates directly in your dashboard." },
              ].map((s, idx) => (
                <div key={idx} className="flex items-start gap-4">
                  <span className="text-lg font-black text-brand-yellow bg-brand-deepNavy px-3 py-1 rounded-xl">
                    {s.step}
                  </span>
                  <div>
                    <h4 className="text-sm font-bold text-brand-deepNavy">{s.title}</h4>
                    <p className="text-xs text-brand-textSecondary mt-0.5">{s.text}</p>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-8 pt-6 border-t border-brand-border flex items-center justify-between">
              <Link
                href="/register"
                className="w-full text-center py-3 bg-brand-yellow hover:bg-brand-yellowHover text-brand-deepNavy font-bold text-sm rounded-xl transition-all shadow-xs"
              >
                Start Your Career Journey
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* EMPLOYER HIRING REQUEST CTA BANNER */}
      <section className="bg-brand-secondaryNavy text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white">
            Are You an Employer Looking for Top Talent?
          </h2>
          <p className="text-sm text-slate-300 max-w-2xl mx-auto mt-2 leading-relaxed">
            Submit your hiring requirements directly to VELVORAX Talent Acquisition. Our specialized recruiters evaluate and match pre-screened engineering and corporate professionals.
          </p>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
            <button
              onClick={() => setEmpModalOpen(true)}
              className="px-6 py-3 bg-brand-yellow hover:bg-brand-yellowHover text-brand-deepNavy font-bold text-sm rounded-xl shadow-md transition-all flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
              <span>Submit Hiring Requirement</span>
            </button>
            <Link
              href="/register"
              className="px-6 py-3 border border-white/20 hover:bg-white/10 text-white font-semibold text-sm rounded-xl transition-colors"
            >
              Recruiter Registration
            </Link>
          </div>
        </div>
      </section>

      {/* EMPLOYER REQUIREMENT MODAL */}
      {empModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-xs">
          <div className="bg-white rounded-3xl max-w-lg w-full p-6 sm:p-8 shadow-2xl border border-brand-border animate-scaleIn max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-4 border-b border-brand-border">
              <h3 className="text-lg font-bold text-brand-deepNavy">
                Submit Hiring Requirement
              </h3>
              <button
                onClick={() => {
                  setEmpModalOpen(false);
                  setEmpSuccess(false);
                }}
                className="text-slate-400 hover:text-brand-deepNavy text-xl"
              >
                ✕
              </button>
            </div>

            {empSuccess ? (
              <div className="py-8 text-center">
                <CheckCircle className="w-12 h-12 text-brand-success mx-auto mb-3" />
                <h4 className="text-lg font-bold text-brand-deepNavy">Request Received!</h4>
                <p className="text-xs text-brand-textSecondary mt-2">
                  Our talent acquisition team has received your hiring requirement and will review it promptly.
                </p>
                <button
                  onClick={() => {
                    setEmpModalOpen(false);
                    setEmpSuccess(false);
                  }}
                  className="mt-6 px-6 py-2 bg-brand-deepNavy text-white rounded-xl text-xs font-bold"
                >
                  Close
                </button>
              </div>
            ) : (
              <form onSubmit={handleEmployerSubmit} className="mt-5 space-y-4 text-xs">
                <div>
                  <label className="block font-semibold text-brand-deepNavy mb-1">Company Name</label>
                  <input
                    type="text"
                    required
                    value={empForm.company_name}
                    onChange={(e) => setEmpForm({ ...empForm, company_name: e.target.value })}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-brand-border focus:outline-brand-yellow"
                    placeholder="e.g. Acme Corporation"
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block font-semibold text-brand-deepNavy mb-1">Contact Person</label>
                    <input
                      type="text"
                      required
                      value={empForm.contact_person}
                      onChange={(e) => setEmpForm({ ...empForm, contact_person: e.target.value })}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-brand-border focus:outline-brand-yellow"
                      placeholder="Your Name"
                    />
                  </div>
                  <div>
                    <label className="block font-semibold text-brand-deepNavy mb-1">Work Email</label>
                    <input
                      type="email"
                      required
                      value={empForm.contact_email}
                      onChange={(e) => setEmpForm({ ...empForm, contact_email: e.target.value })}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-brand-border focus:outline-brand-yellow"
                      placeholder="hr@company.com"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block font-semibold text-brand-deepNavy mb-1">Job Title</label>
                    <input
                      type="text"
                      required
                      value={empForm.job_title}
                      onChange={(e) => setEmpForm({ ...empForm, job_title: e.target.value })}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-brand-border focus:outline-brand-yellow"
                      placeholder="e.g. Lead Python Engineer"
                    />
                  </div>
                  <div>
                    <label className="block font-semibold text-brand-deepNavy mb-1">Number of Vacancies</label>
                    <input
                      type="number"
                      min={1}
                      value={empForm.vacancies_count}
                      onChange={(e) => setEmpForm({ ...empForm, vacancies_count: parseInt(e.target.value) || 1 })}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-brand-border focus:outline-brand-yellow"
                    />
                  </div>
                </div>
                <div>
                  <label className="block font-semibold text-brand-deepNavy mb-1">Requirement Overview</label>
                  <textarea
                    rows={3}
                    required
                    value={empForm.job_description}
                    onChange={(e) => setEmpForm({ ...empForm, job_description: e.target.value })}
                    className="w-full px-3.5 py-2 rounded-xl border border-brand-border focus:outline-brand-yellow"
                    placeholder="Describe key responsibilities, experience range, and compensation..."
                  />
                </div>
                <div className="pt-2">
                  <button
                    type="submit"
                    disabled={empSubmitting}
                    className="w-full py-3 bg-brand-yellow hover:bg-brand-yellowHover text-brand-deepNavy font-bold rounded-xl shadow-xs transition-all text-sm"
                  >
                    {empSubmitting ? "Submitting..." : "Send Hiring Request"}
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
