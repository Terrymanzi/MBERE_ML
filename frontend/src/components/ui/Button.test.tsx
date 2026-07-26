import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Button } from "./Button";

describe("Button", () => {
  it("renders its children and responds to clicks", async () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>Run prediction</Button>);

    const button = screen.getByRole("button", { name: "Run prediction" });
    await userEvent.click(button);

    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it("is disabled and shows a spinner while loading", () => {
    render(<Button loading>Submitting</Button>);
    const button = screen.getByRole("button");

    expect(button).toBeDisabled();
    expect(screen.getByRole("status", { name: "Loading" })).toBeInTheDocument();
  });

  it("does not fire onClick when disabled", async () => {
    const onClick = vi.fn();
    render(
      <Button disabled onClick={onClick}>
        Disabled
      </Button>,
    );

    await userEvent.click(screen.getByRole("button", { name: "Disabled" }));

    expect(onClick).not.toHaveBeenCalled();
  });
});
