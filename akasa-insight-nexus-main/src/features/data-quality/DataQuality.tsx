import { useQuery } from "@tanstack/react-query";
import { getDataQualitySummary } from "@/api/client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { AlertCircle, CheckCircle, ExternalLink, RefreshCw } from "lucide-react";
import { formatDateTime } from "@/lib/format";

export function DataQuality() {
  const { data, isLoading, refetch } = useQuery({
    queryKey: ["data-quality"],
    queryFn: getDataQualitySummary,
  });

  const passedCount = data?.expectations.filter((e) => e.status === "pass").length || 0;
  const failedCount = data?.expectations.filter((e) => e.status === "fail").length || 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Data Quality</h1>
          <p className="text-muted-foreground mt-1">Validation reports and anomaly detection</p>
        </div>
        <Button onClick={() => refetch()} variant="outline">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Expectations Passed</CardTitle>
            <CheckCircle className="h-4 w-4 text-success" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-success">{passedCount}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Expectations Failed</CardTitle>
            <AlertCircle className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-destructive">{failedCount}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Duplicates Found</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{data?.duplicates || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Null Anomalies</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{data?.nullAnomalies || 0}</div>
          </CardContent>
        </Card>
      </div>

      {/* Expectations Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Validation Expectations</CardTitle>
              {data?.lastRun && (
                <p className="text-sm text-muted-foreground mt-1">
                  Last run: {formatDateTime(data.lastRun)}
                </p>
              )}
            </div>
            {data?.reportUrl && (
              <Button variant="outline" size="sm" asChild>
                <a href={data.reportUrl} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="h-4 w-4 mr-2" />
                  View Full Report
                </a>
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-12 text-muted-foreground">Loading...</div>
          ) : (
            <div className="space-y-3">
              {data?.expectations.map((expectation, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-4 border border-border rounded-lg hover:bg-muted/50"
                >
                  <div className="flex items-center gap-3">
                    <StatusBadge status={expectation.status} />
                    <span className="font-medium">{expectation.name}</span>
                  </div>
                  {expectation.failedCount !== undefined && (
                    <Badge variant="destructive">{expectation.failedCount} failures</Badge>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
