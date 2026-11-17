import React from "react";
import Link from "next/link";
import { MapPin, Briefcase, DollarSign, Clock, Building2, CheckCircle2 } from "lucide-react";

export interface JobCardProps {
  id: number;
  title: string;
  slug: string;
  companyName: string;
  companyLogo?: string | null;
  isVerified?: boolean;
  location: string;
  employmentType: string;
  workArrangement: string;
  experienceLevel: string;
  salary?: string | null;
  skills?: string[];
  postedDate: string;
  descriptionPreview?: string;
  onApplyClick?: () => void;
}

export default function JobCard({
  id,
  title,
  slug,
  companyName,
  companyLogo,
  isVerified,
  location,
  employmentType,
  workArrangement,
  experienceLevel,
  salary,
  skills = [],
  postedDate,
  descriptionPreview,
  onApplyClick,
}: JobCardProps) {
  const getArrangementBadge = () => {
    switch (workArrangement.toLowerCase()) {
      case "remote":
        return "bg-emerald-50 text-emerald-700 border-emerald-200";
      case "hybrid":
        return "bg-blue-50 text-blue-700 border-blue-200";
      default:
        return "bg-slate-100 text-slate-700 border-slate-200";
    }
  };

  return (
    <div className="group bg-white rounded-2xl border border-brand-border p-6 shadow-xs hover:shadow-md hover:border-brand-yellow/60 transition-all flex flex-col justify-between">
      <div>
        {/* Top Header: Company & Badges */}
        <div className="flex items-start justify-between gap-4 mb-4">
          <div className="flex items-center gap-3.5">
            <div className="w-12 h-12 rounded-xl bg-brand-softBg border border-brand-border flex items-center justify-center overflow-hidden flex-shrink-0">
              {companyLogo ? (
                <img
                  src={companyLogo}
                  alt={companyName}
                  className="w-full h-full object-cover"
                />
              ) : (
                <Building2 className="w-6 h-6 text-brand-corpBlue" />
              )}
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-sm font-semibold text-brand-deepNavy">
                  {companyName}
                </span>
                {isVerified && (
                  <span title="Verified Hiring Partner">
                    <CheckCircle2 className="w-4 h-4 text-brand-success" />
                  </span>
                )}
              </div>
              <div className="flex items-center gap-1.5 text-xs text-brand-textSecondary mt-0.5">
                <MapPin className="w-3.5 h-3.5 text-slate-400" />
                <span>{location}</span>
              </div>
            </div>
          </div>

          <span
            className={`px-3 py-1 rounded-full text-xs font-semibold border ${getArrangementBadge()}`}
          >
            {workArrangement}
          </span>
        </div>

        {/* Job Title */}
        <Link href={`/jobs/${slug}`}>
          <h3 className="text-lg font-bold text-brand-deepNavy group-hover:text-brand-corpBlue transition-colors mb-2 line-clamp-1">
            {title}
          </h3>
        </Link>

        {/* Description Preview */}
        {descriptionPreview && (
          <p className="text-xs text-brand-textSecondary line-clamp-2 mb-4 leading-relaxed">
            {descriptionPreview}
          </p>
        )}

        {/* Highlights: Experience, Type, Salary */}
        <div className="grid grid-cols-2 gap-2 text-xs text-brand-textSecondary mb-4">
          <div className="flex items-center gap-1.5">
            <Briefcase className="w-3.5 h-3.5 text-slate-400" />
            <span>
              {experienceLevel} • {employmentType}
            </span>
          </div>
          {salary && (
            <div className="flex items-center gap-1.5 text-brand-deepNavy font-semibold">
              <DollarSign className="w-3.5 h-3.5 text-brand-warning" />
              <span>{salary}</span>
            </div>
          )}
        </div>

        {/* Skills Pills */}
        {skills.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-5">
            {skills.slice(0, 4).map((skill, idx) => (
              <span
                key={idx}
                className="px-2.5 py-0.5 rounded-md text-[11px] font-medium bg-brand-softBg text-brand-textPrimary border border-brand-border/60"
              >
                {skill}
              </span>
            ))}
            {skills.length > 4 && (
              <span className="px-2 py-0.5 rounded-md text-[11px] font-medium text-brand-textSecondary">
                +{skills.length - 4} more
              </span>
            )}
          </div>
        )}
      </div>

      {/* Card Footer: Date & CTAs */}
      <div className="pt-4 border-t border-brand-border flex items-center justify-between">
        <div className="flex items-center gap-1 text-[11px] text-brand-textSecondary">
          <Clock className="w-3.5 h-3.5 text-slate-400" />
          <span>{postedDate}</span>
        </div>

        <div className="flex items-center gap-2">
          <Link
            href={`/jobs/${slug}`}
            className="px-3 py-1.5 text-xs font-semibold text-brand-deepNavy hover:bg-brand-softBg rounded-lg transition-colors"
          >
            Details
          </Link>
          <Link
            href={`/jobs/${slug}`}
            className="px-3.5 py-1.5 text-xs font-bold bg-brand-yellow hover:bg-brand-yellowHover text-brand-deepNavy rounded-lg shadow-2xs transition-all"
          >
            Apply Now
          </Link>
        </div>
      </div>
    </div>
  );
}
