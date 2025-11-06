import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { listCustomers } from "@/api/client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Search, ChevronLeft, ChevronRight } from "lucide-react";
import { formatCurrency, formatDate } from "@/lib/format";
import { EmptyState } from "@/components/shared/EmptyState";

export function Customers() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const pageSize = 10;

  const { data, isLoading } = useQuery({
    queryKey: ["customers", page, search],
    queryFn: () => listCustomers({ page, pageSize, search }),
  });

  const totalPages = Math.ceil((data?.total || 0) / pageSize);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Customers</h1>
        <p className="text-muted-foreground mt-1">Browse and analyze customer profiles</p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Customer Directory</CardTitle>
            <div className="relative w-72">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by name or mobile..."
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setPage(1);
                }}
                className="pl-9"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-12 text-muted-foreground">Loading...</div>
          ) : !data?.rows.length ? (
            <EmptyState title="No customers found" description="Try adjusting your search" />
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border text-left text-sm text-muted-foreground">
                      <th className="pb-3 font-medium">Customer</th>
                      <th className="pb-3 font-medium">Mobile</th>
                      <th className="pb-3 font-medium">Region</th>
                      <th className="pb-3 font-medium text-right">Orders</th>
                      <th className="pb-3 font-medium text-right">Lifetime Spend</th>
                      <th className="pb-3 font-medium">Last Order</th>
                      <th className="pb-3 font-medium">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.rows.map((customer) => (
                      <tr key={customer.customer_id} className="border-b border-border last:border-0 hover:bg-muted/50">
                        <td className="py-4 text-sm font-medium">{customer.customer_name}</td>
                        <td className="py-4 text-sm text-muted-foreground">{customer.mobile_number}</td>
                        <td className="py-4 text-sm">{customer.region}</td>
                        <td className="py-4 text-sm text-right">{customer.total_orders}</td>
                        <td className="py-4 text-sm text-right font-semibold">
                          {formatCurrency(customer.lifetime_spend)}
                        </td>
                        <td className="py-4 text-sm text-muted-foreground">
                          {formatDate(customer.last_order_at)}
                        </td>
                        <td className="py-4">
                          {customer.is_repeat ? (
                            <Badge className="bg-success text-success-foreground">Repeat</Badge>
                          ) : (
                            <Badge variant="secondary">New</Badge>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="flex items-center justify-between mt-6">
                <div className="text-sm text-muted-foreground">
                  Showing {(page - 1) * pageSize + 1}-{Math.min(page * pageSize, data.total)} of {data.total}
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
