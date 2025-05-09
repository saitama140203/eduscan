import React, { useState } from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { loginUser } from '@/services/authService';
import { User, Lock, AlertCircle, Loader2, Eye, EyeOff } from 'lucide-react';

// Icons (giả sử bạn sẽ dùng thư viện icon như heroicons hoặc react-icons)
// import { UserIcon, LockClosedIcon, ExclamationCircleIcon } from '@heroicons/react/24/solid';

const LoginSchema = z.object({
  username: z.string().min(1, { message: 'Tên đăng nhập không được để trống' }),
  password: z.string().min(6, { message: 'Mật khẩu phải có ít nhất 6 ký tự' }),
});

type LoginFormInputs = z.infer<typeof LoginSchema>;

interface LoginFormProps {
  onLoginSuccess: (data: any) => void;
}

const LoginForm: React.FC<LoginFormProps> = ({ onLoginSuccess }) => {
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormInputs>({
    resolver: zodResolver(LoginSchema),
  });

  const onSubmit: SubmitHandler<LoginFormInputs> = async (data) => {
    setErrorMessage(null);
    try {
      const response = await loginUser(data.username, data.password);
      onLoginSuccess(response);
    } catch (error: any) {
      if (error.response && error.response.data && error.response.data.detail) {
        setErrorMessage(error.response.data.detail);
      } else {
        setErrorMessage('Đã có lỗi xảy ra khi đăng nhập. Vui lòng thử lại.');
      }
      console.error('Login failed:', error);
    }
  };
  
  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {errorMessage && (
        <div className="p-4 bg-red-50 border-l-4 border-red-500 text-red-700 rounded-md flex items-start animate-fadeIn">
          <AlertCircle className="h-5 w-5 text-red-500 mr-3 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium">Không thể đăng nhập</p>
            <p className="text-sm mt-1">{errorMessage}</p>
          </div>
        </div>
      )}
      
      <div className="space-y-2">
        <label 
          htmlFor="username"
          className="block text-sm font-medium text-gray-700"
        >
          Tên đăng nhập
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <User className="h-5 w-5 text-blue-500/70" aria-hidden="true" />
          </div>
          <input
            id="username"
            type="text"
            autoComplete="username"
            {...register('username')}
            className={`block w-full pl-12 pr-4 py-3.5 border-0 rounded-lg text-gray-900
                        bg-gray-50/80 focus:ring-2 focus:ring-inset focus:ring-blue-500 shadow-sm
                        transition duration-200 ease-in-out
                        ${errors.username ? 'ring-2 ring-red-500' : 'hover:bg-gray-50'}`}
            placeholder="Nhập tên đăng nhập"
          />
        </div>
        {errors.username && (
          <p className="mt-1 text-sm text-red-600 flex items-center">
            <AlertCircle className="h-4 w-4 mr-1" />
            {errors.username.message}
          </p>
        )}
      </div>

      <div className="space-y-2">
        <label 
          htmlFor="password"
          className="block text-sm font-medium text-gray-700"
        >
          Mật khẩu
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <Lock className="h-5 w-5 text-blue-500/70" aria-hidden="true" />
          </div>
          <input
            id="password"
            type={showPassword ? "text" : "password"}
            autoComplete="current-password"
            {...register('password')}
            className={`block w-full pl-12 pr-12 py-3.5 border-0 rounded-lg text-gray-900
                        bg-gray-50/80 focus:ring-2 focus:ring-inset focus:ring-blue-500 shadow-sm
                        transition duration-200 ease-in-out
                        ${errors.password ? 'ring-2 ring-red-500' : 'hover:bg-gray-50'}`}
            placeholder="••••••••"
          />
          <button 
            type="button"
            className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-gray-500 hover:text-gray-600 transition-colors"
            onClick={togglePasswordVisibility}
          >
            {showPassword ? (
              <EyeOff className="h-5 w-5" />
            ) : (
              <Eye className="h-5 w-5" />
            )}
          </button>
        </div>
        {errors.password && (
          <p className="mt-1 text-sm text-red-600 flex items-center">
            <AlertCircle className="h-4 w-4 mr-1" />
            {errors.password.message}
          </p>
        )}
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <input 
            id="remember-me" 
            name="remember-me" 
            type="checkbox" 
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-600">
            Ghi nhớ đăng nhập
          </label>
        </div>
        <div className="text-sm">
          <a href="#" className="font-medium text-blue-600 hover:text-blue-700 transition-colors">
            Quên mật khẩu?
          </a>
        </div>
      </div>

      <div className="pt-2">
        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full relative flex justify-center items-center py-3.5 px-4 border-0 rounded-lg
                     text-base font-medium text-white 
                     bg-gradient-to-r from-blue-600 to-blue-700
                     hover:from-blue-700 hover:to-blue-800
                     focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 
                     disabled:opacity-70 disabled:cursor-not-allowed
                     shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40
                     transform-gpu hover:-translate-y-0.5 active:translate-y-0
                     transition-all duration-150 ease-in-out overflow-hidden"
        >
          <span className="relative z-10">
            {isSubmitting ? (
              <>
                <Loader2 className="animate-spin h-5 w-5 mr-2 inline" />
                Đang xử lý...
              </>
            ) : 'Đăng nhập'}
          </span>
          <span className="absolute inset-0 overflow-hidden rounded-lg">
            <span className="absolute -translate-x-full hover:translate-x-0 ease-in-out duration-500 inset-0 bg-gradient-to-r from-blue-700/80 via-indigo-600/80 to-blue-700/80"></span>
          </span>
        </button>
      </div>
    </form>
  );
};

export default LoginForm;
