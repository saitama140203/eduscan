import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Danh sách các đường dẫn công khai không yêu cầu xác thực
const PUBLIC_PATHS = [
  "/auth/login",
  "/auth/register",
  "/auth/forgot-password",
  // Thêm các đường dẫn reset-password với token động
  // Ví dụ: /auth/reset-password/some-token
  // Do đó, chúng ta sẽ kiểm tra bằng startsWith
];

// Các đường dẫn API không cần kiểm tra token trong middleware này
// (vì chúng có thể có cơ chế xác thực riêng hoặc là public)
const API_AUTH_PREFIX = "/api/auth"; // Ví dụ: /api/auth/login, /api/auth/register

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Lấy token từ cookie (hoặc header nếu bạn dùng cách khác)
  const token = request.cookies.get("accessToken")?.value;

  const isPublicPath = PUBLIC_PATHS.includes(pathname) || pathname.startsWith("/auth/reset-password/");
  const isApiAuthRoute = pathname.startsWith(API_AUTH_PREFIX);
  const isApiRoute = pathname.startsWith("/api/"); // Tất cả các route /api/

  // Nếu là API route không phải auth, cho qua (backend tự xử lý auth)
  if (isApiRoute && !isApiAuthRoute) {
    return NextResponse.next();
  }
  
  // Nếu truy cập public path mà đã có token, redirect tới dashboard
  if (isPublicPath && token && !isApiAuthRoute) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  // Nếu truy cập private path mà không có token (và không phải API auth route)
  // redirect tới login
  if (!isPublicPath && !token && !isApiAuthRoute) {
    let callbackUrl = pathname;
    if (request.nextUrl.search) {
      callbackUrl += request.nextUrl.search;
    }
    const encodedCallbackUrl = encodeURIComponent(callbackUrl);
    return NextResponse.redirect(new URL(`/auth/login?callbackUrl=${encodedCallbackUrl}`, request.url));
  }

  return NextResponse.next();
}

// Cấu hình matcher để middleware chỉ chạy trên các đường dẫn cần thiết
export const config = {
  matcher: [
    // Áp dụng cho tất cả các route ngoại trừ các file static, _next, favicon.ico
    "/((?!_next/static|_next/image|favicon.ico|logo.svg|opengraph-image.png|twitter-image.png).*)",
    // Bao gồm cả các API route để kiểm tra (nếu cần, nhưng ở trên đã bỏ qua các /api/ không phải auth)
    // "/api/:path*", // Nếu bạn muốn middleware xử lý tất cả API routes
  ],
}; 