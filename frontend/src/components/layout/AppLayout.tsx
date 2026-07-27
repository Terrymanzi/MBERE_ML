import { useEffect, useState } from "react";
import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Logo } from "./Logo";
import { LogoutIcon, MenuIcon, XIcon } from "@/components/icons";
import { cn } from "@/lib/cn";
import { useAuth } from "@/features/auth/AuthContext";

/** Authenticated application shell: fixed sidebar + top bar + routed content. */
export function AppLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const { logout } = useAuth();

  // Prevent the page behind the full-screen menu from scrolling while it's open.
  useEffect(() => {
    document.body.style.overflow = mobileOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [mobileOpen]);

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Desktop sidebar */}
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 lg:block">
        <Sidebar />
      </aside>

      {/* Mobile top bar */}
      <div className="fixed inset-x-0 top-0 z-50 flex h-14 items-center justify-between border-b border-slate-200 bg-white px-4 lg:hidden">
        <Logo size="sm" showTagline={false} />
        <button
          type="button"
          aria-label={mobileOpen ? "Close menu" : "Open menu"}
          aria-expanded={mobileOpen}
          onClick={() => setMobileOpen((open) => !open)}
          className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 hover:text-slate-900"
        >
          {mobileOpen ? <XIcon className="h-6 w-6" /> : <MenuIcon className="h-6 w-6" />}
        </button>
      </div>

      {/* Full-screen mobile menu */}
      <div
        className={cn(
          "fixed inset-x-0 bottom-0 top-14 z-40 flex flex-col bg-white transition-opacity lg:hidden",
          mobileOpen ? "pointer-events-auto opacity-100" : "pointer-events-none opacity-0",
        )}
      >
        <div className="flex-1 overflow-y-auto">
          <Sidebar bordered={false} onNavigate={() => setMobileOpen(false)} />
        </div>
        <div className="border-t border-slate-200 px-4 py-4">
          <button
            type="button"
            onClick={() => {
              setMobileOpen(false);
              logout();
            }}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-mono font-semibold text-slate-600 hover:bg-slate-100 hover:text-slate-900"
          >
            <LogoutIcon className="h-5 w-5 shrink-0" />
            Log out
          </button>
        </div>
      </div>

      <div className="pt-14 lg:pl-64 lg:pt-0">
        <main className="px-4 py-8 lg:px-8">
          <div className="mx-auto w-full max-w-7xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
