/**
 * Server-side environment helpers.
 * Keeps process.env access in one place so API routes stay clean.
 */

export function getEnv(name: string, fallback = ""): string {
  const value = process.env[name];
  return value && value.trim().length > 0 ? value : fallback;
}

export function requireEnv(name: string): string {
  const value = getEnv(name);
  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value;
}

export function isProduction(): boolean {
  return process.env.NODE_ENV === "production";
}
