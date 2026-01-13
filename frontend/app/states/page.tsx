"use client";

import { useState } from "react";
import { DashboardLayout } from "@/components/dashboard-layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { FileCode, PlayCircle, TestTube2, CheckCircle2, AlertCircle } from "lucide-react";

interface StateApplyRequest {
  target: string;
  state: string;
  test: boolean;
}

export default function StatesPage() {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [highstateDialogOpen, setHighstateDialogOpen] = useState(false);
  const [applying, setApplying] = useState(false);
  const [stateRequest, setStateRequest] = useState<StateApplyRequest>({
    target: "*",
    state: "",
    test: false,
  });
  const [results, setResults] = useState<any>(null);

  const handleApplyState = async () => {
    setApplying(true);
    try {
      const response = await fetch("http://localhost:8000/api/v1/states/apply", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(stateRequest),
      });
      const data = await response.json();
      setResults(data);
      setDialogOpen(false);
    } catch (error) {
      console.error("Failed to apply state:", error);
    } finally {
      setApplying(false);
    }
  };

  const handleHighstate = async (target: string, test: boolean) => {
    setApplying(true);
    try {
      const response = await fetch("http://localhost:8000/api/v1/states/highstate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target, test }),
      });
      const data = await response.json();
      setResults(data);
      setHighstateDialogOpen(false);
    } catch (error) {
      console.error("Failed to apply highstate:", error);
    } finally {
      setApplying(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">State Management</h1>
            <p className="text-muted-foreground">
              Apply and manage Salt states across your infrastructure
            </p>
          </div>
          <div className="flex gap-2">
            <Dialog open={highstateDialogOpen} onOpenChange={setHighstateDialogOpen}>
              <DialogTrigger asChild>
                <Button variant="outline">
                  <TestTube2 className="mr-2 h-4 w-4" />
                  Highstate
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Apply Highstate</DialogTitle>
                  <DialogDescription>
                    Apply all states assigned to target minions
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="highstate-target">Target</Label>
                    <Input
                      id="highstate-target"
                      placeholder="* (all minions)"
                      defaultValue="*"
                    />
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox id="highstate-test" />
                    <label
                      htmlFor="highstate-test"
                      className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                    >
                      Test mode (dry run)
                    </label>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      className="flex-1"
                      onClick={() => handleHighstate("*", false)}
                      disabled={applying}
                    >
                      <PlayCircle className="mr-2 h-4 w-4" />
                      Apply
                    </Button>
                    <Button
                      variant="outline"
                      className="flex-1"
                      onClick={() => handleHighstate("*", true)}
                      disabled={applying}
                    >
                      <TestTube2 className="mr-2 h-4 w-4" />
                      Test
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
              <DialogTrigger asChild>
                <Button>
                  <PlayCircle className="mr-2 h-4 w-4" />
                  Apply State
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Apply Salt State</DialogTitle>
                  <DialogDescription>
                    Apply a specific state to target minions
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="target">Target</Label>
                    <Input
                      id="target"
                      placeholder="* (all minions)"
                      value={stateRequest.target}
                      onChange={(e) =>
                        setStateRequest({ ...stateRequest, target: e.target.value })
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="state">State Name</Label>
                    <Input
                      id="state"
                      placeholder="e.g., webserver, database"
                      value={stateRequest.state}
                      onChange={(e) =>
                        setStateRequest({ ...stateRequest, state: e.target.value })
                      }
                    />
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="test"
                      checked={stateRequest.test}
                      onCheckedChange={(checked) =>
                        setStateRequest({ ...stateRequest, test: checked as boolean })
                      }
                    />
                    <label
                      htmlFor="test"
                      className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                    >
                      Test mode (dry run)
                    </label>
                  </div>
                  <Button
                    className="w-full"
                    onClick={handleApplyState}
                    disabled={applying || !stateRequest.state}
                  >
                    {applying ? "Applying..." : "Apply State"}
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
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

        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileCode className="h-5 w-5" />
                Common States
              </CardTitle>
              <CardDescription>
                Frequently used state configurations
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex items-center justify-between p-3 border rounded-lg hover:bg-accent cursor-pointer">
                <div>
                  <div className="font-medium">webserver</div>
                  <div className="text-sm text-muted-foreground">
                    Apache/Nginx configuration
                  </div>
                </div>
                <Badge variant="outline">SLS</Badge>
              </div>
              <div className="flex items-center justify-between p-3 border rounded-lg hover:bg-accent cursor-pointer">
                <div>
                  <div className="font-medium">database</div>
                  <div className="text-sm text-muted-foreground">
                    Database server setup
                  </div>
                </div>
                <Badge variant="outline">SLS</Badge>
              </div>
              <div className="flex items-center justify-between p-3 border rounded-lg hover:bg-accent cursor-pointer">
                <div>
                  <div className="font-medium">security</div>
                  <div className="text-sm text-muted-foreground">
                    Security hardening policies
                  </div>
                </div>
                <Badge variant="outline">SLS</Badge>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Recent State Runs</CardTitle>
              <CardDescription>
                Latest state execution history
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-sm text-muted-foreground">
                No recent state executions to display
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
