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
import { Terminal, PlayCircle, CheckCircle2, AlertCircle } from "lucide-react";

interface Runner {
  name: string;
  description: string;
  category: string;
}

export default function RunnersPage() {
  const [runners, setRunners] = useState<Runner[]>([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [selectedRunner, setSelectedRunner] = useState<string>("");
  const [args, setArgs] = useState<string>("");
  const [results, setResults] = useState<any>(null);

  const fetchCommonRunners = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/runners/common");
      const data = await response.json();
      setRunners(data.runners);
    } catch (error) {
      console.error("Failed to fetch runners:", error);
    }
  };

  const executeRunner = async () => {
    setExecuting(true);
    try {
      const response = await fetch("http://localhost:8000/api/v1/runners/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          runner: selectedRunner,
          args: args ? JSON.parse(args) : [],
        }),
      });
      const data = await response.json();
      setResults(data);
      setDialogOpen(false);
    } catch (error) {
      console.error("Failed to execute runner:", error);
    } finally {
      setExecuting(false);
    }
  };

  useEffect(() => {
    fetchCommonRunners();
  }, []);

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      management: "bg-blue-500",
      jobs: "bg-green-500",
      orchestration: "bg-purple-500",
      cache: "bg-orange-500",
    };
    return colors[category] || "bg-gray-500";
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Salt Runners</h1>
            <p className="text-muted-foreground">
              Execute Salt runners for administrative tasks
            </p>
          </div>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Terminal className="mr-2 h-4 w-4" />
                Custom Runner
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Execute Custom Runner</DialogTitle>
                <DialogDescription>
                  Run a custom Salt runner function
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="runner">Runner Function</Label>
                  <Input
                    id="runner"
                    placeholder="e.g., manage.status"
                    value={selectedRunner}
                    onChange={(e) => setSelectedRunner(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="args">Arguments (JSON Array)</Label>
                  <Input
                    id="args"
                    placeholder='["arg1", "arg2"]'
                    value={args}
                    onChange={(e) => setArgs(e.target.value)}
                  />
                </div>
                <Button
                  className="w-full"
                  onClick={executeRunner}
                  disabled={executing || !selectedRunner}
                >
                  {executing ? "Executing..." : "Execute Runner"}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {results && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {results.success ? (
                  <CheckCircle2 className="h-5 w-5 text-green-500" />
                ) : (
                  <AlertCircle className="h-5 w-5 text-red-500" />
                )}
                Execution Results
              </CardTitle>
              <CardDescription>{results.message}</CardDescription>
            </CardHeader>
            <CardContent>
              <pre className="bg-muted p-4 rounded-lg overflow-auto max-h-96 text-sm">
                {JSON.stringify(results.data, null, 2)}
              </pre>
            </CardContent>
          </Card>
        )}

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {runners.map((runner) => (
            <Card key={runner.name} className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">{runner.name}</CardTitle>
                  <Badge className={getCategoryColor(runner.category)}>
                    {runner.category}
                  </Badge>
                </div>
                <CardDescription>{runner.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <Button
                  className="w-full"
                  onClick={() => {
                    setSelectedRunner(runner.name);
                    setDialogOpen(true);
                  }}
                >
                  <PlayCircle className="mr-2 h-4 w-4" />
                  Execute
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </DashboardLayout>
  );
}
