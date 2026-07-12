/** @type {import('tailwindcss').Config} */

// Single source of truth for the product's brand typeface. Change this one
// array to swap the font everywhere (Tailwind's default `sans` is aliased to
// it, and `font-brand` is available for explicit use).
const BRAND_FONT = [
  "Helvetica Neue",
  "Helvetica",
  "Arial",
  "ui-sans-serif",
  "system-ui",
  "sans-serif",
];

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Single accent colour for the whole product (clean research aesthetic).
        brand: {
          50: "#eff5ff",
          100: "#dbe8fe",
          200: "#bfd7fe",
          300: "#93bbfd",
          400: "#6094fa",
          500: "#3b76f6",
          600: "#2563eb",
          700: "#1d4ed8",
          800: "#1e40af",
          900: "#1e3a8a",
        },
        risk: {
          low: "#16a34a",
          medium: "#d97706",
          high: "#dc2626",
        },
      },
      fontFamily: {
        sans: BRAND_FONT,
        brand: BRAND_FONT,
      },
    },
  },
  plugins: [],
};
