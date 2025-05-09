"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { useState, useEffect, ReactNode } from "react";
import {
  Home, School, Users, BookOpen, FileText, BarChart3, Settings, Menu, X, LogOut
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button"; // Sẽ tạo/add sau
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"; // Sẽ tạo/add sau
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"; // Sẽ tạo/add sau
// import { logout } from "@/components/actions/logout-action"; // Sẽ tạo sau nếu cần server action

interface NavItem {
  href: string;
  label: string;
  icon: React.ElementType;
  activeMatcher?: (pathname: string) => boolean;
}

const mainNavItems: NavItem[] = [
  { href: "/dashboard", label: "Trang chủ", icon: Home },
  { href: "/dashboard/to-chuc", label: "Tổ chức", icon: School },
  { href: "/dashboard/nguoi-dung", label: "Người dùng", icon: Users }, // Chung cho Teacher, Staff
  { href: "/dashboard/hoc-sinh", label: "Học sinh", icon: Users }, 
  { href: "/dashboard/lop-hoc", label: "Lớp học", icon: BookOpen },
  { href: "/dashboard/bai-kiem-tra", label: "Bài kiểm tra", icon: FileText },
  { href: "/dashboard/phieu-tra-loi", label: "Phiếu trả lời", icon: FileText },
  { href: "/dashboard/thong-ke", label: "Thống kê", icon: BarChart3 },
];

const settingsNavItem: NavItem = {
  href: "/dashboard/cai-dat", label: "Cài đặt", icon: Settings
};

interface SidebarItemProps {
  item: NavItem;
  isMobile?: boolean;
}

const SidebarItem = ({ item, isMobile }: SidebarItemProps) => {
  const pathname = usePathname();
  const isActive = item.activeMatcher 
    ? item.activeMatcher(pathname)
    : pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));

  return (
    <Link
      href={item.href}
      className={cn(
        "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-all",
        isActive
          ? "bg-primary text-primary-foreground font-medium"
          : "text-muted-foreground hover:bg-muted hover:text-foreground",
        isMobile && "text-base py-3"
      )}
    >
      <item.icon className={cn("h-4 w-4", isMobile && "h-5 w-5")} />
      <span>{item.label}</span>
    </Link>
  );
};

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [pathname]);

  const handleLogout = async () => {
    // await logout(); // Nếu dùng server action
    // Hoặc gọi API logout
    if (typeof window !== "undefined") {
      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");
      window.location.href = "/auth/login"; // Redirect tới trang login
    }
    console.log("Đăng xuất");
  };

  return (
    <div className="grid min-h-screen w-full md:grid-cols-[220px_1fr] lg:grid-cols-[280px_1fr]">
      {/* Desktop Sidebar */}
      <aside className="hidden border-r bg-muted/40 md:block">
        <div className="flex h-full max-h-screen flex-col gap-2">
          <div className="flex h-14 items-center border-b px-4 lg:h-[60px] lg:px-6">
            <Link href="/dashboard" className="flex items-center gap-2 font-semibold">
              <Image src="/logo.svg" alt="EduScan" width={28} height={28} />
              <span className="">EduScan</span>
            </Link>
            {/* <Button variant="outline" size="icon" className="ml-auto h-8 w-8">
              <Bell className="h-4 w-4" />
              <span className="sr-only">Toggle notifications</span>
            </Button> */}
          </div>
          <nav className="flex-1 overflow-auto px-2 py-4 text-sm font-medium lg:px-4 space-y-1">
            {mainNavItems.map((item) => (
              <SidebarItem key={item.href} item={item} />
            ))}
          </nav>
          <div className="mt-auto p-2 lg:p-4 border-t">
            <SidebarItem item={settingsNavItem} />
          </div>
        </div>
      </aside>

      {/* Mobile Navbar & Menu */}
      <div className="flex flex-col">
        <header className="flex h-14 items-center gap-4 border-b bg-muted/40 px-4 lg:h-[60px] lg:px-6">
          <Button
            variant="outline"
            size="icon"
            className="shrink-0 md:hidden"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            <span className="sr-only">Mở menu</span>
          </Button>
          
          {/* Breadcrumb or Page Title - Can be dynamic based on page */}
          <div className="w-full flex-1">
             {/* <h1 className="text-lg font-semibold">Trang chủ</h1> */}
          </div>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="secondary" size="icon" className="rounded-full">
                <Avatar className="h-8 w-8">
                  <AvatarImage src="/avatars/01.png" alt="@username" />
                  <AvatarFallback>AD</AvatarFallback> {/* Lấy tên user */} 
                </Avatar>
                <span className="sr-only">Tài khoản</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>Tài khoản của tôi</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild>
                 <Link href="/dashboard/cai-dat/tai-khoan">Hồ sơ</Link>
              </DropdownMenuItem>
              <DropdownMenuItem>Hỗ trợ</DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleLogout} className="text-red-500 hover:!text-red-600 cursor-pointer">
                <LogOut className="mr-2 h-4 w-4" />
                Đăng xuất
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </header>

        {/* Mobile Menu Content */}
        {isMobileMenuOpen && (
          <div className="md:hidden fixed inset-0 top-14 z-40 bg-background/80 backdrop-blur-sm">
            <nav className="grid gap-2 p-4 text-lg font-medium bg-muted/95 h-full">
              {mainNavItems.map((item) => (
                <SidebarItem key={item.href} item={item} isMobile />
              ))}
              <div className="mt-auto border-t pt-2">
                <SidebarItem item={settingsNavItem} isMobile />
              </div>
            </nav>
          </div>
        )}

        {/* Main Content Area */}
        <main className="flex flex-1 flex-col gap-4 p-4 lg:gap-6 lg:p-6 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
} 