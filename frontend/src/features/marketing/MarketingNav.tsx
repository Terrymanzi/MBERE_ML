import { Link } from "react-router-dom";
import { Logo } from "@/components/layout/Logo";
import { Button } from "@/components/ui/Button";

export function MarketingNav() {
  return (
    <header className="border-b border-slate-200">
      <div className="container-page flex h-20 items-center justify-between">
        <Link to="/" aria-label="MBERE ML home">
          <Logo />
        </Link>
        <nav className="flex items-center gap-2">
          <Link to="/login">
            <Button variant="primary" size="sm">
              Log in
            </Button>
          </Link>
        </nav>
      </div>
    </header>
  );
}
