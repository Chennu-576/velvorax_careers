"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import {
  Search,
  Filter,
  MapPin,
  Briefcase,
  SlidersHorizontal,
  X,
  ChevronLeft,
  ChevronRight,
  RotateCcw
} from "lucide-react";
import JobCard from "@/components/jobs/JobCard";
import { API_BASE_URL } from "@/lib/api";

function BrowseJobsContent() {
  const searchParams = useSearchParams();
  const router = useRouter();

  // Filters state
  const [q, setQ] = useState(searchParams.get("q") || "");
  const [jobType, setJobType] = useState(searchParams.get("job_type") || "");
  const [categoryId, setCategoryId] = useState(searchParams.get("category_id") || "");
  const [employmentType, setEmploymentType] = useState(searchParams.get("employment_type") || "");
  const [experienceLevel, setExperienceLevel] = useState(searchParams.get("experience_level") || "");
  const [workArrangement, setWorkArrangement] = useState(searchParams.get("work_arrangement") || "");
  const [country, setCountry] = useState(searchParams.get("country") || "");
  const [city, setCity] = useState(searchParams.get("city") || "");
  const [sortBy, setSortBy] = useState(searchParams.get("sort_by") || "latest");
  const [page, setPage] = useState(parseInt(searchParams.get("page") || "1"));

  const [jobs, setJobs] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [categories, setCategories] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [mobileFilterOpen, setMobileFilterOpen] = useState(false);

  // Load Categories for filter dropdown
  useEffect(() => {
    fetch(`${API_BASE_URL}/categories`)
      .then((res) => (res.ok ? res.json() : []))
      .then((data) => setCategories(data))
      .catch((err) => console.error(err));
  }, []);

  // Fetch Jobs based on active filters
  const fetchJobs = async () => {
    setLoading(true);
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (jobType) params.set("job_type", jobType);
    if (categoryId) params.set("category_id", categoryId);
    if (employmentType) params.set("employment_type", employmentType);
    if (experienceLevel) params.set("experience_level", experienceLevel);
    if (workArrangement) params.set("work_arrangement", workArrangement);
    if (country) params.set("country", country);
    if (city) params.set("city", city);
    if (sortBy) params.set("sort_by", sortBy);
    params.set("page", page.toString());
    params.set("page_size", "10");

    // Push state to URL
    router.replace(`/jobs?${params.toString()}`);

    try {
      const res = await fetch(`${API_BASE_URL}/jobs?${params.toString()}`);
      if (res.ok) {
        const data = await res.json();
        setJobs(data.items || []);
        setTotal(data.total || 0);
        setTotalPages(data.total_pages || 1);
      }
    } catch (err) {
      console.error("Error fetching jobs:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, [jobType, categoryId, employmentType, experienceLevel, workArrangement, country, sortBy, page]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchJobs();
  };

  const handleResetFilters = () => {
    setQ("");
    setJobType("");
    setCategoryId("");
    setEmploymentType("");
    setExperienceLevel("");
    setWorkArrangement("");
    setCountry("");
    setCity("");
    setSortBy("latest");
    setPage(1);
    router.replace("/jobs");
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Top Search Bar & Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-brand-deepNavy">
          Browse All Opportunities
        </h1>
        <p className="text-sm text-brand-textSecondary mt-1">
          Explore {total} published job positions matching verified enterprise requirements.
        </p>

        {/* Search input bar */}
        <form onSubmit={handleSearchSubmit} className="mt-6 flex gap-3">
          <div className="flex-1 relative">
            <Search className="w-5 h-5 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by job title, company, or keywords..."
              value={q}
              onChange={(e) => setQ(e.target.value)}
              className="w-full pl-12 pr-4 py-3.5 rounded-2xl border border-brand-border bg-white text-sm font-medium focus:outline-brand-yellow shadow-2xs"
            />
          </div>
          <button
            type="submit"
            className="px-6 py-3.5 bg-brand-yellow hover:bg-brand-yellowHover text-brand-deepNavy font-bold rounded-2xl text-sm transition-all shadow-xs flex items-center gap-2"
          >
            <span>Search</span>
          </button>
          <button
            type="button"
            onClick={() => setMobileFilterOpen(true)}
            className="lg:hidden px-4 py-3.5 bg-white border border-brand-border rounded-2xl text-brand-deepNavy font-bold text-sm flex items-center gap-1.5"
          >
            <SlidersHorizontal className="w-4 h-4" />
            <span>Filters</span>
          </button>
        </form>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Desktop Sidebar Filters */}
        <aside className="hidden lg:block space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-brand-border shadow-xs space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-brand-border">
              <span className="font-bold text-sm text-brand-deepNavy flex items-center gap-1.5">
                <SlidersHorizontal className="w-4 h-4 text-brand-yellow" />
                Refine Search
              </span>
              <button
                onClick={handleResetFilters}
                className="text-xs text-brand-textSecondary hover:text-brand-error flex items-center gap-1"
              >
                <RotateCcw className="w-3 h-3" />
                Reset
              </button>
            </div>

            {/* Job Classification (IT / Non-IT) */}
            <div>
              <label className="block text-xs font-bold text-brand-deepNavy uppercase tracking-wider mb-2">
                Classification
              </label>
              <div className="grid grid-cols-2 gap-2">
                {["", "IT", "NON_IT"].map((type) => (
                  <button
                    key={type}
                    type="button"
                    onClick={() => {
                      setJobType(type);
                      setPage(1);
                    }}
                    className={`py-2 text-xs font-bold rounded-xl border transition-all ${
                      jobType === type
                        ? "bg-brand-deepNavy text-brand-yellow border-brand-deepNavy shadow-xs"
                        : "bg-brand-softBg text-brand-textPrimary border-brand-border hover:bg-white"
                    }`}
                  >
                    {type === "" ? "All" : type === "IT" ? "IT Tech" : "Non-IT"}
                  </button>
                ))}
              </div>
            </div>

            {/* Category */}
            <div>
              <label className="block text-xs font-bold text-brand-deepNavy uppercase tracking-wider mb-2">
                Category
              </label>
              <select
                value={categoryId}
                onChange={(e) => {
                  setCategoryId(e.target.value);
                  setPage(1);
                }}
                className="w-full p-2.5 rounded-xl border border-brand-border bg-white text-xs font-medium focus:outline-brand-yellow"
              >
                <option value="">All Categories</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Work Arrangement */}
            <div>
              <label className="block text-xs font-bold text-brand-deepNavy uppercase tracking-wider mb-2">
                Work Arrangement
              </label>
              <div className="space-y-1.5 text-xs text-brand-textPrimary">
                {["", "Remote", "Hybrid", "On-site"].map((w) => (
                  <label key={w} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="workArrangement"
                      checked={workArrangement === w}
                      onChange={() => {
                        setWorkArrangement(w);
                        setPage(1);
                      }}
                      className="accent-brand-yellow"
                    />
                    <span>{w === "" ? "Any Arrangement" : w}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Experience Level */}
            <div>
              <label className="block text-xs font-bold text-brand-deepNavy uppercase tracking-wider mb-2">
                Experience Level
              </label>
              <select
                value={experienceLevel}
                onChange={(e) => {
                  setExperienceLevel(e.target.value);
                  setPage(1);
                }}
                className="w-full p-2.5 rounded-xl border border-brand-border bg-white text-xs font-medium focus:outline-brand-yellow"
              >
                <option value="">Any Experience</option>
                <option value="Fresher">Fresher</option>
                <option value="Junior">Junior (1-3 yrs)</option>
                <option value="Mid-level">Mid-level (3-5 yrs)</option>
                <option value="Senior">Senior (5-8 yrs)</option>
                <option value="Lead">Lead / Principal</option>
                <option value="Manager">Manager / Executive</option>
              </select>
            </div>

            {/* Employment Type */}
            <div>
              <label className="block text-xs font-bold text-brand-deepNavy uppercase tracking-wider mb-2">
                Employment Type
              </label>
              <select
                value={employmentType}
                onChange={(e) => {
                  setEmploymentType(e.target.value);
                  setPage(1);
                }}
                className="w-full p-2.5 rounded-xl border border-brand-border bg-white text-xs font-medium focus:outline-brand-yellow"
              >
                <option value="">Any Type</option>
                <option value="Full-time">Full-time</option>
                <option value="Part-time">Part-time</option>
                <option value="Contract">Contract</option>
                <option value="Internship">Internship</option>
              </select>
            </div>
          </div>
        </aside>

        {/* Main Job Results Feed */}
        <main className="lg:col-span-3 space-y-6">
          {/* Sorting and Results count header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between bg-white px-5 py-3 rounded-2xl border border-brand-border gap-3 text-xs">
            <span className="font-semibold text-brand-deepNavy">
              Showing <span className="text-brand-corpBlue">{jobs.length}</span> of{" "}
              <span className="text-brand-corpBlue">{total}</span> positions
            </span>

            <div className="flex items-center gap-2">
              <span className="text-brand-textSecondary">Sort by:</span>
              <select
                value={sortBy}
                onChange={(e) => {
                  setSortBy(e.target.value);
                  setPage(1);
                }}
                className="bg-transparent font-bold text-brand-deepNavy focus:outline-none cursor-pointer"
              >
                <option value="latest">Latest Jobs</option>
                <option value="oldest">Oldest</option>
                <option value="salary_desc">Salary: High to Low</option>
                <option value="salary_asc">Salary: Low to High</option>
                <option value="popular">Most Viewed</option>
              </select>
            </div>
          </div>

          {/* Job Cards List */}
          {loading ? (
            <div className="space-y-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-44 bg-white rounded-2xl border border-brand-border animate-pulse" />
              ))}
            </div>
          ) : jobs.length > 0 ? (
            <div className="space-y-4">
              {jobs.map((job) => (
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
            <div className="bg-white p-12 text-center rounded-3xl border border-brand-border space-y-3">
              <Briefcase className="w-12 h-12 text-slate-300 mx-auto" />
              <h3 className="font-bold text-base text-brand-deepNavy">
                No matching opportunities found
              </h3>
              <p className="text-xs text-brand-textSecondary max-w-sm mx-auto">
                Try widening your search terms or resetting filters to browse all open vacancies.
              </p>
              <button
                onClick={handleResetFilters}
                className="mt-4 px-5 py-2 bg-brand-yellow font-bold text-xs text-brand-deepNavy rounded-xl"
              >
                Reset Filters
              </button>
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 pt-6">
              <button
                disabled={page <= 1}
                onClick={() => setPage(page - 1)}
                className="p-2 rounded-xl border border-brand-border bg-white disabled:opacity-40 hover:bg-brand-softBg"
              >
                <ChevronLeft className="w-5 h-5 text-brand-deepNavy" />
              </button>
              <span className="px-4 text-xs font-bold text-brand-deepNavy">
                Page {page} of {totalPages}
              </span>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage(page + 1)}
                className="p-2 rounded-xl border border-brand-border bg-white disabled:opacity-40 hover:bg-brand-softBg"
              >
                <ChevronRight className="w-5 h-5 text-brand-deepNavy" />
              </button>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default function BrowseJobsPage() {
  return (
    <Suspense fallback={<div className="p-12 text-center">Loading jobs catalog...</div>}>
      <BrowseJobsContent />
    </Suspense>
  );
}
