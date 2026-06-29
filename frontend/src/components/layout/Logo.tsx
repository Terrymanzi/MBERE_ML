import { cn } from "@/lib/cn";

/**
 * Brand lockup. Uses the bundled logo asset with a typographic fallback so the
 * header still reads if the image is missing.
 */
export function Logo({
  className,
  showTagline = true,
}: {
  className?: string;
  showTagline?: boolean;
}) {
  return (
    <div className={cn("flex items-center gap-0", className)}>
      <img
        src="/images/MBERE ML logo.png"
        alt="Mbere ML logo"
        className="h-20 w-20 shrink-0 object-contain"
        onError={(e) => {
          (e.currentTarget as HTMLImageElement).style.display = "none";
        }}
      />
      <div className="leading-none">
        <span className="block text-lg font-thin tracking-widest text-[#0F6CBD]">
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
