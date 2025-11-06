import { useQuery } from "@tanstack/react-query";
import { getKpis } from "@/api/client";
import { KpiCard } from "@/components/shared/KpiCard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, ShoppingCart, DollarSign, TrendingUp } from "lucide-react";
import { formatCurrency, formatRelativeTime } from "@/lib/format";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { ErrorBoundary } from "@/components/shared/ErrorBoundary";

export function Dashboard() {
  const { data, isLoading, dataUpdatedAt } = useQuery({
    queryKey: ["kpis"],
    queryFn: () => getKpis({ from: "2024-01-01", to: "2024-11-30" }),
    refetchInterval: 60000, // Background refresh every minute
  });

  const lastUpdated = dataUpdatedAt ? formatRelativeTime(new Date(dataUpdatedAt)) : "";

  return (
    <ErrorBoundary>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Real-time analytics and key performance indicators
          </p>
        </div>

        {/* KPI Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <KpiCard
            title="Repeat Customers"
            value={data?.repeatCustomers || 0}
            icon={<Users className="h-4 w-4" />}
            tooltip="Customers with more than 1 order"
            isLoading={isLoading}
            lastUpdated={lastUpdated}
            delta={{ value: 12, isPositive: true }}
          />
          <KpiCard
            title="Total Orders (Nov)"
            value={data?.monthlyOrders[data.monthlyOrders.length - 1]?.count || 0}
            icon={<ShoppingCart className="h-4 w-4" />}
            tooltip="Total orders in the current month"
            isLoading={isLoading}
            lastUpdated={lastUpdated}
            delta={{ value: 8, isPositive: true }}
          />
          <KpiCard
            title="Total Revenue"
            value={formatCurrency(
              data?.regionalRevenue.reduce((sum, r) => sum + r.revenue, 0) || 0
            )}
            icon={<DollarSign className="h-4 w-4" />}
            tooltip="Sum of revenue across all regions"
            isLoading={isLoading}
            lastUpdated={lastUpdated}
          />
          <KpiCard
            title="Avg Spend (Top 5)"
            value={formatCurrency(
              data?.topSpenders.length
                ? data.topSpenders.reduce((sum, s) => sum + s.spend, 0) / data.topSpenders.length
                : 0
            )}
            icon={<TrendingUp className="h-4 w-4" />}
            tooltip="Average spend of top 5 customers (last 30 days)"
            isLoading={isLoading}
            lastUpdated={lastUpdated}
          />
        </div>

        {/* Charts */}
        <div className="grid gap-6 md:grid-cols-2">
          {/* Monthly Orders Trend */}
          <Card>
            <CardHeader>
              <CardTitle>Monthly Orders Trend</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={data?.monthlyOrders || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis
                    dataKey="month"
                    stroke="hsl(var(--muted-foreground))"
                    fontSize={12}
                    tickFormatter={(value) => value.slice(5)}
                  />
                  <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "var(--radius)",
                    }}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="count"
                    stroke="hsl(var(--chart-1))"
                    strokeWidth={2}
                    dot={{ fill: "hsl(var(--chart-1))" }}
                    name="Orders"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Regional Revenue */}
          <Card>
            <CardHeader>
              <CardTitle>Revenue by Region</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={data?.regionalRevenue || []}>
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
                  <Legend />
                  <Bar dataKey="revenue" fill="hsl(var(--chart-2))" name="Revenue (₹)" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Top Spenders Table */}
        <Card>
          <CardHeader>
            <CardTitle>Top Spenders (Last 30 Days)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border text-left text-sm text-muted-foreground">
                    <th className="pb-3 font-medium">Rank</th>
                    <th className="pb-3 font-medium">Customer</th>
                    <th className="pb-3 font-medium">Mobile</th>
                    <th className="pb-3 font-medium text-right">Spend</th>
                  </tr>
                </thead>
                <tbody>
                  {(data?.topSpenders || []).map((spender, idx) => (
                    <tr key={spender.customer_id} className="border-b border-border last:border-0">
                      <td className="py-3 text-sm">{idx + 1}</td>
                      <td className="py-3 text-sm font-medium">{spender.customer_name}</td>
                      <td className="py-3 text-sm text-muted-foreground">{spender.mobile_number}</td>
                      <td className="py-3 text-sm text-right font-semibold">
                        {formatCurrency(spender.spend)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </ErrorBoundary>
  );
}
