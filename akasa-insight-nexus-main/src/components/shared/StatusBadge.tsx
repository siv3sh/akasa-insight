import { Badge } from "@/components/ui/badge";
import { CheckCircle, XCircle, AlertCircle } from "lucide-react";

interface StatusBadgeProps {
  status: "Succeeded" | "Failed" | "Partial" | "pass" | "fail";
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const variants = {
    Succeeded: { variant: "default" as const, icon: CheckCircle, className: "bg-success text-success-foreground" },
    pass: { variant: "default" as const, icon: CheckCircle, className: "bg-success text-success-foreground" },
    Failed: { variant: "destructive" as const, icon: XCircle, className: "" },
    fail: { variant: "destructive" as const, icon: XCircle, className: "" },
    Partial: { variant: "secondary" as const, icon: AlertCircle, className: "bg-warning text-warning-foreground" },
  };

  const config = variants[status];
  const Icon = config.icon;

  return (
    <Badge variant={config.variant} className={`gap-1 ${config.className}`}>
      <Icon className="h-3 w-3" />
      {status}
    </Badge>
  );
}
