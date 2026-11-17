"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Search, Briefcase, Code, ArrowRight, Layers } from "lucide-react";
import { API_BASE_URL } from "@/lib/api";

export default function JobCategoriesDirectoryPage() {
  const [categories, setCategories] = useState<any[]>([]);
  const [search, setSearch] = useState("");
  const [activeTab, setActiveTab] = useState<"ALL" | "IT" | "NON_IT">("ALL");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE_URL}/categories`)
      .then((res) => (res.ok ? res.json() : []))
      .then((data) => setCategories(data || []))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const filteredCategories = categories.filter((cat) => {
    const matchesTab =
      activeTab === "ALL" ? true : cat.category_type === activeTab;
    const matchesSearch =
      cat.name.toLowerCase().includes(search.toLowerCase()) ||
      (cat.description && cat.description.toLowerCase().includes(search.toLowerCase()));
    return matchesTab && matchesSearch;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center max-w-2xl mx-auto mb-10">
        <span className="text-xs font-bold uppercase tracking-widest text-brand-corpBlue">
          Taxonomy Catalog
        </span>
        <h1 className="text-3xl font-extrabold text-brand-deepNavy mt-1">
          Explore All Job Categories
        </h1>
        <p className="text-sm text-brand-textSecondary mt-2">
          Discover specialized roles organized across Information Technology and Corporate Non-IT divisions.
        </p>

        {/* Search */}
        <div className="mt-6 relative max-w-md mx-auto">
          <Search className="w-4 h-4 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search categories or specializations..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-11 pr-4 py-3 rounded-2xl border border-brand-border bg-white text-xs font-medium focus:outline-brand-yellow shadow-2xs"
          />
        </div>

        {/* Tab Filters */}
        <div className="mt-6 inline-flex p-1 bg-white border border-brand-border rounded-xl shadow-2xs">
          {(["ALL", "IT", "NON_IT"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-5 py-2 text-xs font-bold rounded-lg transition-all ${
                activeTab === tab
                  ? "bg-brand-deepNavy text-brand-yellow shadow-xs"
                  : "text-brand-textSecondary hover:text-brand-deepNavy"
              }`}
            >
              {tab === "ALL" ? "All Categories" : tab === "IT" ? "IT & Tech" : "Non-IT & Corporate"}
            </button>
          ))}
        </div>
      </div>

      {/* Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="h-44 bg-white rounded-2xl border border-brand-border animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCategories.map((cat) => (
            <div
              key={cat.id}
              className="bg-white rounded-2xl border border-brand-border p-6 shadow-xs hover:shadow-md hover:border-brand-yellow transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-10 h-10 rounded-xl bg-brand-softBg flex items-center justify-center text-brand-deepNavy">
                    {cat.category_type === "IT" ? (
                      <Code className="w-5 h-5 text-brand-corpBlue" />
                    ) : (
                      <Briefcase className="w-5 h-5 text-brand-warning" />
                    )}
                  </div>
                  <span
                    className={`text-[10px] uppercase font-bold tracking-wider px-2.5 py-0.5 rounded-full border ${
                      cat.category_type === "IT"
                        ? "bg-blue-50 text-blue-700 border-blue-200"
                        : "bg-amber-50 text-amber-700 border-amber-200"
                    }`}
                  >
                    {cat.category_type === "IT" ? "IT" : "Non-IT"}
                  </span>
                </div>

                <h3 className="font-bold text-base text-brand-deepNavy mb-1">
                  {cat.name}
                </h3>
                <p className="text-xs text-brand-textSecondary line-clamp-2 leading-relaxed">
                  {cat.description || "Career opportunities and professional specializations."}
                </p>

                {/* Subcategories list preview */}
                {cat.subcategories && cat.subcategories.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-1">
                    {cat.subcategories.map((sub: any) => (
                      <span
                        key={sub.id}
                        className="px-2 py-0.5 rounded bg-brand-softBg text-[10px] font-semibold text-brand-textPrimary"
                      >
                        {sub.name}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              <div className="mt-5 pt-4 border-t border-brand-border flex items-center justify-between">
                <span className="text-xs font-bold text-brand-deepNavy">
                  {cat.active_jobs_count} Positions Open
                </span>
                <Link
                  href={`/job-categories/${cat.slug}`}
                  className="inline-flex items-center gap-1 text-xs font-bold text-brand-corpBlue hover:underline"
                >
                  <span>Explore Subcategories</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
