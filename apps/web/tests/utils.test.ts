import { describe, expect, it } from "vitest";
import { cn, formatShortDate } from "../lib/utils";

describe("cn", () => {
  it("merges conflicting tailwind classes, last wins", () => {
    expect(cn("p-2", "p-4")).toBe("p-4");
  });
});

describe("formatShortDate", () => {
  it("formats an ISO date", () => {
    expect(formatShortDate("2026-03-05T00:00:00Z")).toMatch(/5 Mar/);
  });
  it("returns a dash for invalid input", () => {
    expect(formatShortDate("not-a-date")).toBe("—");
  });
});
