"use client";

import { useState, useEffect } from "react";
import { DashboardLayout } from "@/components/dashboard-layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Key, CheckCircle, XCircle, Trash2, RefreshCw, Clock } from "lucide-react";

export default function KeysPage() {
  const [keys, setKeys] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const fetchKeys = async () => {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/v1/keys");
      const data = await response.json();
      setKeys(data.data);
    } catch (error) {
      console.error("Failed to fetch keys:", error);
    } finally {
      setLoading(false);
    }
  };

  const acceptKey = async (minionId: string) => {
    try {
      await fetch(`http://localhost:8000/api/v1/keys/${minionId}/accept`, {
        method: "POST",
      });
      fetchKeys();
    } catch (error) {
      console.error("Failed to accept key:", error);
    }
  };

  const rejectKey = async (minionId: string) => {
    try {
      await fetch(`http://localhost:8000/api/v1/keys/${minionId}/reject`, {
        method: "POST",
      });
      fetchKeys();
    } catch (error) {
      console.error("Failed to reject key:", error);
    }
  };

  const deleteKey = async (minionId: string) => {
    try {
      await fetch(`http://localhost:8000/api/v1/keys/${minionId}`, {
        method: "DELETE",
      });
      fetchKeys();
    } catch (error) {
      console.error("Failed to delete key:", error);
    }
  };

  useEffect(() => {
    fetchKeys();
  }, []);

  const renderKeyList = (title: string, keyList: string[], status: string, icon: React.ReactNode, badgeVariant: any) => {
    if (!keyList || keyList.length === 0) return null;

    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {icon}
            {title}
          </CardTitle>
          <CardDescription>
            {keyList.length} minion(s) with {status} keys
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {keyList.map((minionId) => (
              <div
                key={minionId}
                className="flex items-center justify-between p-3 border rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <Key className="h-4 w-4 text-muted-foreground" />
                  <span className="font-medium">{minionId}</span>
                  <Badge variant={badgeVariant}>{status}</Badge>
                </div>
                <div className="flex gap-2">
                  {status === "pending" && (
                    <>
                      <Button
                        size="sm"
                        onClick={() => acceptKey(minionId)}
                      >
                        <CheckCircle className="h-4 w-4 mr-1" />
                        Accept
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => rejectKey(minionId)}
                      >
                        <XCircle className="h-4 w-4 mr-1" />
                        Reject
                      </Button>
                    </>
                  )}
                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button size="sm" variant="destructive">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>Delete Key</AlertDialogTitle>
                        <AlertDialogDescription>
                          Are you sure you want to delete the key for {minionId}?
                          This action cannot be undone.
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction onClick={() => deleteKey(minionId)}>
                          Delete
                        </AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Minion Keys</h1>
            <p className="text-muted-foreground">
              Manage minion authentication keys
            </p>
          </div>
          <Button onClick={fetchKeys} disabled={loading}>
            <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        </div>

        {loading && !keys ? (
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : keys ? (
          <div className="space-y-4">
            {renderKeyList(
              "Pending Keys",
              keys.return?.[0]?.data?.return?.minions_pre || [],
              "pending",
              <Clock className="h-5 w-5 text-yellow-500" />,
              "outline"
            )}
            {renderKeyList(
              "Accepted Keys",
              keys.return?.[0]?.data?.return?.minions || [],
              "accepted",
              <CheckCircle className="h-5 w-5 text-green-500" />,
              "default"
            )}
            {renderKeyList(
              "Rejected Keys",
              keys.return?.[0]?.data?.return?.minions_rejected || [],
              "rejected",
              <XCircle className="h-5 w-5 text-red-500" />,
              "destructive"
            )}
            {renderKeyList(
              "Denied Keys",
              keys.return?.[0]?.data?.return?.minions_denied || [],
              "denied",
              <XCircle className="h-5 w-5 text-gray-500" />,
              "secondary"
            )}
          </div>
        ) : (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Key className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No Keys</h3>
              <p className="text-sm text-muted-foreground text-center">
                No minion keys found
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
