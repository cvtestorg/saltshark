"use client";

import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/dashboard-layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { minionsAPI } from "@/lib/api";
import { Server, RefreshCw } from "lucide-react";
import type { MinionStatus } from "@/types";

export default function MinionsPage() {
  const [minions, setMinions] = useState<MinionStatus[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchMinions = async () => {
    setLoading(true);
    try {
      const data = await minionsAPI.list();
      setMinions(data.minions);
    } catch (error) {
      console.error("Failed to fetch minions:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMinions();
  }, []);

  const getStatusColor = (status: string | null) => {
    switch (status) {
      case "up":
        return "bg-green-500";
      case "down":
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  const getStatusBadge = (status: string | null) => {
    switch (status) {
      case "up":
        return <Badge className="bg-green-500">Online</Badge>;
      case "down":
        return <Badge variant="destructive">Offline</Badge>;
      default:
        return <Badge variant="secondary">Unknown</Badge>;
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Minions</h1>
            <p className="text-muted-foreground">
              Manage and monitor your Salt minions
            </p>
          </div>
          <Button onClick={fetchMinions} disabled={loading}>
            <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        </div>

        {loading && minions.length === 0 ? (
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {minions.map((minion) => (
              <Card key={minion.id} className="hover:shadow-lg transition-shadow">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <div className="flex items-center space-x-2">
                    <Server className="h-5 w-5 text-muted-foreground" />
                    <CardTitle className="text-lg font-semibold">
                      {minion.id}
                    </CardTitle>
                  </div>
                  {getStatusBadge(minion.status)}
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">OS:</span>
                      <span className="font-medium">
                        {minion.os || "Unknown"}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Release:</span>
                      <span className="font-medium">
                        {minion.osrelease || "Unknown"}
                      </span>
                    </div>
                    <div className="mt-4 flex gap-2">
                      <Button variant="outline" size="sm" className="flex-1">
                        Details
                      </Button>
                      <Button variant="outline" size="sm" className="flex-1">
                        Execute
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {!loading && minions.length === 0 && (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Server className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No minions found</h3>
              <p className="text-sm text-muted-foreground text-center">
                No minions are currently registered with the Salt master.
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
