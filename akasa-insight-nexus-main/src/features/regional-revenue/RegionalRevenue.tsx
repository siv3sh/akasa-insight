import { useQuery } from "@tanstack/react-query";
import { getRegionalRevenue } from "@/api/client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { formatCurrency } from "@/lib/format";

export function RegionalRevenue() {
  const { data, isLoading } = useQuery({
    queryKey: ["regional-revenue"],
    queryFn: () => getRegionalRevenue({}),
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Regional Revenue</h1>
        <p className="text-muted-foreground mt-1">Revenue distribution across regions</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Revenue by Region</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-12 text-muted-foreground">Loading...</div>
          ) : (
            <>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={data || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="region" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                  <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "var(--radius)",
                    }}
                    formatter={(value: number) => formatCurrency(value)}
                  />
                  <Bar dataKey="revenue" fill="hsl(var(--chart-2))" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>

              <div className="mt-6 overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border text-left text-sm text-muted-foreground">
                      <th className="pb-3 font-medium">Region</th>
                      <th className="pb-3 font-medium text-right">Revenue</th>
                      <th className="pb-3 font-medium text-right">Orders</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(data || []).map((item) => (
                      <tr key={item.region} className="border-b border-border last:border-0">
                        <td className="py-3 text-sm font-medium">{item.region}</td>
                        <td className="py-3 text-sm text-right font-semibold">
                          {formatCurrency(item.revenue)}
                        </td>
                        <td className="py-3 text-sm text-right">{item.orders.toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
