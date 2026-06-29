import { NavLink } from "react-router-dom";
import type { ComponentType, SVGProps } from "react";
import { Logo } from "./Logo";
import {
  AnalyticsIcon,
  DashboardIcon,
  DriversIcon,
  ModelsIcon,
  PredictIcon,
  SettingsIcon,
  UserIcon,
} from "@/components/icons";
import { cn } from "@/lib/cn";

interface NavItem {
  to: string;
  label: string;
  icon: ComponentType<SVGProps<SVGSVGElement>>;
  end?: boolean;
}

const TOOLS: NavItem[] = [
  { to: "/app", label: "Dashboard", icon: DashboardIcon, end: true },
  { to: "/app/drivers", label: "Drivers", icon: DriversIcon },
  { to: "/app/predict", label: "Prediction", icon: PredictIcon },
  { to: "/app/analytics", label: "Analytics", icon: AnalyticsIcon },
  { to: "/app/models", label: "Models", icon: ModelsIcon },
];

const ACTIONS: NavItem[] = [
  { to: "/app/settings", label: "Settings", icon: SettingsIcon },
  { to: "/app/profile", label: "Profile", icon: UserIcon },
];

function Item({
  item,
  onNavigate,
}: {
  item: NavItem;
  onNavigate?: () => void;
}) {
  const Icon = item.icon;
  return (
    <NavLink
      to={item.to}
      end={item.end}
      onClick={onNavigate}
      className={({ isActive }) =>
        cn(
          "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-mono transition-colors",
          isActive
            ? "bg-[#0F6CBD] text-white"
            : "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
        )
      }
    >
      <Icon className="h-5 w-5 shrink-0" />
      {item.label}
    </NavLink>
  );
}

export function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <div className="flex h-full flex-col gap-6 border-r border-slate-200 bg-white px-4 py-6">
      <div className="px-2">
        <Logo />
      </div>

      <nav className="flex flex-1 flex-col gap-1">
        <p className="px-3 pb-1 text-xs font-thin uppercase tracking-wide text-slate-400">
          Tools
        </p>
        {TOOLS.map((item) => (
          <Item key={item.to} item={item} onNavigate={onNavigate} />
        ))}

        <p className="px-3 pb-1 pt-5 text-xs font-thin uppercase tracking-wide text-slate-400">
          Account
        </p>
        {ACTIONS.map((item) => (
          <Item key={item.to} item={item} onNavigate={onNavigate} />
        ))}
      </nav>
    </div>
  );
}
