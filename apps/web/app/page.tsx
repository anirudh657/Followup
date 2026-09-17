/**
 * Landing / entry page.
 * TODO(phase-0): replace with auth-aware redirect (signed-in -> /app, else marketing page).
 */
export default function Home() {
  return (
    <main className="mx-auto flex max-w-2xl flex-col gap-4 px-6 py-24">
      <h1 className="text-3xl font-semibold tracking-tight">ActionFlow</h1>
      <p className="text-neutral-600">
        Meetings into executed work: action items, synced tasks, follow-ups, reports.
      </p>
      <p className="text-sm text-neutral-400">
        Scaffold build — see docs/ROADMAP.md for what lands when.
      </p>
    </main>
  );
}
