import type { Config } from "tailwindcss";

/**
 * Tailwind config. shadcn/ui components (added via `npx shadcn@latest add ...`)
 * extend this with their design tokens; keep custom theme values here.
 */
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {},
  },
  plugins: [],
};

export default config;
