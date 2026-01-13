"use client";

import { useState, useEffect } from "react";
import { DashboardLayout } from "@/components/dashboard-layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Database, Search, RefreshCw } from "lucide-react";

export default function PillarsPage() {
  const [selectedMinion, setSelectedMinion] = useState<string>("");
  const [pillars, setPillars] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [searchKey, setSearchKey] = useState("");

  const fetchPillars = async (minionId: string) => {
    if (!minionId) return;
    
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/v1/pillars/${minionId}`);
      const data = await response.json();
      setPillars(data);
    } catch (error) {
      console.error("Failed to fetch pillars:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchPillarItem = async (key: string) => {
    if (!selectedMinion || !key) return;
    
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/pillars/${selectedMinion}/item/${key}`
      );
      const data = await response.json();
      console.log("Pillar item:", data);
    } catch (error) {
      console.error("Failed to fetch pillar item:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Pillar Management</h1>
            <p className="text-muted-foreground">
              View and manage Salt pillar data
            </p>
          </div>
          <Button
            onClick={() => selectedMinion && fetchPillars(selectedMinion)}
            disabled={loading || !selectedMinion}
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Select Minion</CardTitle>
            <CardDescription>
              Choose a minion to view its pillar data
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="minion">Minion ID</Label>
              <Input
                id="minion"
                placeholder="Enter minion ID (e.g., minion-1)"
                value={selectedMinion}
                onChange={(e) => setSelectedMinion(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && selectedMinion) {
                    fetchPillars(selectedMinion);
                  }
                }}
              />
            </div>
            <Button
              className="w-full"
              onClick={() => fetchPillars(selectedMinion)}
              disabled={!selectedMinion}
            >
              <Database className="mr-2 h-4 w-4" />
              Load Pillars
            </Button>
          </CardContent>
        </Card>

        {pillars && (
          <Card>
            <CardHeader>
              <CardTitle>Pillar Data for {pillars.minion_id}</CardTitle>
              <CardDescription>
                All pillar key-value pairs for this minion
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex gap-2">
                  <div className="flex-1">
                    <Input
                      placeholder="Search pillar keys..."
                      value={searchKey}
                      onChange={(e) => setSearchKey(e.target.value)}
                    />
                  </div>
                  <Button
                    variant="outline"
                    onClick={() => fetchPillarItem(searchKey)}
                    disabled={!searchKey}
                  >
                    <Search className="h-4 w-4" />
                  </Button>
                </div>
                
                <div className="border rounded-lg">
                  <pre className="p-4 overflow-auto max-h-[600px] text-sm">
                    {JSON.stringify(pillars.data, null, 2)}
                  </pre>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {!pillars && !loading && (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Database className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No Pillar Data</h3>
              <p className="text-sm text-muted-foreground text-center">
                Select a minion above to view its pillar configuration
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
