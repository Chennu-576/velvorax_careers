"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Globe2, MapPin, Search, Plane, ShieldCheck, ArrowRight, Building2 } from "lucide-react";
import JobCard from "@/components/jobs/JobCard";
import { API_BASE_URL } from "@/lib/api";

export default function GlobalJobsPage() {
  const [countries, setCountries] = useState<any[]>([]);
  const [selectedRegion, setSelectedRegion] = useState<string>("ALL");
  const [selectedCountry, setSelectedCountry] = useState<string>("");
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const regions = ["ALL", "Asia", "Europe", "North America", "Middle East"];

  useEffect(() => {
    async function loadData() {
      try {
        const [cRes, jRes] = await Promise.all([
          fetch(`${API_BASE_URL}/locations/countries`),
          fetch(`${API_BASE_URL}/jobs?page_size=12`),
        ]);

        if (cRes.ok) {
          const cData = await cRes.json();
          setCountries(cData || []);
        }
        if (jRes.ok) {
          const jData = await jRes.json();
          setJobs(jData.items || []);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleCountryFilter = async (countryName: string) => {
    setSelectedCountry(countryName);
    setLoading(true);
    try {
      const url = countryName
        ? `${API_BASE_URL}/jobs?country=${encodeURIComponent(countryName)}`
        : `${API_BASE_URL}/jobs`;
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

  const filteredCountries = countries.filter((c) =>
    selectedRegion === "ALL" ? true : c.region === selectedRegion
  );

  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Banner */}
      <section className="bg-brand-deepNavy text-white py-16 border-b border-brand-secondaryNavy">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-brand-secondaryNavy text-brand-yellow text-xs font-semibold mb-4 border border-brand-border/20">
            <Globe2 className="w-3.5 h-3.5" />
            <span>Worldwide Career Discovery</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-white">
            Global Opportunities & International Roles
          </h1>
          <p className="mt-2 text-sm text-slate-300 max-w-2xl leading-relaxed">
            Discover verified tech, corporate, and executive opportunities across India, North America, Europe, Asia-Pacific, and the Middle East.
          </p>
        </div>
      </section>

      {/* Country Directory & Region Tabs */}
      <section className="py-12 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <h2 className="text-xl font-bold text-brand-deepNavy">
              Global Country Directory
            </h2>
            <p className="text-xs text-brand-textSecondary mt-0.5">
              Select a destination to filter open positions backed by our geographic database.
            </p>
          </div>

          {/* Region Tabs */}
          <div className="flex flex-wrap gap-1 p-1 bg-white border border-brand-border rounded-xl">
            {regions.map((reg) => (
              <button
                key={reg}
                onClick={() => setSelectedRegion(reg)}
                className={`px-3 py-1.5 text-xs font-bold rounded-lg transition-all ${
                  selectedRegion === reg
                    ? "bg-brand-deepNavy text-brand-yellow shadow-xs"
                    : "text-brand-textSecondary hover:text-brand-deepNavy"
                }`}
              >
                {reg}
              </button>
            ))}
          </div>
        </div>

        {/* Countries Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3.5 mb-12">
          {filteredCountries.map((c) => {
            const isSelected = selectedCountry === c.name;
            return (
              <button
                key={c.id}
                onClick={() => handleCountryFilter(isSelected ? "" : c.name)}
                className={`p-4 rounded-2xl border text-left transition-all ${
                  isSelected
                    ? "bg-brand-deepNavy text-white border-brand-deepNavy shadow-md"
                    : "bg-white text-brand-deepNavy border-brand-border hover:border-brand-yellow"
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-2xl">{c.flag_emoji || "🌐"}</span>
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                      isSelected ? "bg-white/20 text-brand-yellow" : "bg-brand-softBg text-brand-corpBlue"
                    }`}
                  >
                    {c.iso2}
                  </span>
                </div>
                <h4 className="font-bold text-xs line-clamp-1">{c.name}</h4>
                <div
                  className={`text-[11px] font-semibold mt-1 ${
                    isSelected ? "text-brand-yellow" : "text-brand-textSecondary"
                  }`}
                >
                  {c.active_jobs_count} open jobs
                </div>
              </button>
            );
          })}
        </div>

        {/* Global Jobs Feed */}
        <div className="flex items-center justify-between mb-6 pb-3 border-b border-brand-border">
          <div className="flex items-center gap-2">
            <span className="font-bold text-sm text-brand-deepNavy">
              Positions {selectedCountry ? `in ${selectedCountry}` : "Worldwide"} ({jobs.length})
            </span>
            {selectedCountry && (
              <button
                onClick={() => handleCountryFilter("")}
                className="text-xs text-brand-corpBlue font-bold hover:underline"
              >
                (Clear country filter)
              </button>
            )}
          </div>
          <Link
            href="/jobs"
            className="text-xs font-bold text-brand-deepNavy hover:text-brand-corpBlue flex items-center gap-1"
          >
            <span>All Global Filters</span>
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
              No positions matching this location at present.
            </p>
          </div>
        )}
      </section>
    </div>
  );
}
