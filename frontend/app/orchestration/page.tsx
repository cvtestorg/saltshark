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
import { Workflow, PlayCircle, CheckCircle2, AlertCircle } from "lucide-react";

interface Orchestration {
  name: string;
  description: string;
  target: string;
}

export default function OrchestrationPage() {
  const [orchestrations, setOrchestrations] = useState<Orchestration[]>([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [selectedOrch, setSelectedOrch] = useState({ name: "", target: "*" });
  const [results, setResults] = useState<any>(null);

  const fetchCommonOrchestrations = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/orchestration/common");
      const data = await response.json();
      setOrchestrations(data.orchestrations);
    } catch (error) {
      console.error("Failed to fetch orchestrations:", error);
    }
  };

  const runOrchestration = async () => {
    setExecuting(true);
    try {
      const response = await fetch("http://localhost:8000/api/v1/orchestration/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          orchestration: selectedOrch.name,
          target: selectedOrch.target,
        }),
      });
      const data = await response.json();
      setResults(data);
      setDialogOpen(false);
    } catch (error) {
      console.error("Failed to run orchestration:", error);
    } finally {
      setExecuting(false);
    }
  };

  useEffect(() => {
    fetchCommonOrchestrations();
  }, []);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Orchestration</h1>
            <p className="text-muted-foreground">
              Run Salt orchestration workflows
            </p>
          </div>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Workflow className="mr-2 h-4 w-4" />
                Custom Orchestration
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Run Orchestration</DialogTitle>
                <DialogDescription>
                  Execute a Salt orchestration workflow
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="orch-name">Orchestration SLS</Label>
                  <Input
                    id="orch-name"
                    placeholder="e.g., deploy.webapp"
                    value={selectedOrch.name}
                    onChange={(e) =>
                      setSelectedOrch({ ...selectedOrch, name: e.target.value })
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="orch-target">Target</Label>
                  <Input
                    id="orch-target"
                    placeholder="* (all minions)"
                    value={selectedOrch.target}
                    onChange={(e) =>
                      setSelectedOrch({ ...selectedOrch, target: e.target.value })
                    }
                  />
                </div>
                <Button
                  className="w-full"
                  onClick={runOrchestration}
                  disabled={executing || !selectedOrch.name}
                >
                  {executing ? "Running..." : "Run Orchestration"}
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
                Orchestration Results
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
          {orchestrations.map((orch) => (
            <Card key={orch.name} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Workflow className="h-5 w-5" />
                  {orch.name}
                </CardTitle>
                <CardDescription>{orch.description}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex items-center gap-2">
                  <Badge variant="outline">Target: {orch.target}</Badge>
                </div>
                <Button
                  className="w-full"
                  onClick={() => {
                    setSelectedOrch({ name: orch.name, target: orch.target });
                    setDialogOpen(true);
                  }}
                >
                  <PlayCircle className="mr-2 h-4 w-4" />
                  Run
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {orchestrations.length === 0 && (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Workflow className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No Orchestrations</h3>
              <p className="text-sm text-muted-foreground text-center">
                Configure orchestration SLS files to get started
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
