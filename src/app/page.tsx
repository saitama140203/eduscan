"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    // Kiểm tra token ở đây nếu cần, hoặc dựa vào middleware
    // Middleware đã xử lý việc redirect nên trang này có thể chỉ là placeholder
    // hoặc redirect tới một trang giới thiệu nếu chưa login.
    // Hiện tại, giả sử middleware đã điều hướng đúng.
    // Nếu người dùng vào thẳng trang này mà chưa login, middleware sẽ đưa họ tới /auth/login.
    // Nếu đã login, middleware sẽ cho phép vào, và chúng ta có thể redirect tới /dashboard.
    
    // Tuy nhiên, tốt hơn là middleware nên redirect thẳng đến /dashboard nếu đã login và truy cập /
    // Do đó, trang này có thể không cần thiết nếu middleware xử lý tốt.
    // Hoặc nó có thể là một landing page thực sự.

    // Để đơn giản, nếu vào được đây (đã qua middleware), điều hướng tới dashboard.
    // Điều này cũng đảm bảo nếu người dùng đã login và gõ URL gốc thì vào dashboard.
    router.replace('/dashboard');
  }, [router]);

  // Có thể hiển thị một spinner hoặc loading message trong khi redirect
  return (
    <div className="flex items-center justify-center min-h-screen">
      <p>Đang chuyển hướng...</p>
      {/* Hoặc một component Spinner đẹp hơn */}
    </div>
  );
} 