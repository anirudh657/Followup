/**
 * Supabase browser client factory.
 *
 * The browser client uses the anon key; Postgres RLS is the security boundary
 * (see docs/ARCHITECTURE.md §5). Server components / route handlers should use
 * @supabase/ssr cookie-based clients instead — added in phase 0 auth work.
 */
import { createClient, type SupabaseClient } from "@supabase/supabase-js";

let client: SupabaseClient | null = null;

export function getSupabaseBrowserClient(): SupabaseClient {
  if (!client) {
    const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
    if (!url || !anonKey) {
      throw new Error(
        "NEXT_PUBLIC_SUPABASE_URL / NEXT_PUBLIC_SUPABASE_ANON_KEY are not set",
      );
    }
    client = createClient(url, anonKey);
  }
  return client;
}
