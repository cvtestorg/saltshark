"use client";

import { useState } from "react";
import { DashboardLayout } from "@/components/dashboard-layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import {
  Cloud,
  Terminal,
  Bell,
  Database,
  Zap,
  Activity,
  Target,
  RefreshCw,
} from "lucide-react";

export default function AdvancedPage() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);

  // Cloud Management
  const [cloudProviders, setCloudProviders] = useState<any>(null);
  const [cloudProfiles, setCloudProfiles] = useState<any>(null);

  const fetchCloudProviders = async () => {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/v1/cloud/providers");
      const data = await response.json();
      setCloudProviders(data);
    } catch (error) {
      console.error("Failed to fetch cloud providers:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCloudProfiles = async () => {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/v1/cloud/profiles");
      const data = await response.json();
      setCloudProfiles(data);
    } catch (error) {
      console.error("Failed to fetch cloud profiles:", error);
    } finally {
      setLoading(false);
    }
  };

  // Salt SSH
  const [sshConfig, setSshConfig] = useState({
    target: "",
    function: "test.ping",
    roster: "flat",
  });

  const executeSsh = async () => {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/v1/ssh/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(sshConfig),
      });
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error("Failed to execute SSH:", error);
    } finally {
      setLoading(false);
    }
  };

  // Beacons
  const [beacons, setBeacons] = useState<any>(null);

  const fetchBeacons = async (target: string = "*") => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/v1/beacons/${target}`);
      const data = await response.json();
      setBeacons(data);
    } catch (error) {
      console.error("Failed to fetch beacons:", error);
    } finally {
      setLoading(false);
    }
  };

  // Events
  const [events, setEvents] = useState<any>(null);

  const fetchEvents = async (tag: string = "") => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/events?tag=${encodeURIComponent(tag)}`
      );
      const data = await response.json();
      setEvents(data);
    } catch (error) {
      console.error("Failed to fetch events:", error);
    } finally {
      setLoading(false);
    }
  };

  // Nodegroups
  const [nodegroups, setNodegroups] = useState<any>(null);

  const fetchNodegroups = async () => {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/v1/nodegroups");
      const data = await response.json();
      setNodegroups(data);
    } catch (error) {
      console.error("Failed to fetch nodegroups:", error);
    } finally {
      setLoading(false);
    }
  };

  // Reactor
  const [reactors, setReactors] = useState<any>(null);

  const fetchReactors = async () => {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/v1/reactor");
      const data = await response.json();
      setReactors(data);
    } catch (error) {
      console.error("Failed to fetch reactors:", error);
    } finally {
      setLoading(false);
    }
  };

  // Mine
  const [mineData, setMineData] = useState<any>(null);

  const getMineData = async (target: string, func: string) => {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/v1/mine/get", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target, function: func }),
      });
      const data = await response.json();
      setMineData(data);
    } catch (error) {
      console.error("Failed to get mine data:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Advanced Features</h1>
          <p className="text-muted-foreground">
            Cloud management, SSH, Beacons, Events, and more advanced Salt features
          </p>
        </div>

        <Tabs defaultValue="cloud" className="space-y-4">
          <TabsList>
            <TabsTrigger value="cloud">
              <Cloud className="mr-2 h-4 w-4" />
              Cloud
            </TabsTrigger>
            <TabsTrigger value="ssh">
              <Terminal className="mr-2 h-4 w-4" />
              Salt SSH
            </TabsTrigger>
            <TabsTrigger value="beacons">
              <Bell className="mr-2 h-4 w-4" />
              Beacons
            </TabsTrigger>
            <TabsTrigger value="mine">
              <Database className="mr-2 h-4 w-4" />
              Mine
            </TabsTrigger>
            <TabsTrigger value="events">
              <Activity className="mr-2 h-4 w-4" />
              Events
            </TabsTrigger>
            <TabsTrigger value="targeting">
              <Target className="mr-2 h-4 w-4" />
              Targeting
            </TabsTrigger>
            <TabsTrigger value="reactor">
              <Zap className="mr-2 h-4 w-4" />
              Reactor
            </TabsTrigger>
          </TabsList>

          <TabsContent value="cloud" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Cloud Management</CardTitle>
                <CardDescription>
                  Manage cloud infrastructure via Salt Cloud
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-2">
                  <Button onClick={fetchCloudProviders} disabled={loading}>
                    <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
                    List Providers
                  </Button>
                  <Button onClick={fetchCloudProfiles} disabled={loading} variant="outline">
                    List Profiles
                  </Button>
                </div>

                {cloudProviders && (
                  <div className="border rounded-lg p-4">
                    <h3 className="font-semibold mb-2">Cloud Providers</h3>
                    <pre className="text-sm overflow-auto max-h-60">
                      {JSON.stringify(cloudProviders.data, null, 2)}
                    </pre>
                  </div>
                )}

                {cloudProfiles && (
                  <div className="border rounded-lg p-4">
                    <h3 className="font-semibold mb-2">Cloud Profiles</h3>
                    <pre className="text-sm overflow-auto max-h-60">
                      {JSON.stringify(cloudProfiles.data, null, 2)}
                    </pre>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="ssh" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Salt SSH</CardTitle>
                <CardDescription>
                  Execute commands on agentless systems via SSH
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="ssh-target">Target</Label>
                  <Input
                    id="ssh-target"
                    placeholder="host1,host2"
                    value={sshConfig.target}
                    onChange={(e) => setSshConfig({ ...sshConfig, target: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="ssh-function">Function</Label>
                  <Input
                    id="ssh-function"
                    placeholder="test.ping"
                    value={sshConfig.function}
                    onChange={(e) => setSshConfig({ ...sshConfig, function: e.target.value })}
                  />
                </div>
                <Button onClick={executeSsh} disabled={loading || !sshConfig.target}>
                  <Terminal className="mr-2 h-4 w-4" />
                  Execute via SSH
                </Button>

                {results && (
                  <div className="border rounded-lg p-4">
                    <pre className="text-sm overflow-auto max-h-96">
                      {JSON.stringify(results, null, 2)}
                    </pre>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="beacons" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Beacons</CardTitle>
                <CardDescription>
                  Configure system monitoring beacons
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button onClick={() => fetchBeacons("*")} disabled={loading}>
                  <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
                  List Beacons
                </Button>

                {beacons && (
                  <div className="border rounded-lg p-4">
                    <pre className="text-sm overflow-auto max-h-96">
                      {JSON.stringify(beacons.data, null, 2)}
                    </pre>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="mine" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Salt Mine</CardTitle>
                <CardDescription>
                  Share data between minions using Salt Mine
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Target</Label>
                    <Input id="mine-target" placeholder="*" />
                  </div>
                  <div className="space-y-2">
                    <Label>Function</Label>
                    <Input id="mine-function" placeholder="network.ip_addrs" />
                  </div>
                </div>
                <Button
                  onClick={() => {
                    const target = (document.getElementById("mine-target") as HTMLInputElement)?.value || "*";
                    const func = (document.getElementById("mine-function") as HTMLInputElement)?.value;
                    if (func) getMineData(target, func);
                  }}
                  disabled={loading}
                >
                  Get Mine Data
                </Button>

                {mineData && (
                  <div className="border rounded-lg p-4">
                    <pre className="text-sm overflow-auto max-h-96">
                      {JSON.stringify(mineData.data, null, 2)}
                    </pre>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="events" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Event Stream</CardTitle>
                <CardDescription>
                  Monitor Salt event bus
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-2">
                  <Input id="event-tag" placeholder="Event tag filter (optional)" />
                  <Button
                    onClick={() => {
                      const tag = (document.getElementById("event-tag") as HTMLInputElement)?.value || "";
                      fetchEvents(tag);
                    }}
                    disabled={loading}
                  >
                    Get Events
                  </Button>
                </div>

                {events && (
                  <div className="border rounded-lg p-4">
                    <pre className="text-sm overflow-auto max-h-96">
                      {JSON.stringify(events.data, null, 2)}
                    </pre>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="targeting" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Advanced Targeting</CardTitle>
                <CardDescription>
                  Nodegroups and compound targeting
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button onClick={fetchNodegroups} disabled={loading}>
                  <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
                  List Nodegroups
                </Button>

                {nodegroups && (
                  <div className="border rounded-lg p-4">
                    <pre className="text-sm overflow-auto max-h-96">
                      {JSON.stringify(nodegroups.data, null, 2)}
                    </pre>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="reactor" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Reactor System</CardTitle>
                <CardDescription>
                  Event-driven automation with Salt Reactor
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button onClick={fetchReactors} disabled={loading}>
                  <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
                  List Reactors
                </Button>

                {reactors && (
                  <div className="border rounded-lg p-4">
                    <pre className="text-sm overflow-auto max-h-96">
                      {JSON.stringify(reactors.data, null, 2)}
                    </pre>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
}
