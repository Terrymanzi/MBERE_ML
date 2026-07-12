import { Link } from "react-router-dom";
import { Logo } from "@/components/layout/Logo";
import { Button } from "@/components/ui/Button";

const LINKS = [
  { href: "#product", label: "Product" },
  { href: "#how-it-works", label: "Research" },
  { href: "#contact", label: "Contact" },
];

export function MarketingNav() {
  return (
    <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/95 backdrop-blur">
      <div className="container-page flex h-16 items-center justify-between">
        <Link to="/" aria-label="MBERE ML home">
          <Logo size="sm" showTagline={false} />
        </Link>
        <nav className="hidden items-center gap-8 text-sm text-slate-600 md:flex">
          {LINKS.map((link) => (
            <a key={link.href} href={link.href} className="hover:text-slate-900">
              {link.label}
            </a>
          ))}
        </nav>
        <Link to="/login">
          <Button variant="primary" size="sm">
            Log in
          </Button>
        </Link>
      </div>
    </header>
  );
}
