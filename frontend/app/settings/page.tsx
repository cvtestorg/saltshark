"use client";

import { DashboardLayout } from "@/components/dashboard-layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Settings as SettingsIcon } from "lucide-react";

export default function SettingsPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground">
            Configure SaltShark application settings
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Salt API Configuration</CardTitle>
            <CardDescription>
              Configure the connection to your Salt API server
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="api-url">API URL</Label>
              <Input
                id="api-url"
                placeholder="http://localhost:8000"
                defaultValue="http://localhost:8000"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="api-user">Username</Label>
              <Input
                id="api-user"
                placeholder="saltapi"
                defaultValue="saltapi"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="api-password">Password</Label>
              <Input
                id="api-password"
                type="password"
                placeholder="••••••••"
              />
            </div>
            <Button>Save Configuration</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Display Settings</CardTitle>
            <CardDescription>
              Customize the appearance of the application
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Dark Mode</Label>
                <p className="text-sm text-muted-foreground">
                  Toggle dark mode theme
                </p>
              </div>
              <Button variant="outline">Toggle</Button>
            </div>
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Auto-refresh</Label>
                <p className="text-sm text-muted-foreground">
                  Automatically refresh data every 30 seconds
                </p>
              </div>
              <Button variant="outline">Enable</Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>About</CardTitle>
            <CardDescription>
              SaltShark version and information
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Version:</span>
                <span className="font-medium">0.1.0</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Backend API:</span>
                <span className="font-medium">v1</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Framework:</span>
                <span className="font-medium">Next.js 16</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
