"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  ShieldCheck,
  CheckCircle2,
  Users,
  Award,
  Globe2,
  Cpu,
  Layers,
  Sparkles,
  ArrowRight,
  MapPin,
  Mail,
  Phone
} from "lucide-react";
import { API_BASE_URL } from "@/lib/api";

export default function AboutPage() {
  const [cmsData, setCmsData] = useState<any>(null);

  useEffect(() => {
    fetch(`${API_BASE_URL}/cms/content/about_page`)
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => setCmsData(data))
      .catch((err) => console.error(err));
  }, []);

  return (
    <div className="flex flex-col min-h-screen">
      {/* HERO SECTION */}
      <section className="bg-brand-deepNavy text-white py-20 lg:py-24 border-b border-brand-secondaryNavy">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-brand-secondaryNavy border border-brand-border/20 text-brand-yellow text-xs font-semibold mb-4">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Official Corporate Profile</span>
          </div>

          <h1 className="text-4xl sm:text-5xl font-black tracking-tight text-white">
            {cmsData?.title || "About VELVORAX"}
          </h1>

          <p className="mt-4 text-xl sm:text-2xl font-bold text-brand-yellow max-w-3xl mx-auto">
            {cmsData?.subtitle || "Smart Automation. Better Relationships. Faster Growth."}
          </p>

          <p className="mt-6 text-sm sm:text-base text-slate-300 max-w-2xl mx-auto leading-relaxed">
            {cmsData?.body ||
              "We built Velvorax's automation platform to help businesses grow faster through AI-powered CRM technology that increases productivity, improves customer relationships, and automates workflows."}
          </p>
        </div>
      </section>

      {/* FOUNDER & EXECUTIVE LEADERSHIP */}
      <section className="py-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        <div className="bg-white rounded-3xl border border-brand-border p-8 lg:p-12 shadow-sm flex flex-col md:flex-row items-center gap-8 lg:gap-12">
          {/* Executive Avatar / Profile Card */}
          <div className="w-44 h-44 sm:w-52 sm:h-52 rounded-2xl bg-brand-deepNavy border-4 border-brand-yellow flex flex-col items-center justify-center text-center p-4 flex-shrink-0 shadow-lg">
            <div className="w-20 h-20 rounded-full bg-brand-yellow/20 flex items-center justify-center text-brand-yellow mb-3 font-black text-2xl">
              VR
            </div>
            <span className="text-white font-extrabold text-base">Vagga Raraju</span>
            <span className="text-brand-yellow text-xs font-semibold mt-0.5">
              Founder & CEO
            </span>
          </div>

          <div className="flex-1 space-y-4">
            <div className="inline-block px-3 py-1 bg-brand-yellow/15 text-brand-deepNavy text-xs font-bold rounded-lg">
              Executive Leadership
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-brand-deepNavy">
              Vagga Raraju
            </h2>
            <p className="text-sm font-semibold text-brand-corpBlue">
              Founder & Chief Executive Officer — VELVORAX Software Solutions
            </p>
            <p className="text-sm text-brand-textSecondary leading-relaxed">
              Leading the company with a commitment to technology-driven growth, Vagga Raraju founded VELVORAX Software Solutions to empower enterprises with next-generation CRM architecture, workflow intelligence, and streamlined recruitment connectivity.
            </p>
            <div className="pt-2 flex flex-wrap gap-4 text-xs font-medium text-brand-deepNavy">
              <span className="flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-brand-success" />
                Enterprise Architecture
              </span>
              <span className="flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-brand-success" />
                AI CRM Workflow Automation
              </span>
              <span className="flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-brand-success" />
                Global Talent Sourcing
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* WHAT WE DO */}
      <section className="py-16 bg-white border-y border-brand-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <span className="text-xs font-bold uppercase tracking-widest text-brand-corpBlue">
              Core Capabilities
            </span>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-brand-deepNavy mt-1">
              What We Do
            </h2>
            <p className="text-sm text-brand-textSecondary mt-2">
              End-to-end digital solutions and engineering excellence driving scalable enterprise transformation.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                title: "Website Development",
                desc: "High-performance full-stack web applications, portals, and SaaS platforms built with Next.js, React, and TypeScript.",
              },
              {
                title: "Mobile App Development",
                desc: "Native and cross-platform mobile experiences delivering intuitive UI and robust offline capabilities.",
              },
              {
                title: "CRM & Sales Automation",
                desc: "Intelligent CRM technology that automates customer funnels, lead nurturing, and relationship operations.",
              },
              {
                title: "Digital Marketing",
                desc: "Performance marketing, SEO engineering, and data-driven client acquisition campaigns.",
              },
              {
                title: "Process Automation",
                desc: "Custom AI automation bots, API integrations, and robotic process automation eliminating manual workloads.",
              },
              {
                title: "Global Talent Acquisition",
                desc: "Dedicated recruitment infrastructure connecting candidates, recruiters, and companies across global locations.",
              },
            ].map((service, idx) => (
              <div
                key={idx}
                className="p-6 rounded-2xl border border-brand-border bg-brand-softBg hover:bg-white hover:border-brand-yellow/80 hover:shadow-md transition-all"
              >
                <div className="w-10 h-10 rounded-xl bg-white border border-brand-border flex items-center justify-center text-brand-deepNavy mb-4">
                  <Cpu className="w-5 h-5 text-brand-corpBlue" />
                </div>
                <h3 className="font-bold text-base text-brand-deepNavy mb-2">
                  {service.title}
                </h3>
                <p className="text-xs text-brand-textSecondary leading-relaxed">
                  {service.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* VISION & MISSION */}
      <section className="py-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="p-8 rounded-3xl bg-brand-deepNavy text-white border border-brand-secondaryNavy">
            <span className="text-xs font-bold uppercase tracking-widest text-brand-yellow">
              Our Vision
            </span>
            <h3 className="text-2xl font-bold mt-1 mb-4 text-white">
              Shaping the Future of Intelligent Business & Hiring
            </h3>
            <p className="text-sm text-slate-300 leading-relaxed">
              To be the premier global platform where intelligent automation meets human potential, empowering businesses to operate seamlessly and individuals to discover meaningful careers without friction.
            </p>
          </div>

          <div className="p-8 rounded-3xl bg-white border border-brand-border text-brand-deepNavy shadow-xs">
            <span className="text-xs font-bold uppercase tracking-widest text-brand-corpBlue">
              Our Mission
            </span>
            <h3 className="text-2xl font-bold mt-1 mb-4 text-brand-deepNavy">
              Empowering Growth Through Cutting-Edge Technology
            </h3>
            <p className="text-sm text-brand-textSecondary leading-relaxed">
              We engineer dependable, secure, and scalable automation tools and recruitment platforms that elevate productivity, nurture transparent hiring partnerships, and foster enduring economic prosperity.
            </p>
          </div>
        </div>
      </section>

      {/* WHY VELVORAX? (5 PILLARS) */}
      <section className="py-16 bg-white border-y border-brand-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <span className="text-xs font-bold uppercase tracking-widest text-brand-corpBlue">
              Key Value Drivers
            </span>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-brand-deepNavy mt-1">
              Why VELVORAX?
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {[
              {
                title: "One Account, Multiple Companies",
                desc: "Unified identity access across hiring partners and portfolio organizations.",
              },
              {
                title: "All-In-One Platform",
                desc: "Discovery, ATS, resume vault, and interview scheduling under a single roof.",
              },
              {
                title: "Automation-Driven Growth",
                desc: "Accelerating workflows through AI, eliminating tedious recruitment friction.",
              },
              {
                title: "Scalable Solutions",
                desc: "PostgreSQL relational architecture engineered for high concurrency.",
              },
              {
                title: "Dedicated Support",
                desc: "Reliable guidance and round-the-clock enterprise onboarding support.",
              },
            ].map((pillar, idx) => (
              <div
                key={idx}
                className="p-5 rounded-2xl border border-brand-border bg-brand-softBg text-center flex flex-col justify-between"
              >
                <div>
                  <div className="w-10 h-10 mx-auto rounded-full bg-brand-yellow/20 flex items-center justify-center text-brand-deepNavy mb-3">
                    <span className="font-extrabold text-sm">{idx + 1}</span>
                  </div>
                  <h4 className="font-bold text-xs text-brand-deepNavy mb-2">
                    {pillar.title}
                  </h4>
                  <p className="text-[11px] text-brand-textSecondary leading-relaxed">
                    {pillar.desc}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* OUR 5-STEP APPROACH */}
      <section className="py-16 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <span className="text-xs font-bold uppercase tracking-widest text-brand-corpBlue">
            Proven Methodology
          </span>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-brand-deepNavy mt-1">
            Our Approach
          </h2>
          <p className="text-sm text-brand-textSecondary mt-2">
            A disciplined five-stage delivery process turning client challenges into scalable business wins.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {[
            { stage: "01", name: "Understand", desc: "Thorough technical requirement analysis and strategic alignment." },
            { stage: "02", name: "Build", desc: "Robust engineering, clean database models, and modern UX architecture." },
            { stage: "03", name: "Automate", desc: "Infusing AI-powered automation to supercharge business throughput." },
            { stage: "04", name: "Convert", desc: "Optimizing conversion funnels, applicant pipelines, and engagement." },
            { stage: "05", name: "Scale", desc: "Continuous performance tuning, global replication, and enterprise reliability." },
          ].map((step, idx) => (
            <div
              key={idx}
              className="p-5 rounded-2xl bg-white border border-brand-border shadow-xs hover:border-brand-yellow transition-all"
            >
              <span className="text-xs font-extrabold text-brand-yellow bg-brand-deepNavy px-2.5 py-1 rounded-md">
                Step {step.stage}
              </span>
              <h4 className="font-bold text-sm text-brand-deepNavy mt-3 mb-1.5">
                {step.name}
              </h4>
              <p className="text-xs text-brand-textSecondary leading-relaxed">
                {step.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* CONTACT & HEADQUARTERS VERIFIED SECTION */}
      <section className="py-16 bg-brand-deepNavy text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-6 rounded-2xl bg-brand-secondaryNavy border border-brand-border/20">
              <MapPin className="w-6 h-6 text-brand-yellow mb-3" />
              <h4 className="font-bold text-sm text-white mb-1">Corporate Headquarters</h4>
              <p className="text-xs text-slate-300 leading-relaxed">
                Flat 303, Sri Mani Sai Arcade, &apos;X&apos; Road Miyapur, Hyderabad, Telangana - 500049.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-brand-secondaryNavy border border-brand-border/20">
              <Mail className="w-6 h-6 text-brand-yellow mb-3" />
              <h4 className="font-bold text-sm text-white mb-1">Direct Inquiries</h4>
              <p className="text-xs text-slate-300">
                <a href="mailto:raraju@velvorax.tech" className="hover:text-brand-yellow">
                  raraju@velvorax.tech
                </a>
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-brand-secondaryNavy border border-brand-border/20">
              <Phone className="w-6 h-6 text-brand-yellow mb-3" />
              <h4 className="font-bold text-sm text-white mb-1">Telephone Contact</h4>
              <p className="text-xs text-slate-300">
                <a href="tel:+919985201116" className="hover:text-brand-yellow">
                  +91 9985201116
                </a>
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
