"use client";

import useSWR from "swr";
import { DashboardLayout } from "@/components/dashboard-layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
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
import { PlayCircle, RefreshCw, Terminal } from "lucide-react";
import { jobsAPI } from "@/lib/api";
import { useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";

function JobsContent() {
  const searchParams = useSearchParams();
  const target = searchParams.get("target") || "*";
  
  const [jobRequest, setJobRequest] = useState({
    target: target,
    function: "",
    args: [],
  });
  const [dialogOpen, setDialogOpen] = useState(false);
  const [executing, setExecuting] = useState(false);

  const { data, isLoading, isValidating, mutate } = useSWR(
    "/api/v1/jobs",
    () => jobsAPI.list()
  );

  const jobs = data?.data || [];
  const isRefreshing = isLoading || isValidating;

  const handleExecuteJob = async () => {
    setExecuting(true);
    try {
      await jobsAPI.execute(jobRequest);
      setDialogOpen(false);
      mutate();
    } catch (error) {
      console.error("Failed to execute job:", error);
    } finally {
      setExecuting(false);
    }
  };

  const getStatusIcon = (status: string) => {
    return <Terminal className="h-5 w-5 text-blue-500" />;
  };

  const getStatusBadge = (status: string) => {
    return <Badge>Completed</Badge>;
  };

  return (
    <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Jobs</h1>
            <p className="text-muted-foreground">
              Execute and monitor Salt jobs
            </p>
          </div>
          <div className="flex gap-2">
            <Button onClick={() => mutate()} disabled={isRefreshing} variant="outline">
               <RefreshCw className={`mr-2 h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`} />
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

        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <div className="space-y-4">
            {jobs.map((job: any) => (
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

        {!isLoading && jobs.length === 0 && (
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
  );
}

export default function JobsPage() {
    return (
        <DashboardLayout>
            <Suspense fallback={<div>Loading...</div>}>
                <JobsContent />
            </Suspense>
        </DashboardLayout>
    );
}

