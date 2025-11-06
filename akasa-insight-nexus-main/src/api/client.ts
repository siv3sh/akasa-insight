// API client with mock/real adapter pattern
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
import * as mocks from "./mocks";

const USE_MOCKS = import.meta.env.VITE_USE_MOCKS !== "false";
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:3001";

// Helper function to make API requests
const apiRequest = async (endpoint: string, options: RequestInit = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });
  
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
  }
  
  return response.json();
};

// Real API implementations
const realGetKpis = async (filters: ApiFilters): Promise<KpisResponse> => {
  const params = new URLSearchParams();
  if (filters.from) params.append('from', filters.from);
  if (filters.to) params.append('to', filters.to);
  
  return apiRequest(`/api/kpis?${params.toString()}`);
};

const realListCustomers = async (filters: ApiFilters): Promise<CustomersResponse> => {
  const params = new URLSearchParams();
  if (filters.page) params.append('page', filters.page.toString());
  if (filters.pageSize) params.append('pageSize', filters.pageSize.toString());
  if (filters.search) params.append('search', filters.search);
  
  return apiRequest(`/api/customers?${params.toString()}`);
};

const realGetCustomerDetail = async (id: string): Promise<CustomerDetail> => {
  // For simplicity, we'll return mock data for customer details
  return mocks.mockGetCustomerDetail(id);
};

const realGetOrdersTrend = async (filters: ApiFilters): Promise<OrdersTrendPoint[]> => {
  const params = new URLSearchParams();
  if (filters.granularity) params.append('granularity', filters.granularity);
  if (filters.from) params.append('from', filters.from);
  if (filters.to) params.append('to', filters.to);
  
  return apiRequest(`/api/orders-trend?${params.toString()}`);
};

const realGetRegionalRevenue = async (filters: ApiFilters): Promise<RegionalRevenueItem[]> => {
  const params = new URLSearchParams();
  if (filters.regions) {
    filters.regions.forEach(region => params.append('regions', region));
  }
  if (filters.from) params.append('from', filters.from);
  if (filters.to) params.append('to', filters.to);
  
  return apiRequest(`/api/regional-revenue?${params.toString()}`);
};

const realGetTopSpenders = async (filters: ApiFilters): Promise<TopSpenderItem[]> => {
  const params = new URLSearchParams();
  if (filters.limit) params.append('limit', filters.limit.toString());
  if (filters.from) params.append('from', filters.from);
  if (filters.to) params.append('to', filters.to);
  
  return apiRequest(`/api/top-spenders?${params.toString()}`);
};

const realGetDataQualitySummary = async (): Promise<DataQualitySummary> => {
  return apiRequest(`/api/data-quality`);
};

const realListIngestionRuns = async (filters: ApiFilters): Promise<IngestionRunsResponse> => {
  const params = new URLSearchParams();
  if (filters.page) params.append('page', filters.page.toString());
  if (filters.pageSize) params.append('pageSize', filters.pageSize.toString());
  
  return apiRequest(`/api/ingestion-runs?${params.toString()}`);
};

// Export functions that automatically switch between mock and real implementations
export const getKpis = async (filters: ApiFilters): Promise<KpisResponse> => {
  if (USE_MOCKS) return mocks.mockGetKpis(filters);
  return realGetKpis(filters);
};

export const listCustomers = async (filters: ApiFilters): Promise<CustomersResponse> => {
  if (USE_MOCKS) return mocks.mockListCustomers(filters);
  return realListCustomers(filters);
};

export const getCustomerDetail = async (id: string): Promise<CustomerDetail> => {
  if (USE_MOCKS) return mocks.mockGetCustomerDetail(id);
  return realGetCustomerDetail(id);
};

export const getOrdersTrend = async (filters: ApiFilters): Promise<OrdersTrendPoint[]> => {
  if (USE_MOCKS) return mocks.mockGetOrdersTrend(filters);
  return realGetOrdersTrend(filters);
};

export const getRegionalRevenue = async (filters: ApiFilters): Promise<RegionalRevenueItem[]> => {
  if (USE_MOCKS) return mocks.mockGetRegionalRevenue(filters);
  return realGetRegionalRevenue(filters);
};

export const getTopSpenders = async (filters: ApiFilters): Promise<TopSpenderItem[]> => {
  if (USE_MOCKS) return mocks.mockGetTopSpenders(filters);
  return realGetTopSpenders(filters);
};

export const getDataQualitySummary = async (): Promise<DataQualitySummary> => {
  if (USE_MOCKS) return mocks.mockGetDataQualitySummary();
  return realGetDataQualitySummary();
};

export const listIngestionRuns = async (filters: ApiFilters): Promise<IngestionRunsResponse> => {
  if (USE_MOCKS) return mocks.mockListIngestionRuns(filters);
  return realListIngestionRuns(filters);
};