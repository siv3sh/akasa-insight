import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { useTheme } from "next-themes";
import { Trash2, Info } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

export function Settings() {
  const { theme, setTheme } = useTheme();
  const queryClient = useQueryClient();

  const handleClearCache = () => {
    queryClient.clear();
    toast.success("Cache cleared successfully");
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground mt-1">Configure your console preferences</p>
      </div>

      {/* Appearance */}
      <Card>
        <CardHeader>
          <CardTitle>Appearance</CardTitle>
          <CardDescription>Customize the look and feel of the console</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="dark-mode">Dark Mode</Label>
              <p className="text-sm text-muted-foreground">Enable dark theme</p>
            </div>
            <Switch
              id="dark-mode"
              checked={theme === "dark"}
              onCheckedChange={(checked) => setTheme(checked ? "dark" : "light")}
            />
          </div>
        </CardContent>
      </Card>

      {/* Cache Management */}
      <Card>
        <CardHeader>
          <CardTitle>Cache Management</CardTitle>
          <CardDescription>Manage cached data and query results</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Clear All Cached Data</Label>
              <p className="text-sm text-muted-foreground">
                Remove all cached queries and force fresh data fetch
              </p>
            </div>
            <Button variant="destructive" onClick={handleClearCache}>
              <Trash2 className="h-4 w-4 mr-2" />
              Clear Cache
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Environment Info */}
      <Card>
        <CardHeader>
          <CardTitle>Environment Information</CardTitle>
          <CardDescription>Current environment and system details</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center justify-between py-2">
            <span className="text-sm font-medium">Environment</span>
            <Badge variant="secondary">Development</Badge>
          </div>
          <div className="flex items-center justify-between py-2">
            <span className="text-sm font-medium">API Mode</span>
            <Badge>{import.meta.env.VITE_USE_MOCKS !== "false" ? "Mock Data" : "Production"}</Badge>
          </div>
          <div className="flex items-center justify-between py-2">
            <span className="text-sm font-medium">Version</span>
            <span className="text-sm text-muted-foreground">1.0.0</span>
          </div>
          <div className="mt-4 p-4 bg-muted rounded-lg flex items-start gap-3">
            <Info className="h-5 w-5 text-muted-foreground flex-shrink-0 mt-0.5" />
            <div className="text-sm text-muted-foreground">
              <p className="font-medium text-foreground mb-1">Security Notice</p>
              <p>
                This console never displays sensitive credentials or connection strings. All secrets
                are securely managed server-side.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
