import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { RiskBadge } from "./RiskBadge";

describe("RiskBadge", () => {
  it("renders the band label", () => {
    render(<RiskBadge band="High" />);
    expect(screen.getByText("High")).toBeInTheDocument();
  });

  it("applies a distinct style per band", () => {
    const { rerender } = render(<RiskBadge band="Low" />);
    expect(screen.getByText("Low").className).toContain("green");

    rerender(<RiskBadge band="Medium" />);
    expect(screen.getByText("Medium").className).toContain("amber");

    rerender(<RiskBadge band="High" />);
    expect(screen.getByText("High").className).toContain("red");
  });

  it("merges an extra className onto the default styling", () => {
    render(<RiskBadge band="Low" className="extra-class" />);
    expect(screen.getByText("Low").className).toContain("extra-class");
  });
});
