"use client";

import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/dashboard-layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { minionsAPI, jobsAPI, healthAPI } from "@/lib/api";
import { Server, CheckCircle, XCircle, Activity } from "lucide-react";

export default function Home() {
  const [stats, setStats] = useState({
    totalMinions: 0,
    activeMinions: 0,
    inactiveMinions: 0,
    totalJobs: 0,
    runningJobs: 0,
    apiStatus: "checking",
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [minionsData, jobsData, healthData] = await Promise.all([
          minionsAPI.list(),
          jobsAPI.list(),
          healthAPI.check(),
        ]);

        const activeMinions = minionsData.minions.filter(
          (m: any) => m.status === "up"
        ).length;
        const runningJobs = jobsData.jobs.filter(
          (j: any) => j.status === "running"
        ).length;

        setStats({
          totalMinions: minionsData.total,
          activeMinions,
          inactiveMinions: minionsData.total - activeMinions,
          totalJobs: jobsData.total,
          runningJobs,
          apiStatus: healthData.status,
        });
      } catch (error) {
        console.error("Failed to fetch data:", error);
        setStats((prev) => ({ ...prev, apiStatus: "error" }));
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Overview of your SaltStack infrastructure
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Minions</CardTitle>
              <Server className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {loading ? "..." : stats.totalMinions}
              </div>
              <p className="text-xs text-muted-foreground">
                {stats.activeMinions} active, {stats.inactiveMinions} inactive
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Minions</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {loading ? "..." : stats.activeMinions}
              </div>
              <p className="text-xs text-muted-foreground">
                Currently online
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Jobs</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {loading ? "..." : stats.totalJobs}
              </div>
              <p className="text-xs text-muted-foreground">
                {stats.runningJobs} currently running
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">API Status</CardTitle>
              {stats.apiStatus === "healthy" ? (
                <CheckCircle className="h-4 w-4 text-green-500" />
              ) : (
                <XCircle className="h-4 w-4 text-red-500" />
              )}
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold capitalize">
                {loading ? "..." : stats.apiStatus}
              </div>
              <p className="text-xs text-muted-foreground">
                Backend connection
              </p>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>Latest jobs and executions</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                No recent activity to display
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>System Health</CardTitle>
              <CardDescription>Infrastructure status overview</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Salt Master</span>
                  <CheckCircle className="h-4 w-4 text-green-500" />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Database</span>
                  <CheckCircle className="h-4 w-4 text-green-500" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
