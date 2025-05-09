import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';

interface UserData {
  id: number;
  email: string;
  hoTen: string;
  vaiTro: string;
}

const HomePage = () => {
  const router = useRouter();
  const [user, setUser] = useState<UserData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const accessToken = localStorage.getItem('accessToken');
    const storedUser = localStorage.getItem('user');

    if (accessToken && storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (error) {
        console.error("Failed to parse user data from localStorage:", error);
        // Xử lý lỗi, có thể xóa localStorage hỏng và đăng xuất
        localStorage.removeItem('accessToken');
        localStorage.removeItem('user');
        router.push('/auth/login');
      }
    } else {
      // Nếu không có token hoặc thông tin người dùng, chuyển về trang đăng nhập
      router.push('/auth/login');
    }
    setIsLoading(false);
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('user');
    // TODO: Gọi API backend để vô hiệu hóa token nếu có
    router.push('/auth/login');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p>Đang tải...</p>
      </div>
    );
  }

  if (!user) {
    // Điều này không nên xảy ra nếu logic useEffect đúng, nhưng để phòng ngừa
    // Hoặc có thể hiển thị một thông báo "Vui lòng đăng nhập" thay vì redirect ngay
    return null; // Hoặc một component fallback
  }

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4">
      <div className="bg-white shadow-md rounded-lg p-8 max-w-md w-full">
        <h1 className="text-3xl font-bold text-center text-indigo-600 mb-6">
          Chào mừng trở lại!
        </h1>
        <div className="space-y-4 mb-8">
          <p className="text-lg">
            <span className="font-semibold">Họ tên:</span> {user.hoTen}
          </p>
          <p className="text-lg">
            <span className="font-semibold">Email:</span> {user.email}
          </p>
          <p className="text-lg">
            <span className="font-semibold">Vai trò:</span> <span className="capitalize">{user.vaiTro}</span>
          </p>
        </div>
        <button
          onClick={handleLogout}
          className="w-full py-2 px-4 bg-red-500 hover:bg-red-600 text-white font-semibold rounded-md focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition duration-150 ease-in-out"
        >
          Đăng xuất
        </button>
      </div>
      <footer className="mt-8 text-center text-gray-600">
        <p>&copy; {new Date().getFullYear()} EduScan. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default HomePage; 