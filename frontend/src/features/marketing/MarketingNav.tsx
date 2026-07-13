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
    <header className="sticky top-5 mx-auto w-full max-w-5xl z-50 px-6">
      <div className="flex h-16 items-center justify-between rounded-full bg-white/90 px-6 py-2 shadow-md">
        {/* Logo Section */}
        <Link to="/" aria-label="MBERE ML home" className="flex items-center">
          <Logo size="sm" showTagline={false} />
        </Link>

        {/* Navigation Links */}
        <nav className="hidden items-center gap-8 text-sm font-medium  md:flex">
          {LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="transition-transform hover:text-[#0F6CBD] hover:scale-105 "
            >
              {link.label}
            </a>
          ))}
        </nav>

        {/* Call to Action Button */}
        <Link to="/login">
          <Button variant="primaryMarketing" size="sm">
            Log in
          </Button>
        </Link>
      </div>
    </header>
  );
}
