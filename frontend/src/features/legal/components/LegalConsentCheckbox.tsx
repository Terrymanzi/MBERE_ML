import { useId } from "react";
import { LegalLink } from "./LegalLink";
import { cn } from "@/lib/cn";

export interface LegalConsentCheckboxProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  error?: string;
}

/** Required signup consent checkbox — "I have read and agree to the Terms of Use, including the Privacy Policy of MBERE ML." */
export function LegalConsentCheckbox({
  checked,
  onChange,
  error,
}: LegalConsentCheckboxProps) {
  const inputId = useId();
  const errorId = useId();

  return (
    <div>
      <div className="flex items-start gap-3">
        <input
          id={inputId}
          type="checkbox"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
          required
          aria-invalid={error ? true : undefined}
          aria-describedby={error ? errorId : undefined}
          className={cn(
            "mt-0.5 h-4 w-4 shrink-0 cursor-pointer rounded-sm border-slate-300 text-[#0F6CBD]",
            "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-600",
            error && "border-red-400",
          )}
        />
        <label
          htmlFor={inputId}
          className="cursor-pointer text-sm font-thin text-slate-600"
        >
          I have read and agree to the{" "}
          <LegalLink to="/legal/terms" newTab>
            Terms of Use
          </LegalLink>
          , including the{" "}
          <LegalLink to="/legal/privacy" newTab>
            Privacy Policy
          </LegalLink>{" "}
          of MBERE ML.
        </label>
      </div>
      {error && (
        <p id={errorId} role="alert" className="mt-1.5 pl-7 text-sm text-red-600">
          {error}
        </p>
      )}
    </div>
  );
}
