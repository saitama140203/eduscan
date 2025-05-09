import React, { useEffect } from 'react';
import LoginForm from '@/components/auth/LoginForm';
import { useRouter } from 'next/router';
import Head from 'next/head';

const LoginPage = () => {
  const router = useRouter();

  const handleLoginSuccess = (data: any) => {
    localStorage.setItem('accessToken', data.access_token);
    localStorage.setItem('user', JSON.stringify({
      id: data.user_id,
      email: data.email,
      hoTen: data.hoTen,
      vaiTro: data.vaiTro,
    }));
    
    router.push('/'); 
  };

  // Thêm các hiệu ứng khi load trang
  useEffect(() => {
    document.body.classList.add('auth-page');
    return () => {
      document.body.classList.remove('auth-page');
    };
  }, []);

  return (
    <>
      <Head>
        <title>Đăng nhập - EduScan</title>
        <meta name="description" content="Hệ thống quản lý giáo dục EduScan - Đăng nhập" />
      </Head>

      <div className="min-h-screen flex items-center justify-center relative px-4 py-12">
        {/* Các hình khối background */}
        <div className="bg-shape w-96 h-96 top-0 right-0 bg-blue-500/30 pulse-animation"></div>
        <div className="bg-shape w-96 h-96 bottom-0 left-0 bg-indigo-500/20 pulse-animation" style={{animationDelay: '2s'}}></div>
        <div className="bg-shape w-64 h-64 top-1/4 left-10 bg-purple-500/20 pulse-animation" style={{animationDelay: '1s'}}></div>
        
        {/* Dải particle(tùy chọn) */}
        <div className="absolute inset-0 overflow-hidden opacity-20">
          <div className="absolute -inset-[10px] [mask-image:radial-gradient(ellipse_at_center,transparent_20%,#000)]">
            {[...Array(100)].map((_, index) => (
              <div
                key={index}
                className="absolute bg-white rounded-full"
                style={{
                  width: Math.random() * 3 + 1 + 'px',
                  height: Math.random() * 3 + 1 + 'px',
                  top: Math.random() * 100 + '%',
                  left: Math.random() * 100 + '%',
                  opacity: Math.random() * 0.5 + 0.3,
                  animation: `pulse ${Math.random() * 3 + 2}s ease-in-out infinite`
                }}
              ></div>
            ))}
          </div>
        </div>
        
        <div className="container max-w-5xl mx-auto relative z-10">
          <div className="grid md:grid-cols-5 gap-8 items-center">
            {/* Phần tiêu đề bên trái */}
            <div className="md:col-span-2 text-center md:text-left">
              <div className="mb-6 flex justify-center md:justify-start">
                <div className="w-16 h-16 flex items-center justify-center rounded-full bg-white/90 shadow-xl float-animation">
                  <span className="edu-logo text-4xl font-bold">ED</span>
                </div>
              </div>
              
              <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 leading-tight">
                Quản lý giáo dục <span className="login-title">thông minh</span>
              </h1>
              
              <p className="text-blue-100 text-lg mb-6 md:pr-8">
                Hệ thống quản lý toàn diện dành cho các đơn vị giáo dục hiện đại.
              </p>
              
              <div className="hidden md:block">
                <div className="flex items-center text-white/80 space-x-4 mb-2">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path>
                  </svg>
                  <span>Quản lý dữ liệu tập trung</span>
                </div>
                <div className="flex items-center text-white/80 space-x-4 mb-2">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path>
                  </svg>
                  <span>Báo cáo đa chiều trực quan</span>
                </div>
                <div className="flex items-center text-white/80 space-x-4">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path>
                  </svg>
                  <span>Bảo mật dữ liệu tiêu chuẩn</span>
                </div>
              </div>
            </div>
            
            {/* Form đăng nhập */}
            <div className="md:col-span-3 login-container py-8 px-6 sm:px-10">
              <div className="mb-8">
                <h2 className="text-2xl font-bold text-gray-800 mb-2">Đăng nhập hệ thống</h2>
                <p className="text-gray-600">Vui lòng đăng nhập để truy cập vào tài khoản của bạn</p>
              </div>
              
              <LoginForm onLoginSuccess={handleLoginSuccess} />
              
              <div className="mt-8 pt-6 border-t border-gray-200">
                <p className="text-center text-gray-600">
                  Bạn cần trợ giúp?{' '}
                  <a href="#" className="font-medium text-blue-600 hover:text-blue-700 transition-colors">
                    Liên hệ quản trị viên
                  </a>
                </p>
              </div>
            </div>
          </div>
          
          <footer className="mt-10 text-center text-white/70 text-sm">
            &copy; {new Date().getFullYear()} EduScan. Phát triển bởi Nhóm EDUSCAN.
          </footer>
        </div>
      </div>
    </>
  );
};

export default LoginPage; 