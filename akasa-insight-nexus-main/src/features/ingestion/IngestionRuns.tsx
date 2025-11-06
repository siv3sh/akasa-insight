import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { listIngestionRuns } from "@/api/client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { Badge } from "@/components/ui/badge";
import { ExternalLink, RefreshCw, ChevronLeft, ChevronRight } from "lucide-react";
import { formatDateTime, formatDuration } from "@/lib/format";

export function IngestionRuns() {
  const [page, setPage] = useState(1);
  const pageSize = 10;

  const { data, isLoading, refetch } = useQuery({
    queryKey: ["ingestion-runs", page],
    queryFn: () => listIngestionRuns({ page, pageSize }),
  });

  const totalPages = Math.ceil((data?.total || 0) / pageSize);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Ingestion Runs</h1>
          <p className="text-muted-foreground mt-1">Pipeline execution history and monitoring</p>
        </div>
        <Button onClick={() => refetch()} variant="outline">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Runs</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-12 text-muted-foreground">Loading...</div>
          ) : (
            <>
              <div className="space-y-3">
                {data?.runs.map((run) => (
                  <div
                    key={run.id}
                    className="flex items-center justify-between p-4 border border-border rounded-lg hover:bg-muted/50"
                  >
                    <div className="space-y-2 flex-1">
                      <div className="flex items-center gap-3">
                        <span className="font-mono text-sm font-medium">{run.id}</span>
                        <StatusBadge status={run.status} />
                        <span className="text-sm text-muted-foreground">
                          {formatDateTime(run.started_at)}
                        </span>
                      </div>
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <span>Duration: {formatDuration(run.duration_ms)}</span>
                        <span>Files: {run.files}</span>
                        <span>Rows: {run.rows.toLocaleString()}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {run.logUrl && (
                        <Button variant="ghost" size="sm" asChild>
                          <a href={run.logUrl} target="_blank" rel="noopener noreferrer">
                            <ExternalLink className="h-4 w-4" />
                          </a>
                        </Button>
                      )}
                      {run.rejectsUrl && (
                        <Badge variant="destructive">
                          <a href={run.rejectsUrl} target="_blank" rel="noopener noreferrer">
                            View Rejects
                          </a>
                        </Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex items-center justify-between mt-6">
                <div className="text-sm text-muted-foreground">
                  Showing {(page - 1) * pageSize + 1}-{Math.min(page * pageSize, data?.total || 0)} of {data?.total || 0}
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                  >
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
