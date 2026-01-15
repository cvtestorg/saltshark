"use client";

import useSWR from "swr";
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
import { Calendar, Trash2, RefreshCw, Plus } from "lucide-react";
import { schedulesAPI } from "@/lib/api";
import React from "react";

export default function SchedulesPage() {
  const { data, isLoading, isValidating, mutate } = useSWR(
    "/api/v1/schedules/*",
    () => schedulesAPI.list("*")
  );

  const schedules = data?.data || {};
  const isRefreshing = isLoading || isValidating;

  const deleteSchedule = async (target: string, name: string) => {
    try {
      await schedulesAPI.delete(target, name);
      mutate();
    } catch (error) {
      console.error("Failed to delete schedule:", error);
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Schedules</h1>
            <p className="text-muted-foreground">
              Manage automated task schedules
            </p>
          </div>
          <div className="flex gap-2">
            <Button onClick={() => mutate()} disabled={isRefreshing} variant="outline">
               <RefreshCw className={`mr-2 h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`} />
              Refresh
            </Button>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Create Schedule
            </Button>
          </div>
        </div>

        {isLoading ? (
           <div className="flex items-center justify-center py-12">
            <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <div className="grid gap-6">
             {Object.keys(schedules).length === 0 && (
              <Card>
                <CardContent className="flex flex-col items-center justify-center py-12">
                  <Calendar className="h-12 w-12 text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No schedules found</h3>
                  <p className="text-muted-foreground text-center mb-4">
                    Create a schedule to automate Salt jobs.
                  </p>
                </CardContent>
              </Card>
            )}

            {Object.entries(schedules).map(([minionId, minionSchedules]: [string, any]) => (
               <Card key={minionId}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Calendar className="h-5 w-5" />
                    {minionId}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                     {Object.entries(minionSchedules).map(([name, config]: [string, any]) => (
                        <div key={name} className="flex items-center justify-between p-4 border rounded-lg">
                           <div>
                            <div className="font-medium">{name}</div>
                            <div className="text-sm text-muted-foreground">
                              Function: {config.function}
                            </div>
                            {config.cron && (
                                <Badge variant="secondary" className="mt-2">
                                    {config.cron}
                                </Badge>
                            )}
                            {config.seconds && (
                                 <Badge variant="secondary" className="mt-2">
                                    Every {config.seconds} seconds
                                </Badge>
                            )}
                           </div>
                           
                            <AlertDialog>
                            <AlertDialogTrigger asChild>
                              <Button size="icon" variant="ghost" className="text-destructive">
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </AlertDialogTrigger>
                            <AlertDialogContent>
                              <AlertDialogHeader>
                                <AlertDialogTitle>Delete Schedule?</AlertDialogTitle>
                                <AlertDialogDescription>
                                  Are you sure you want to delete the schedule &quot;{name}&quot; on {minionId}?
                                </AlertDialogDescription>
                              </AlertDialogHeader>
                              <AlertDialogFooter>
                                <AlertDialogCancel>Cancel</AlertDialogCancel>
                                <AlertDialogAction onClick={() => deleteSchedule(minionId, name)}>
                                  Delete
                                </AlertDialogAction>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                        </div>
                     ))}
                  </div>
                </CardContent>
               </Card>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
