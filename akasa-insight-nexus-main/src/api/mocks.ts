// Mock data for Akasa Air Data Engineering Console
import {
  KpisResponse,
  CustomersResponse,
  CustomerDetail,
  OrdersTrendPoint,
  RegionalRevenueItem,
  TopSpenderItem,
  DataQualitySummary,
  IngestionRunsResponse,
  ApiFilters,
} from "./types";

const regions = ["North", "South", "East", "West", "Central"];

const customerNames = [
  "Rajesh Kumar", "Priya Sharma", "Amit Patel", "Sneha Gupta", "Vijay Singh",
  "Anita Desai", "Rahul Mehta", "Kavita Reddy", "Suresh Nair", "Deepa Iyer",
];

export const mockGetKpis = async (filters: ApiFilters): Promise<KpisResponse> => {
  await new Promise((resolve) => setTimeout(resolve, 800));

  const monthlyOrders = [
    { month: "2024-01", count: 1250 },
    { month: "2024-02", count: 1380 },
    { month: "2024-03", count: 1520 },
    { month: "2024-04", count: 1680 },
    { month: "2024-05", count: 1820 },
    { month: "2024-06", count: 1950 },
    { month: "2024-07", count: 2100 },
    { month: "2024-08", count: 2280 },
    { month: "2024-09", count: 2450 },
    { month: "2024-10", count: 2620 },
    { month: "2024-11", count: 2800 },
  ];

  const regionalRevenue = regions.map((region) => ({
    region,
    revenue: Math.floor(Math.random() * 5000000) + 2000000,
  }));

  const topSpenders = customerNames.slice(0, 5).map((name, idx) => ({
    customer_id: `CUST-${1000 + idx}`,
    customer_name: name,
    mobile_number: `+91-98765432${10 + idx}`,
    spend: Math.floor(Math.random() * 500000) + 100000,
  }));

  return {
    repeatCustomers: 4234,
    monthlyOrders,
    regionalRevenue,
    topSpenders,
  };
};

export const mockListCustomers = async (
  filters: ApiFilters
): Promise<CustomersResponse> => {
  await new Promise((resolve) => setTimeout(resolve, 600));

  const page = filters.page || 1;
  const pageSize = filters.pageSize || 10;
  const total = 250;

  const rows = Array.from({ length: pageSize }, (_, i) => {
    const idx = (page - 1) * pageSize + i;
    const totalOrders = Math.floor(Math.random() * 15) + 1;
    return {
      customer_id: `CUST-${1000 + idx}`,
      customer_name: customerNames[idx % customerNames.length],
      mobile_number: `+91-98765432${(10 + idx) % 100}`,
      region: regions[idx % regions.length],
      total_orders: totalOrders,
      lifetime_spend: Math.floor(Math.random() * 800000) + 50000,
      last_order_at: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
      is_repeat: totalOrders > 1,
    };
  });

  return { rows, total };
};

export const mockGetCustomerDetail = async (id: string): Promise<CustomerDetail> => {
  await new Promise((resolve) => setTimeout(resolve, 400));

  const totalOrders = Math.floor(Math.random() * 15) + 1;
  const lifetimeSpend = Math.floor(Math.random() * 800000) + 50000;

  const profile = {
    customer_id: id,
    customer_name: customerNames[0],
    mobile_number: "+91-9876543210",
    region: "North",
    total_orders: totalOrders,
    lifetime_spend: lifetimeSpend,
    last_order_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    is_repeat: totalOrders > 1,
  };

  const orders = Array.from({ length: totalOrders }, (_, i) => ({
    order_id: `ORD-${5000 + i}`,
    order_date: new Date(Date.now() - (i + 1) * 15 * 24 * 60 * 60 * 1000).toISOString(),
    amount: Math.floor(Math.random() * 80000) + 10000,
    items: [`Item ${i + 1}`, `Item ${i + 2}`],
    status: i === 0 ? "Completed" : "Delivered",
  }));

  return {
    profile,
    orders,
    metrics: {
      lifetime_spend: lifetimeSpend,
      total_orders: totalOrders,
      last_order_at: profile.last_order_at,
      avg_order_value: Math.floor(lifetimeSpend / totalOrders),
    },
  };
};

export const mockGetOrdersTrend = async (
  filters: ApiFilters
): Promise<OrdersTrendPoint[]> => {
  await new Promise((resolve) => setTimeout(resolve, 500));

  const granularity = filters.granularity || "day";
  const days = granularity === "day" ? 30 : granularity === "week" ? 12 : 6;

  return Array.from({ length: days }, (_, i) => ({
    ts: new Date(Date.now() - (days - i) * 24 * 60 * 60 * 1000).toISOString().split("T")[0],
    orders: Math.floor(Math.random() * 100) + 50,
  }));
};

export const mockGetRegionalRevenue = async (
  filters: ApiFilters
): Promise<RegionalRevenueItem[]> => {
  await new Promise((resolve) => setTimeout(resolve, 400));

  return regions.map((region) => ({
    region,
    revenue: Math.floor(Math.random() * 5000000) + 2000000,
    orders: Math.floor(Math.random() * 2000) + 500,
  }));
};

export const mockGetTopSpenders = async (
  filters: ApiFilters
): Promise<TopSpenderItem[]> => {
  await new Promise((resolve) => setTimeout(resolve, 400));

  const limit = filters.limit || 10;

  return customerNames.slice(0, limit).map((name, idx) => ({
    customer_id: `CUST-${1000 + idx}`,
    customer_name: name,
    mobile_number: `+91-98765432${10 + idx}`,
    spend: Math.floor(Math.random() * 500000) + 100000,
    orders: Math.floor(Math.random() * 20) + 5,
  }));
};

export const mockGetDataQualitySummary = async (): Promise<DataQualitySummary> => {
  await new Promise((resolve) => setTimeout(resolve, 300));

  return {
    lastRun: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    expectations: [
      { name: "customer_id not null", status: "pass" },
      { name: "order_amount > 0", status: "pass" },
      { name: "mobile_number format", status: "fail", failedCount: 3 },
      { name: "region in allowed list", status: "pass" },
    ],
    duplicates: 5,
    nullAnomalies: 2,
    reportUrl: "#",
  };
};

export const mockListIngestionRuns = async (
  filters: ApiFilters
): Promise<IngestionRunsResponse> => {
  await new Promise((resolve) => setTimeout(resolve, 500));

  const page = filters.page || 1;
  const pageSize = filters.pageSize || 10;
  const total = 45;

  const runs = Array.from({ length: pageSize }, (_, i) => {
    const idx = (page - 1) * pageSize + i;
    const statuses: Array<"Succeeded" | "Failed" | "Partial"> = ["Succeeded", "Succeeded", "Succeeded", "Partial", "Failed"];
    return {
      id: `RUN-${2000 + idx}`,
      started_at: new Date(Date.now() - idx * 6 * 60 * 60 * 1000).toISOString(),
      duration_ms: Math.floor(Math.random() * 120000) + 30000,
      status: statuses[idx % statuses.length],
      files: Math.floor(Math.random() * 5) + 1,
      rows: Math.floor(Math.random() * 50000) + 10000,
      logUrl: "#",
      rejectsUrl: idx % 3 === 0 ? "#" : undefined,
    };
  });

  return { runs, total };
};
