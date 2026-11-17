import React from "react";
import Link from "next/link";
import { Mail, Phone, MapPin, ExternalLink, ShieldCheck } from "lucide-react";
import Logo from "./Logo";

export default function Footer() {
  return (
    <footer className="bg-brand-deepNavy text-white pt-16 pb-12 border-t border-brand-secondaryNavy">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10 pb-12 border-b border-white/10">
          {/* Col 1: Left-aligned Logo & Company Mission */}
          <div className="lg:col-span-2 space-y-4">
            <Logo variant="light" />
            <p className="text-sm text-slate-300 max-w-sm leading-relaxed">
              We built Velvorax&apos;s automation platform to help businesses grow faster through AI-powered CRM technology that increases productivity, improves customer relationships, and automates workflows.
            </p>
            <div className="pt-2 flex items-center gap-2 text-xs text-brand-yellow font-medium">
              <ShieldCheck className="w-4 h-4 text-brand-yellow" />
              <span>Verified Global Hiring & Talent Platform</span>
            </div>
          </div>

          {/* Col 2: Product */}
          <div>
            <h4 className="text-sm font-bold uppercase tracking-wider text-brand-yellow mb-4">
              Explore Jobs
            </h4>
            <ul className="space-y-2.5 text-sm text-slate-300">
              <li>
                <Link href="/jobs" className="hover:text-white transition-colors">
                  Browse All Jobs
                </Link>
              </li>
              <li>
                <Link href="/it-jobs" className="hover:text-white transition-colors">
                  IT Opportunities
                </Link>
              </li>
              <li>
                <Link href="/non-it-jobs" className="hover:text-white transition-colors">
                  Non-IT Opportunities
                </Link>
              </li>
              <li>
                <Link href="/job-categories" className="hover:text-white transition-colors">
                  Job Categories
                </Link>
              </li>
              <li>
                <Link href="/global-jobs" className="hover:text-white transition-colors">
                  Global Opportunities
                </Link>
              </li>
            </ul>
          </div>

          {/* Col 3: Company & Portals */}
          <div>
            <h4 className="text-sm font-bold uppercase tracking-wider text-brand-yellow mb-4">
              Company & Portals
            </h4>
            <ul className="space-y-2.5 text-sm text-slate-300">
              <li>
                <Link href="/about" className="hover:text-white transition-colors">
                  About VELVORAX
                </Link>
              </li>
              <li>
                <Link href="/login" className="hover:text-white transition-colors">
                  Unified Login
                </Link>
              </li>
              <li>
                <Link href="/register" className="hover:text-white transition-colors">
                  Create Account
                </Link>
              </li>
              <li>
                <Link href="/candidate/dashboard" className="hover:text-white transition-colors">
                  Candidate Dashboard
                </Link>
              </li>
              <li>
                <Link href="/recruiter/dashboard" className="hover:text-white transition-colors">
                  Recruiter ATS
                </Link>
              </li>
            </ul>
          </div>

          {/* Col 4: Verified Contact Info (Section 20 requirement) */}
          <div>
            <h4 className="text-sm font-bold uppercase tracking-wider text-brand-yellow mb-4">
              Headquarters
            </h4>
            <ul className="space-y-3 text-sm text-slate-300">
              <li className="flex items-start gap-2.5">
                <MapPin className="w-5 h-5 text-brand-yellow flex-shrink-0 mt-0.5" />
                <span className="leading-snug">
                  Flat 303, Sri Mani Sai Arcade, &apos;X&apos; Road Miyapur, Hyderabad, Telangana - 500049.
                </span>
              </li>
              <li className="flex items-center gap-2.5">
                <Mail className="w-4 h-4 text-brand-yellow flex-shrink-0" />
                <a
                  href="mailto:raraju@velvorax.tech"
                  className="hover:text-white transition-colors"
                >
                  raraju@velvorax.tech
                </a>
              </li>
              <li className="flex items-center gap-2.5">
                <Phone className="w-4 h-4 text-brand-yellow flex-shrink-0" />
                <a
                  href="tel:+919985201116"
                  className="hover:text-white transition-colors"
                >
                  +91 9985201116
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 flex flex-col md:flex-row items-center justify-between text-xs text-slate-400 gap-4">
          <p>© {new Date().getFullYear()} VELVORAX Software Solutions. All rights reserved.</p>
          <div className="flex items-center gap-6">
            <span className="hover:text-slate-200 cursor-pointer">Privacy Policy</span>
            <span className="hover:text-slate-200 cursor-pointer">Terms & Conditions</span>
            <span className="hover:text-slate-200 cursor-pointer">Security Standards</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
