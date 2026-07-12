import { cn } from "@/lib/cn";

type Size = "sm" | "md";

const IMAGE_SIZES: Record<Size, string> = {
  sm: "h-9 w-9",
  md: "h-20 w-20",
};

const WORDMARK_SIZES: Record<Size, string> = {
  sm: "text-sm",
  md: "text-lg",
};

/**
 * Brand lockup. Uses the bundled logo asset with a typographic fallback so the
 * header still reads if the image is missing.
 */
export function Logo({
  className,
  showTagline = true,
  size = "md",
}: {
  className?: string;
  showTagline?: boolean;
  size?: Size;
}) {
  return (
    <div className={cn("flex items-center gap-0", className)}>
      <img
        src="/images/MBERE ML logo.png"
        alt="Mbere ML logo"
        className={cn("shrink-0 object-contain", IMAGE_SIZES[size])}
        onError={(e) => {
          (e.currentTarget as HTMLImageElement).style.display = "none";
        }}
      />
      <div className="leading-none">
        <span
          className={cn(
            "block font-thin tracking-widest text-[#0F6CBD]",
            WORDMARK_SIZES[size],
          )}
        >
          MBERE ML
        </span>
        {showTagline && (
          <span className="mt-0.5 block text-[10px] font-thin uppercase tracking-wide text-slate-400">
            Predicting Road Risk Before It Happens
          </span>
        )}
      </div>
    </div>
  );
}
