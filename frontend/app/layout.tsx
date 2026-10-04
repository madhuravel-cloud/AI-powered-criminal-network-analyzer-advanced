import type { Metadata } from "next";
import Link from "next/link";
import {
  LayoutDashboard,
  FolderKanban,
  FileSearch,
  Network,
  BrainCircuit,
} from "lucide-react";

import "./globals.css";

export const metadata: Metadata = {
  title: "Criminal Network Analyzer",
  description: "Investigation intelligence and evidence analysis platform",
};

function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 z-50 flex h-screen w-64 flex-col border-r border-white/10 bg-[#080b12]">

      {/* Logo / Header */}
      <div className="flex h-20 items-center border-b border-white/10 px-6">
        <div>
          <h1 className="text-lg font-bold tracking-wide text-white">
            CRIMINAL
          </h1>

          <p className="text-xs font-medium tracking-[0.25em] text-cyan-400">
            NETWORK ANALYZER
          </p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-2 px-4 py-6">

        <NavItem
          href="/"
          icon={<LayoutDashboard size={18} />}
          label="Dashboard"
        />

        <NavItem
          href="/cases"
          icon={<FolderKanban size={18} />}
          label="Cases"
        />

        <NavItem
          href="/evidence"
          icon={<FileSearch size={18} />}
          label="Evidence"
        />

        <NavItem
          href="/network"
          icon={<Network size={18} />}
          label="Network"
        />

        <NavItem
          href="/analysis"
          icon={<BrainCircuit size={18} />}
          label="Analysis"
        />

      </nav>

      {/* System Status */}
      <div className="border-t border-white/10 p-4">

        <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">

          <div className="mb-3 flex items-center gap-2">
            <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />

            <span className="text-xs font-semibold uppercase tracking-wider text-white/70">
              System Status
            </span>
          </div>

          <div className="space-y-2 text-xs text-white/40">

            <div className="flex items-center justify-between">
              <span>API</span>
              <span className="text-emerald-400">Online</span>
            </div>

            <div className="flex items-center justify-between">
              <span>PostgreSQL</span>
              <span className="text-emerald-400">Online</span>
            </div>

            <div className="flex items-center justify-between">
              <span>Neo4j</span>
              <span className="text-emerald-400">Online</span>
            </div>

          </div>

        </div>

      </div>
    </aside>
  );
}

function NavItem({
  href,
  icon,
  label,
}: {
  href: string;
  icon: React.ReactNode;
  label: string;
}) {
  return (
    <Link
      href={href}
      className="group flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-white/50 transition-all duration-200 hover:bg-white/[0.06] hover:text-white"
    >
      <span className="text-white/40 transition-colors group-hover:text-cyan-400">
        {icon}
      </span>

      <span>{label}</span>
    </Link>
  );
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#05070b] text-white antialiased">
        <Sidebar />

        <main className="min-h-screen pl-64">
          {children}
        </main>
      </body>
    </html>
  );
}