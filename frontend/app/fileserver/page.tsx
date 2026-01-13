"use client";

import { useState } from "react";
import { DashboardLayout } from "@/components/dashboard-layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { FileText, Folder, RefreshCw } from "lucide-react";

export default function FileServerPage() {
  const [environment, setEnvironment] = useState("base");
  const [files, setFiles] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const fetchFiles = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/fileserver/files?environment=${environment}`
      );
      const data = await response.json();
      setFiles(data);
    } catch (error) {
      console.error("Failed to fetch files:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">File Server</h1>
            <p className="text-muted-foreground">
              Browse and manage Salt file server
            </p>
          </div>
          <Button onClick={fetchFiles} disabled={loading}>
            <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>File Server Browser</CardTitle>
            <CardDescription>
              Browse files in the Salt file server
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="environment">Environment</Label>
              <Input
                id="environment"
                placeholder="base"
                value={environment}
                onChange={(e) => setEnvironment(e.target.value)}
              />
            </div>
            <Button onClick={fetchFiles} disabled={loading}>
              <Folder className="mr-2 h-4 w-4" />
              List Files
            </Button>
          </CardContent>
        </Card>

        {files && (
          <Card>
            <CardHeader>
              <CardTitle>Files in {files.environment}</CardTitle>
              <CardDescription>
                File server contents
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="border rounded-lg">
                <pre className="p-4 overflow-auto max-h-[600px] text-sm">
                  {JSON.stringify(files.data, null, 2)}
                </pre>
              </div>
            </CardContent>
          </Card>
        )}

        {!files && !loading && (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <FileText className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No Files Loaded</h3>
              <p className="text-sm text-muted-foreground text-center">
                Select an environment and click "List Files" to browse
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
