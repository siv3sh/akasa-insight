// API types for Akasa Air Data Engineering Console

export interface KpisResponse {
  repeatCustomers: number;
  monthlyOrders: Array<{ month: string; count: number }>;
  regionalRevenue: Array<{ region: string; revenue: number }>;
  topSpenders: Array<{
    customer_id: string;
    customer_name: string;
    mobile_number: string;
    spend: number;
  }>;
}

export interface CustomerRow {
  customer_id: string;
  customer_name: string;
  mobile_number: string;
  region: string;
  total_orders: number;
  lifetime_spend: number;
  last_order_at: string;
  is_repeat: boolean;
}

export interface CustomersResponse {
  rows: CustomerRow[];
  total: number;
}

export interface Order {
  order_id: string;
  order_date: string;
  amount: number;
  items: string[];
  status: string;
}

export interface CustomerDetail {
  profile: CustomerRow;
  orders: Order[];
  metrics: {
    lifetime_spend: number;
    total_orders: number;
    last_order_at: string;
    avg_order_value: number;
  };
}

export interface OrdersTrendPoint {
  ts: string;
  orders: number;
}

export interface RegionalRevenueItem {
  region: string;
  revenue: number;
  orders: number;
}

export interface TopSpenderItem {
  customer_id: string;
  customer_name: string;
  mobile_number: string;
  spend: number;
  orders: number;
}

export interface DataQualityExpectation {
  name: string;
  status: "pass" | "fail";
  failedCount?: number;
}

export interface DataQualitySummary {
  lastRun: string;
  expectations: DataQualityExpectation[];
  duplicates: number;
  nullAnomalies: number;
  reportUrl?: string;
}

export interface IngestionRun {
  id: string;
  started_at: string;
  duration_ms: number;
  status: "Succeeded" | "Failed" | "Partial";
  files: number;
  rows: number;
  logUrl?: string;
  rejectsUrl?: string;
}

export interface IngestionRunsResponse {
  runs: IngestionRun[];
  total: number;
}

export interface ApiFilters {
  from?: string;
  to?: string;
  regions?: string[];
  search?: string;
  page?: number;
  pageSize?: number;
  granularity?: "day" | "week" | "month";
  limit?: number;
}
