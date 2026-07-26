import { afterEach } from "vitest";
import { cleanup } from "@testing-library/react";
import "@testing-library/jest-dom/vitest";

// RTL's automatic afterEach(cleanup) only self-registers when it detects a
// global `afterEach` (jest-style globals); this project keeps `globals: false`
// in vite.config.ts, so cleanup is wired explicitly here instead.
afterEach(() => {
  cleanup();
});
