"use client";

import { useState, useEffect } from "react";
import { DashboardLayout } from "@/components/dashboard-layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Calendar, Plus, Trash2, RefreshCw } from "lucide-react";

interface ScheduleRequest {
  target: string;
  name: string;
  function: string;
  schedule: any;
}

export default function SchedulesPage() {
  const [schedules, setSchedules] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [target, setTarget] = useState("*");
  const [scheduleRequest, setScheduleRequest] = useState<ScheduleRequest>({
    target: "*",
    name: "",
    function: "",
    schedule: {},
  });

  const fetchSchedules = async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/v1/schedules/${target}`);
      const data = await response.json();
      setSchedules(data);
    } catch (error) {
      console.error("Failed to fetch schedules:", error);
    } finally {
      setLoading(false);
    }
  };

  const addSchedule = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/schedules", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...scheduleRequest,
          schedule: JSON.parse(scheduleRequest.schedule || "{}"),
        }),
      });
      const data = await response.json();
      setDialogOpen(false);
      fetchSchedules();
    } catch (error) {
      console.error("Failed to add schedule:", error);
    }
  };

  const deleteSchedule = async (name: string) => {
    try {
      await fetch(`http://localhost:8000/api/v1/schedules/${target}/${name}`, {
        method: "DELETE",
      });
      fetchSchedules();
    } catch (error) {
      console.error("Failed to delete schedule:", error);
    }
  };

  useEffect(() => {
    fetchSchedules();
  }, []);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Job Scheduling</h1>
            <p className="text-muted-foreground">
              Schedule recurring Salt jobs
            </p>
          </div>
          <div className="flex gap-2">
            <Button onClick={fetchSchedules} variant="outline" disabled={loading}>
              <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
              Refresh
            </Button>
            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Add Schedule
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create Scheduled Job</DialogTitle>
                  <DialogDescription>
                    Schedule a recurring Salt job
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="schedule-target">Target</Label>
                    <Input
                      id="schedule-target"
                      placeholder="* (all minions)"
                      value={scheduleRequest.target}
                      onChange={(e) =>
                        setScheduleRequest({ ...scheduleRequest, target: e.target.value })
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="schedule-name">Schedule Name</Label>
                    <Input
                      id="schedule-name"
                      placeholder="e.g., daily-backup"
                      value={scheduleRequest.name}
                      onChange={(e) =>
                        setScheduleRequest({ ...scheduleRequest, name: e.target.value })
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="schedule-function">Function</Label>
                    <Input
                      id="schedule-function"
                      placeholder="e.g., cmd.run"
                      value={scheduleRequest.function}
                      onChange={(e) =>
                        setScheduleRequest({ ...scheduleRequest, function: e.target.value })
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="schedule-config">Schedule Configuration (JSON)</Label>
                    <Input
                      id="schedule-config"
                      placeholder='{"seconds": 3600}'
                      value={scheduleRequest.schedule}
                      onChange={(e) =>
                        setScheduleRequest({ ...scheduleRequest, schedule: e.target.value })
                      }
                    />
                    <p className="text-xs text-muted-foreground">
                      Examples: {"{"}"seconds": 3600{"}"} or {"{"}"cron": "0 0 * * *"{"}"}
                    </p>
                  </div>
                  <Button
                    className="w-full"
                    onClick={addSchedule}
                    disabled={!scheduleRequest.name || !scheduleRequest.function}
                  >
                    <Calendar className="mr-2 h-4 w-4" />
                    Create Schedule
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Target Selection</CardTitle>
            <CardDescription>
              Select target minions to view their schedules
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="target">Target</Label>
              <Input
                id="target"
                placeholder="* (all minions)"
                value={target}
                onChange={(e) => setTarget(e.target.value)}
              />
            </div>
            <Button onClick={fetchSchedules} disabled={loading}>
              <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
              Load Schedules
            </Button>
          </CardContent>
        </Card>

        {schedules && schedules.data && (
          <Card>
            <CardHeader>
              <CardTitle>Active Schedules</CardTitle>
              <CardDescription>
                Scheduled jobs for {target}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="border rounded-lg">
                <pre className="p-4 overflow-auto max-h-96 text-sm">
                  {JSON.stringify(schedules.data, null, 2)}
                </pre>
              </div>
            </CardContent>
          </Card>
        )}

        {!schedules && !loading && (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Calendar className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No Schedules</h3>
              <p className="text-sm text-muted-foreground text-center">
                Create a new schedule or select a target to view existing schedules
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
