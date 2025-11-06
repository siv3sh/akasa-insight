import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "next-themes";
import { AppLayout } from "@/components/layout/AppLayout";
import { Dashboard } from "@/features/dashboard/Dashboard";
import { Customers } from "@/features/customers/Customers";
import { OrdersTrends } from "@/features/orders-trends/OrdersTrends";
import { RegionalRevenue } from "@/features/regional-revenue/RegionalRevenue";
import { TopSpenders } from "@/features/top-spenders/TopSpenders";
import { DataQuality } from "@/features/data-quality/DataQuality";
import { IngestionRuns } from "@/features/ingestion/IngestionRuns";
import { Settings } from "@/features/settings/Settings";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30000,
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

const App = () => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider attribute="class" defaultTheme="light" enableSystem>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route element={<AppLayout />}>
              <Route path="/" element={<Dashboard />} />
              <Route path="/customers" element={<Customers />} />
              <Route path="/orders-trends" element={<OrdersTrends />} />
              <Route path="/regional-revenue" element={<RegionalRevenue />} />
              <Route path="/top-spenders" element={<TopSpenders />} />
              <Route path="/data-quality" element={<DataQuality />} />
              <Route path="/ingestion-runs" element={<IngestionRuns />} />
              <Route path="/settings" element={<Settings />} />
            </Route>
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </ThemeProvider>
  </QueryClientProvider>
);

export default App;
