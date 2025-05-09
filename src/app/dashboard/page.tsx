"use client";

import { useState, useEffect, ReactNode } from "react";
import Link from "next/link";
import {
  School, Users, BookOpen, FileText, BarChart3, CalendarRange, Activity
} from "lucide-react";
// import { organizationAPI, teacherAPI, classAPI, examAPI } from "@/lib/api-service"; // Bỏ comment khi API sẵn sàng
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
// import { showError } from "@/lib/utils"; // Bỏ comment khi utils sẵn sàng

interface StatCardProps {
  title: string;
  value: number | string;
  description: string;
  icon: ReactNode;
  href: string;
  loading: boolean;
}

const StatCard = ({ title, value, description, icon, href, loading }: StatCardProps) => (
  <Card>
    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
      <div className="text-muted-foreground">{icon}</div>
    </CardHeader>
    <CardContent>
      <div className="text-2xl font-bold">
        {loading ? (
          <div className="h-8 w-20 animate-pulse rounded-md bg-muted" />
        ) : (
          value
        )}
      </div>
      <p className="text-xs text-muted-foreground mt-1">{description}</p>
      <Button asChild variant="link" className="p-0 h-auto mt-2 text-xs font-medium text-primary">
        <Link href={href}>
          Xem chi tiết &rarr;
        </Link>
      </Button>
    </CardContent>
  </Card>
);

interface ActivityItem {
  id: string;
  actor: string;
  action: string;
  target?: string;
  timestamp: Date;
}

const RecentActivityItem = ({ activity }: { activity: ActivityItem }) => (
  <div className="flex items-start gap-3">
    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-primary">
      <Activity className="h-4 w-4" />
    </div>
    <div className="text-sm">
      <p className="font-medium">
        {activity.actor} <span className="text-muted-foreground">{activity.action}</span> {activity.target && <span className="font-semibold">{activity.target}</span>}
      </p>
      <p className="text-xs text-muted-foreground">
        {/* {formatDate(activity.timestamp, { hour: '2-digit', minute: '2-digit' })} */}
        {new Date(activity.timestamp).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit'})} - {new Date(activity.timestamp).toLocaleDateString('vi-VN')}
      </p>
    </div>
  </div>
);

export default function DashboardPage() {
  const [stats, setStats] = useState({
    organizations: 0,
    teachers: 0,
    students: 0,
    classes: 0,
    exams: 0,
    answerSheets: 0,
  });
  const [recentActivities, setRecentActivities] = useState<ActivityItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        // Dữ liệu mẫu - Thay thế bằng API calls thực tế sau này
        // const [orgRes, teacherRes, classRes, examRes] = await Promise.all([
        //   organizationAPI.getAll(), // Cần cập nhật API để lấy tổng số
        //   teacherAPI.getAll(currentOrgId), // Tương tự
        //   classAPI.getAll(currentOrgId),
        //   examAPI.getAll(currentOrgId),
        //   // Thêm API lấy activities
        // ]);

        // Dữ liệu mẫu
        setTimeout(() => {
          setStats({
            organizations: 5,
            teachers: 48,
            students: 542,
            classes: 24,
            exams: 36,
            answerSheets: 1284,
          });
          setRecentActivities([
            { id: '1', actor: 'Admin User', action: 'đã tạo tổ chức mới', target: 'THPT Chuyên KHTN', timestamp: new Date() },
            { id: '2', actor: 'Giáo viên A', action: 'đã thêm bài kiểm tra', target: 'Toán lớp 10 - HK1', timestamp: new Date(Date.now() - 3600000) }, // 1 hour ago
            { id: '3', actor: 'Học sinh B', action: 'đã nộp phiếu trả lời cho bài', target: 'Lý lớp 11 - GK2', timestamp: new Date(Date.now() - 7200000) }, // 2 hours ago
          ]);
          setLoading(false);
        }, 1000);

      } catch (error) {
        console.error("Lỗi khi tải dữ liệu dashboard:", error);
        // showError("Không thể tải dữ liệu thống kê"); // Bỏ comment khi utils sẵn sàng
        alert("Không thể tải dữ liệu thống kê");
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold md:text-3xl tracking-tight">Trang chủ</h1>
        <p className="text-muted-foreground">
          Tổng quan về hệ thống EduScan của bạn.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3">
        <StatCard title="Tổ chức" value={stats.organizations} description="Tổng số tổ chức" icon={<School className="h-5 w-5" />} href="/dashboard/to-chuc" loading={loading} />
        <StatCard title="Giáo viên" value={stats.teachers} description="Tổng số giáo viên" icon={<Users className="h-5 w-5" />} href="/dashboard/nguoi-dung" loading={loading} />
        <StatCard title="Học sinh" value={stats.students} description="Tổng số học sinh" icon={<Users className="h-5 w-5" />} href="/dashboard/hoc-sinh" loading={loading} />
        <StatCard title="Lớp học" value={stats.classes} description="Số lớp học đang hoạt động" icon={<BookOpen className="h-5 w-5" />} href="/dashboard/lop-hoc" loading={loading} />
        <StatCard title="Bài kiểm tra" value={stats.exams} description="Tổng số bài kiểm tra" icon={<FileText className="h-5 w-5" />} href="/dashboard/bai-kiem-tra" loading={loading} />
        <StatCard title="Phiếu trả lời" value={stats.answerSheets} description="Phiếu trả lời đã xử lý" icon={<FileText className="h-5 w-5" />} href="/dashboard/phieu-tra-loi" loading={loading} />
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7">
        <Card className="lg:col-span-4">
          <CardHeader>
            <CardTitle>Hoạt động gần đây</CardTitle>
            <CardDescription>Các hoạt động mới nhất trong hệ thống.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {loading ? (
              Array(3).fill(0).map((_, i) => (
                <div key={i} className="flex items-start gap-3 animate-pulse">
                  <div className="h-8 w-8 rounded-full bg-muted" />
                  <div className="flex-1 space-y-1">
                    <div className="h-4 w-3/4 rounded bg-muted" />
                    <div className="h-3 w-1/2 rounded bg-muted" />
                  </div>
                </div>
              ))
            ) : recentActivities.length > 0 ? (
              recentActivities.map(activity => <RecentActivityItem key={activity.id} activity={activity} />)
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <Activity className="h-10 w-10 mx-auto mb-2 text-muted-foreground/50" />
                <p>Chưa có hoạt động nào.</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle>Lịch trình & Sự kiện</CardTitle>
            <CardDescription>Các sự kiện và lịch kiểm tra sắp tới.</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              Array(2).fill(0).map((_, i) => (
                <div key={i} className="flex items-start gap-3 animate-pulse mb-4">
                  <div className="h-10 w-10 rounded-md bg-muted" />
                  <div className="flex-1 space-y-1">
                    <div className="h-4 w-3/4 rounded bg-muted" />
                    <div className="h-3 w-1/2 rounded bg-muted" />
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-muted-foreground flex flex-col items-center">
                <CalendarRange className="h-10 w-10 mb-2 text-muted-foreground/50" />
                <p>Chưa có sự kiện nào được lên lịch.</p>
                <Button asChild variant="outline" size="sm" className="mt-3">
                  <Link href="/dashboard/lich">Xem lịch</Link>
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 