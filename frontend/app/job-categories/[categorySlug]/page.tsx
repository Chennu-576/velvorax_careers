"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ChevronRight, Briefcase, Code, ArrowRight, ArrowLeft } from "lucide-react";
import JobCard from "@/components/jobs/JobCard";
import { API_BASE_URL } from "@/lib/api";

export default function SubcategoryDetailsPage() {
  const params = useParams();
  const categorySlug = params.categorySlug as string;

  const [category, setCategory] = useState<any>(null);
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [catRes, jobsRes] = await Promise.all([
          fetch(`${API_BASE_URL}/categories/${categorySlug}`),
          fetch(`${API_BASE_URL}/jobs?category_slug=${categorySlug}&page_size=12`),
        ]);

        if (catRes.ok) {
          setCategory(await catRes.json());
        }
        if (jobsRes.ok) {
          const jData = await jobsRes.json();
          setJobs(jData.items || []);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    if (categorySlug) {
      loadData();
    }
  }, [categorySlug]);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <p className="text-brand-textSecondary text-sm">Loading category details...</p>
      </div>
    );
  }

  if (!category) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <h2 className="text-xl font-bold text-brand-deepNavy">Category Not Found</h2>
        <Link href="/job-categories" className="mt-4 inline-block text-xs font-bold text-brand-corpBlue underline">
          Back to Categories Directory
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-xs text-brand-textSecondary mb-6">
        <Link href="/" className="hover:text-brand-deepNavy">
          Home
        </Link>
        <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
        <Link href="/job-categories" className="hover:text-brand-deepNavy">
          Job Categories
        </Link>
        <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
        <span className="font-bold text-brand-deepNavy">{category.name}</span>
      </nav>

      {/* Header Banner */}
      <div className="bg-white rounded-3xl border border-brand-border p-8 mb-10 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div className="inline-block px-3 py-1 rounded-full text-[11px] font-bold bg-brand-softBg text-brand-corpBlue mb-2 border border-brand-border">
            {category.category_type} Division
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-brand-deepNavy">
            {category.name}
          </h1>
          <p className="text-sm text-brand-textSecondary mt-2 max-w-2xl leading-relaxed">
            {category.description || "Explore specialized career pathways and open positions in this domain."}
          </p>
        </div>

        <div className="p-4 bg-brand-softBg rounded-2xl border border-brand-border text-center flex-shrink-0">
          <span className="text-2xl font-black text-brand-deepNavy">
            {category.active_jobs_count}
          </span>
          <span className="block text-xs font-semibold text-brand-textSecondary mt-0.5">
            Active Openings
          </span>
        </div>
      </div>

      {/* Subcategories Pills */}
      {category.subcategories && category.subcategories.length > 0 && (
        <div className="mb-10">
          <h3 className="text-sm font-bold text-brand-deepNavy uppercase tracking-wider mb-4">
            Subcategories & Focus Areas
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {category.subcategories.map((sub: any) => (
              <div
                key={sub.id}
                className="p-4 bg-white rounded-xl border border-brand-border hover:border-brand-yellow shadow-2xs transition-all"
              >
                <h4 className="font-bold text-xs text-brand-deepNavy">{sub.name}</h4>
                <p className="text-[11px] text-brand-textSecondary mt-1 line-clamp-1">
                  {sub.description || "Specialized focus tracks."}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Jobs Feed for this Category */}
      <div className="mb-6 flex items-center justify-between pb-3 border-b border-brand-border">
        <h3 className="text-base font-bold text-brand-deepNavy">
          Available Positions in {category.name}
        </h3>
        <Link
          href={`/jobs?category_id=${category.id}`}
          className="text-xs font-bold text-brand-corpBlue hover:underline flex items-center gap-1"
        >
          <span>View in Search Filter</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>

      {jobs.length > 0 ? (
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
            No active positions listed in this subcategory currently.
          </p>
        </div>
      )}
    </div>
  );
}
