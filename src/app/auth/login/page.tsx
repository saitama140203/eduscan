"use client";

import { useState } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { loginSchema, LoginFormInputs } from '@/lib/validations';
import { authAPI } from '@/lib/api-service';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input"; // Sẽ add sau
import {
  Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle,
} from "@/components/ui/card";
import { Label } from "@/components/ui/label"; // Sẽ add sau
// import { showError, showSuccess } from '@/lib/utils'; // Sẽ dùng sau
import Image from 'next/image';

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const callbackUrl = searchParams.get('callbackUrl') || '/dashboard';
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const form = useForm<LoginFormInputs>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const onSubmit = async (data: LoginFormInputs) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await authAPI.login(data);
      // Giả sử API trả về accessToken và refreshToken trong response.data.data
      if (response.data.success && response.data.data.accessToken) {
        if (typeof window !== "undefined") {
          localStorage.setItem('accessToken', response.data.data.accessToken);
          if (response.data.data.refreshToken) {
            localStorage.setItem('refreshToken', response.data.data.refreshToken);
          }
        }
        // showSuccess('Đăng nhập thành công!'); // Sẽ dùng sau
        alert('Đăng nhập thành công!');
        router.push(callbackUrl);
      } else {
        throw new Error(response.data.message || 'Thông tin đăng nhập không chính xác');
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || err.message || 'Đăng nhập thất bại. Vui lòng thử lại.';
      setError(errorMessage);
      // showError(errorMessage); // Sẽ dùng sau
      console.error("Login error:", err);
    }
    setIsLoading(false);
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/40 p-4">
      <Card className="w-full max-w-sm">
        <CardHeader className="text-center">
          <Image src="/logo.svg" alt="EduScan Logo" width={48} height={48} className="mx-auto mb-2" />
          <CardTitle className="text-2xl font-bold">Đăng nhập</CardTitle>
          <CardDescription>
            Nhập email và mật khẩu của bạn để tiếp tục.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input 
                id="email" 
                type="email" 
                placeholder="email@example.com" 
                {...form.register("email")} 
                disabled={isLoading}
              />
              {form.formState.errors.email && (
                <p className="text-xs text-red-500">{form.formState.errors.email.message}</p>
              )}
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="password">Mật khẩu</Label>
                <Link href="/auth/forgot-password" className="text-xs text-primary hover:underline">
                  Quên mật khẩu?
                </Link>
              </div>
              <Input 
                id="password" 
                type="password" 
                placeholder="••••••••" 
                {...form.register("password")} 
                disabled={isLoading}
              />
              {form.formState.errors.password && (
                <p className="text-xs text-red-500">{form.formState.errors.password.message}</p>
              )}
            </div>
            {error && (
              <p className="text-sm text-red-600 bg-red-100 p-3 rounded-md">{error}</p>
            )}
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? 'Đang xử lý...' : 'Đăng nhập'}
            </Button>
          </form>
        </CardContent>
        <CardFooter className="text-center text-sm">
          Chưa có tài khoản?{" "}
          <Link href="/auth/register" className="font-semibold text-primary hover:underline">
            Đăng ký ngay
          </Link>
        </CardFooter>
      </Card>
    </div>
  );
} 