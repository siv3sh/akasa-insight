const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3001;

// Enable CORS for all routes
app.use(cors());

// Serve static files from the outputs directory
const outputsDir = path.join(__dirname, '..', '..', 'outputs');

// Helper function to read JSON files
const readJsonFile = (filename) => {
  try {
    const data = fs.readFileSync(path.join(outputsDir, filename), 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.error(`Error reading ${filename}:`, error);
    return [];
  }
};

// API Routes
app.get('/api/kpis', (req, res) => {
  try {
    const repeatCustomersData = readJsonFile('sql_repeat_customers.json');
    const monthlyTrendsData = readJsonFile('sql_monthly_trends.json');
    const regionalRevenueData = readJsonFile('sql_regional_revenue.json');
    
    // Transform data to match frontend expectations
    const kpis = {
      repeatCustomers: repeatCustomersData.length,
      monthlyOrders: monthlyTrendsData.map(item => ({
        month: `${item.year}-${String(item.month).padStart(2, '0')}`,
        count: item.order_count
      })),
      regionalRevenue: regionalRevenueData.map(item => ({
        region: item.region,
        revenue: item.total_revenue
      })),
      topSpenders: [] // We don't have top spenders data
    };
    
    res.json(kpis);
  } catch (error) {
    console.error('Error fetching KPIs:', error);
    res.status(500).json({ error: 'Failed to fetch KPIs' });
  }
});

app.get('/api/customers', (req, res) => {
  try {
    const repeatCustomersData = readJsonFile('sql_repeat_customers.json');
    
    // Transform data to match frontend expectations
    const customers = {
      rows: repeatCustomersData.map(customer => ({
        customer_id: customer.customer_id.toString(),
        customer_name: customer.customer_name,
        mobile_number: customer.mobile_number,
        region: customer.region,
        total_orders: customer.order_count,
        lifetime_spend: customer.order_count * 5000, // Estimated value
        last_order_at: new Date().toISOString(),
        is_repeat: true
      })),
      total: repeatCustomersData.length
    };
    
    res.json(customers);
  } catch (error) {
    console.error('Error fetching customers:', error);
    res.status(500).json({ error: 'Failed to fetch customers' });
  }
});

app.get('/api/orders-trend', (req, res) => {
  try {
    const monthlyTrendsData = readJsonFile('sql_monthly_trends.json');
    
    // Transform data to match frontend expectations
    const ordersTrend = monthlyTrendsData.map(item => ({
      ts: `${item.year}-${String(item.month).padStart(2, '0')}-01`,
      orders: item.order_count
    }));
    
    res.json(ordersTrend);
  } catch (error) {
    console.error('Error fetching orders trend:', error);
    res.status(500).json({ error: 'Failed to fetch orders trend' });
  }
});

app.get('/api/regional-revenue', (req, res) => {
  try {
    const regionalRevenueData = readJsonFile('sql_regional_revenue.json');
    
    // Transform data to match frontend expectations
    const regionalRevenue = regionalRevenueData.map(item => ({
      region: item.region,
      revenue: item.total_revenue,
      orders: item.order_count
    }));
    
    res.json(regionalRevenue);
  } catch (error) {
    console.error('Error fetching regional revenue:', error);
    res.status(500).json({ error: 'Failed to fetch regional revenue' });
  }
});

app.get('/api/top-spenders', (req, res) => {
  try {
    // We don't have top spenders data, so we'll create some mock data based on regional revenue
    const regionalRevenueData = readJsonFile('sql_regional_revenue.json');
    
    // Create mock top spenders based on regional data
    const topSpenders = regionalRevenueData.slice(0, 5).map((item, index) => ({
      customer_id: `CUST-${1000 + index}`,
      customer_name: `Customer ${item.region}`,
      mobile_number: `+91-98765432${10 + index}`,
      spend: item.total_revenue / (index + 1),
      orders: item.order_count
    }));
    
    res.json(topSpenders);
  } catch (error) {
    console.error('Error fetching top spenders:', error);
    res.status(500).json({ error: 'Failed to fetch top spenders' });
  }
});

app.get('/api/data-quality', (req, res) => {
  try {
    // Mock data quality summary
    const dataQuality = {
      lastRun: new Date().toISOString(),
      expectations: [
        { name: "customer_id not null", status: "pass" },
        { name: "order_amount > 0", status: "pass" },
        { name: "mobile_number format", status: "pass" },
        { name: "region in allowed list", status: "pass" }
      ],
      duplicates: 0,
      nullAnomalies: 0,
      reportUrl: "#"
    };
    
    res.json(dataQuality);
  } catch (error) {
    console.error('Error fetching data quality:', error);
    res.status(500).json({ error: 'Failed to fetch data quality' });
  }
});

app.get('/api/ingestion-runs', (req, res) => {
  try {
    // Mock ingestion runs
    const runs = [
      {
        id: "RUN-2001",
        started_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        duration_ms: 45000,
        status: "Succeeded",
        files: 2,
        rows: 28,
        logUrl: "#",
        rejectsUrl: undefined
      },
      {
        id: "RUN-2000",
        started_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        duration_ms: 38000,
        status: "Succeeded",
        files: 2,
        rows: 28,
        logUrl: "#",
        rejectsUrl: undefined
      }
    ];
    
    res.json({
      runs,
      total: runs.length
    });
  } catch (error) {
    console.error('Error fetching ingestion runs:', error);
    res.status(500).json({ error: 'Failed to fetch ingestion runs' });
  }
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Start the server
app.listen(PORT, () => {
  console.log(`Akasa Air API server is running on port ${PORT}`);
  console.log(`Outputs directory: ${outputsDir}`);
});