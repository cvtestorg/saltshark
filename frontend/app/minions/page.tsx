"use client";

import useSWR from "swr";
import { DashboardLayout } from "@/components/dashboard-layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Server, MoreHorizontal, RefreshCw, Search, Terminal } from "lucide-react";
import { minionsAPI } from "@/lib/api";
import { useState } from "react";
import Link from "next/link";

export default function MinionsPage() {
  const [searchTerm, setSearchTerm] = useState("");
  
  const { data, isLoading, isValidating, mutate } = useSWR(
    "/api/v1/minions",
    () => minionsAPI.list()
  );

  const minions = data?.data || {};
  const isRefreshing = isLoading || isValidating;

  const filteredMinions = Object.entries(minions).filter(([id]) =>
    id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Minions</h1>
            <p className="text-muted-foreground">
              Monitor and manage connected minions
            </p>
          </div>
          <Button onClick={() => mutate()} disabled={isRefreshing}>
             <RefreshCw className={`mr-2 h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        </div>

        <div className="flex items-center space-x-2">
          <div className="relative flex-1">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Search minions..."
              className="pl-8"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {filteredMinions.map(([id, grains]: [string, any]) => (
              <Card key={id}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    {id}
                  </CardTitle>
                  <Server className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold mb-2">
                    {grains.os || "Unknown OS"}
                  </div>
                  <div className="space-y-2 text-sm text-muted-foreground">
                  <div className="flex justify-between">
                      <span>OS Release:</span>
                      <span className="font-medium text-foreground">{grains.osrelease || "-"}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Kernel:</span>
                      <span className="font-medium text-foreground">{grains.kernel || "-"}</span>
                    </div>
                    <div className="flex justify-between">
                       <span>IPv4:</span>
                       <span className="font-medium text-foreground">
                         {Array.isArray(grains.ipv4) 
                           ? grains.ipv4.filter((ip: string) => ip !== '127.0.0.1').join(', ') 
                           : grains.ipv4 || "-"}
                       </span>
                    </div>
                     <div className="flex justify-between">
                      <span>Salt Version:</span>
                      <span className="font-medium text-foreground">{grains.saltversion || "-"}</span>
                    </div>
                  </div>
                  
                  <div className="mt-4 flex gap-2">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="outline" className="w-full">
                          <MoreHorizontal className="mr-2 h-4 w-4" />
                          Actions
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuLabel>Actions</DropdownMenuLabel>
                        <DropdownMenuItem asChild>
                            <Link href={`/states?target=${id}`}>Apply State</Link>
                        </DropdownMenuItem>
                         <DropdownMenuItem asChild>
                            <Link href={`/jobs?target=${id}`}>View Jobs</Link>
                        </DropdownMenuItem>
                         <DropdownMenuItem asChild>
                            <Link href={`/advanced?target=${id}`}>Run Command</Link>
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </CardContent>
              </Card>
            ))}
            
            {filteredMinions.length === 0 && (
                 <div className="col-span-full flex flex-col items-center justify-center py-12 text-muted-foreground">
                  <Server className="h-12 w-12 mb-4" />
                  <p>No minions found matching your search.</p>
                </div>
            )}
             {!filteredMinions.length && !searchTerm && (
                <div className="col-span-full flex flex-col items-center justify-center py-12 text-muted-foreground">
                  <Server className="h-12 w-12 mb-4" />
                  <p>No minions connected.</p>
                </div>
            )}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
