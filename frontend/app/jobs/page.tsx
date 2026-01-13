"use client";

import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/dashboard-layout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
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
import { jobsAPI } from "@/lib/api";
import { PlayCircle, RefreshCw, Clock, CheckCircle2, XCircle } from "lucide-react";
import type { JobStatus, JobExecuteRequest } from "@/types";

export default function JobsPage() {
  const [jobs, setJobs] = useState<JobStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [jobRequest, setJobRequest] = useState<JobExecuteRequest>({
    target: "*",
    function: "test.ping",
    args: [],
  });

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const data = await jobsAPI.list();
      setJobs(data.jobs);
    } catch (error) {
      console.error("Failed to fetch jobs:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const handleExecuteJob = async () => {
    setExecuting(true);
    try {
      await jobsAPI.execute(jobRequest);
      setDialogOpen(false);
      // Refresh jobs list after execution
      await fetchJobs();
    } catch (error) {
      console.error("Failed to execute job:", error);
    } finally {
      setExecuting(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case "running":
        return <Clock className="h-4 w-4 text-blue-500 animate-pulse" />;
      case "failed":
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return <Badge className="bg-green-500">Completed</Badge>;
      case "running":
        return <Badge className="bg-blue-500">Running</Badge>;
      case "failed":
        return <Badge variant="destructive">Failed</Badge>;
      default:
        return <Badge variant="secondary">Unknown</Badge>;
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Jobs</h1>
            <p className="text-muted-foreground">
              Execute and monitor Salt jobs
            </p>
          </div>
          <div className="flex gap-2">
            <Button onClick={fetchJobs} disabled={loading} variant="outline">
              <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
              Refresh
            </Button>
            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
              <DialogTrigger asChild>
                <Button>
                  <PlayCircle className="mr-2 h-4 w-4" />
                  Execute Job
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Execute Salt Job</DialogTitle>
                  <DialogDescription>
                    Run a Salt function on target minions
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="target">Target</Label>
                    <Input
                      id="target"
                      placeholder="* (all minions)"
                      value={jobRequest.target}
                      onChange={(e) =>
                        setJobRequest({ ...jobRequest, target: e.target.value })
                      }
                    />
                    <p className="text-xs text-muted-foreground">
                      Use glob patterns like * or minion-*
                    </p>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="function">Function</Label>
                    <Input
                      id="function"
                      placeholder="test.ping"
                      value={jobRequest.function}
                      onChange={(e) =>
                        setJobRequest({ ...jobRequest, function: e.target.value })
                      }
                    />
                    <p className="text-xs text-muted-foreground">
                      Examples: test.ping, cmd.run, state.apply
                    </p>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="args">Arguments (optional)</Label>
                    <Input
                      id="args"
                      placeholder='["arg1", "arg2"]'
                      onChange={(e) => {
                        try {
                          const args = JSON.parse(e.target.value || "[]");
                          setJobRequest({ ...jobRequest, args });
                        } catch {
                          // Ignore parse errors
                        }
                      }}
                    />
                  </div>
                  <Button
                    className="w-full"
                    onClick={handleExecuteJob}
                    disabled={executing}
                  >
                    {executing ? (
                      <>
                        <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                        Executing...
                      </>
                    ) : (
                      <>
                        <PlayCircle className="mr-2 h-4 w-4" />
                        Execute
                      </>
                    )}
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        {loading && jobs.length === 0 ? (
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <div className="space-y-4">
            {jobs.map((job) => (
              <Card key={job.jid}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(job.status)}
                      <CardTitle className="text-lg">
                        {job.function}
                      </CardTitle>
                    </div>
                    {getStatusBadge(job.status)}
                  </div>
                  <CardDescription>
                    Job ID: {job.jid} • Started: {job.start_time || "Unknown"}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div className="text-sm">
                      <span className="text-muted-foreground">Targets: </span>
                      <span className="font-medium">
                        {job.minions.length} minion(s)
                      </span>
                      {job.minions.length > 0 && (
                        <span className="ml-2 text-muted-foreground">
                          ({job.minions.slice(0, 3).join(", ")}
                          {job.minions.length > 3 ? "..." : ""})
                        </span>
                      )}
                    </div>
                    <Button variant="outline" size="sm">
                      View Details
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {!loading && jobs.length === 0 && (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <PlayCircle className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No jobs found</h3>
              <p className="text-sm text-muted-foreground text-center">
                Execute your first Salt job to get started.
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
