"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Briefcase, Users, DollarSign, TrendingUp, Headphones, Scale, ArrowRight } from "lucide-react";
import JobCard from "@/components/jobs/JobCard";
import { API_BASE_URL } from "@/lib/api";

export default function NonITJobsPage() {
  const [categories, setCategories] = useState<any[]>([]);
  const [jobs, setJobs] = useState<any[]>([]);
  const [selectedCat, setSelectedCat] = useState<string>("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [catsRes, jobsRes] = await Promise.all([
          fetch(`${API_BASE_URL}/categories?category_type=NON_IT`),
          fetch(`${API_BASE_URL}/jobs?job_type=NON_IT&page_size=12`),
        ]);

        if (catsRes.ok) {
          const catsData = await catsRes.json();
          setCategories(catsData || []);
        }
        if (jobsRes.ok) {
          const jobsData = await jobsRes.json();
          setJobs(jobsData.items || []);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleCategoryFilter = async (catSlug: string) => {
    setSelectedCat(catSlug);
    setLoading(true);
    try {
      const url = catSlug
        ? `${API_BASE_URL}/jobs?job_type=NON_IT&category_slug=${catSlug}`
        : `${API_BASE_URL}/jobs?job_type=NON_IT`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setJobs(data.items || []);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      {/* Header Banner */}
      <section className="bg-brand-deepNavy text-white py-16 border-b border-brand-secondaryNavy">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-brand-secondaryNavy text-brand-yellow text-xs font-semibold mb-4 border border-brand-border/20">
            <Briefcase className="w-3.5 h-3.5" />
            <span>Corporate, Business & Operations Division</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-white">
            Non-IT & Corporate Management Opportunities
          </h1>
          <p className="mt-2 text-sm text-slate-300 max-w-2xl leading-relaxed">
            Discover roles in Human Resources, Talent Acquisition, Finance & Accounting, Enterprise B2B Sales, Performance Marketing, and Global Operations.
          </p>
        </div>
      </section>

      {/* Categories Grid */}
      <section className="py-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-brand-deepNavy">
            Business & Operational Domains
          </h2>
          {selectedCat && (
            <button
              onClick={() => handleCategoryFilter("")}
              className="text-xs font-bold text-brand-corpBlue hover:underline"
            >
              Clear filter ({selectedCat})
            </button>
          )}
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3.5 mb-12">
          {categories.map((cat) => {
            const isSelected = selectedCat === cat.slug;
            return (
              <button
                key={cat.id}
                onClick={() => handleCategoryFilter(isSelected ? "" : cat.slug)}
                className={`p-4 rounded-2xl border text-left transition-all ${
                  isSelected
                    ? "bg-brand-deepNavy text-white border-brand-deepNavy shadow-md"
                    : "bg-white text-brand-deepNavy border-brand-border hover:border-brand-yellow"
                }`}
              >
                <div
                  className={`w-8 h-8 rounded-lg flex items-center justify-center mb-2.5 ${
                    isSelected ? "bg-brand-yellow text-brand-deepNavy" : "bg-brand-softBg text-brand-corpBlue"
                  }`}
                >
                  <Briefcase className="w-4 h-4" />
                </div>
                <h4 className="font-bold text-xs line-clamp-1">{cat.name}</h4>
                <span
                  className={`text-[11px] font-semibold mt-1 inline-block ${
                    isSelected ? "text-brand-yellow" : "text-brand-textSecondary"
                  }`}
                >
                  {cat.active_jobs_count} open jobs
                </span>
              </button>
            );
          })}
        </div>

        {/* Jobs Feed */}
        <div className="flex items-center justify-between mb-6 pb-3 border-b border-brand-border">
          <span className="font-bold text-sm text-brand-deepNavy">
            Available Positions ({jobs.length})
          </span>
          <Link
            href="/jobs?job_type=NON_IT"
            className="text-xs font-bold text-brand-deepNavy hover:text-brand-corpBlue flex items-center gap-1"
          >
            <span>Advanced Filters</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-56 bg-slate-200 animate-pulse rounded-2xl" />
            ))}
          </div>
        ) : jobs.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {jobs.map((job) => (
              <JobCard
                key={job.id}
                id={job.id}
                title={job.title}
                slug={job.slug}
                companyName={job.company?.name || "VELVORAX"}
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
          <div className="bg-white p-12 text-center rounded-3xl border border-brand-border">
            <p className="text-sm text-brand-textSecondary">
              No Non-IT positions matching this filter right now.
            </p>
          </div>
        )}
      </section>
    </div>
  );
}
