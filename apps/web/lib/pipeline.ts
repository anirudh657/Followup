/**
 * Typed client for the Python pipeline service.
 *
 * Boundary rule (docs/ARCHITECTURE.md §3): the browser never calls the pipeline
 * directly. UI code calls Next.js API routes, and those routes use this client
 * server-side, forwarding the user's Supabase JWT. Response/request types are
 * generated from the pipeline's OpenAPI schema into ./pipeline-types.ts
 * (TODO(phase-0): add the codegen script — `make types`).
 */

export interface PipelineClientOptions {
  /** Supabase access token of the acting user; forwarded as a Bearer token. */
  accessToken: string;
  /** Org the user is acting in; the pipeline re-verifies membership. */
  orgId: string;
}

export function pipelineFetch(
  path: string,
  init: RequestInit,
  opts: PipelineClientOptions,
): Promise<Response> {
  const base = process.env.PIPELINE_URL;
  if (!base) throw new Error("PIPELINE_URL is not set");
  return fetch(`${base}${path}`, {
    ...init,
    headers: {
      ...init.headers,
      Authorization: `Bearer ${opts.accessToken}`,
      "X-Org-Id": opts.orgId,
      "Content-Type": "application/json",
    },
    cache: "no-store",
  });
}
