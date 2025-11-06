import { useQuery } from "@tanstack/react-query";
import { getTopSpenders } from "@/api/client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatCurrency } from "@/lib/format";
import { Trophy } from "lucide-react";

export function TopSpenders() {
  const { data, isLoading } = useQuery({
    queryKey: ["top-spenders"],
    queryFn: () => getTopSpenders({ limit: 20 }),
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Top Spenders</h1>
        <p className="text-muted-foreground mt-1">Highest spending customers (last 30 days)</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Ranked by Total Spend</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-12 text-muted-foreground">Loading...</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border text-left text-sm text-muted-foreground">
                    <th className="pb-3 font-medium">Rank</th>
                    <th className="pb-3 font-medium">Customer</th>
                    <th className="pb-3 font-medium">Mobile</th>
                    <th className="pb-3 font-medium text-right">Orders</th>
                    <th className="pb-3 font-medium text-right">Total Spend</th>
                  </tr>
                </thead>
                <tbody>
                  {(data || []).map((spender, idx) => (
                    <tr key={spender.customer_id} className="border-b border-border last:border-0 hover:bg-muted/50">
                      <td className="py-4 text-sm">
                        <div className="flex items-center gap-2">
                          {idx < 3 && <Trophy className="h-4 w-4 text-warning" />}
                          <span className="font-semibold">{idx + 1}</span>
                        </div>
                      </td>
                      <td className="py-4 text-sm font-medium">{spender.customer_name}</td>
                      <td className="py-4 text-sm text-muted-foreground">{spender.mobile_number}</td>
                      <td className="py-4 text-sm text-right">
                        <Badge variant="secondary">{spender.orders}</Badge>
                      </td>
                      <td className="py-4 text-sm text-right font-semibold text-lg">
                        {formatCurrency(spender.spend)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
