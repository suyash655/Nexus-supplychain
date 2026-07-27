import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

/**
 * NEXUS Auth Middleware
 * Protects all app routes. Unauthenticated users are redirected to /login.
 * Public routes: /, /login
 *
 * Note: middleware runs on the Edge runtime and cannot access localStorage.
 * We check for the nexus_token cookie set by the client on login.
 */

const PUBLIC_PATHS = new Set(["/", "/login"]);

export default function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow public paths
  if (PUBLIC_PATHS.has(pathname)) {
    return NextResponse.next();
  }

  // Allow Next.js internals + static assets
  if (
    pathname.startsWith("/_next") ||
    pathname.startsWith("/api") ||
    pathname.includes(".") // static files like .ico, .png
  ) {
    return NextResponse.next();
  }

  // Check for auth token in cookie
  const token = request.cookies.get("nexus_token")?.value;

  if (!token) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all paths except:
     * - _next/static, _next/image (Next.js internals)
     * - favicon.ico
     */
    "/((?!_next/static|_next/image|favicon.ico).*)",
  ],
};
