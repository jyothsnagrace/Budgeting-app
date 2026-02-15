// API Configuration
// This uses environment variables set during build time

// Get API URL from environment variable or use localhost for development
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Full API endpoints
export const API_ENDPOINTS = {
  // Auth
  signup: `${API_URL}/api/v1/auth/signup`,
  login: `${API_URL}/api/v1/auth/login`,
  
  // Budgets
  budgetsList: `${API_URL}/api/v1/budgets/list`,
  budgetsSet: `${API_URL}/api/v1/budgets/set`,
  
  // Expenses
  expensesList: `${API_URL}/api/v1/expenses/list`,
  expensesParse: `${API_URL}/api/v1/expenses/parse`,
  expensesAdd: `${API_URL}/api/v1/expenses/add`,
  expensesAddDirect: `${API_URL}/api/v1/expenses/add-direct`,
  expensesParseReceipt: `${API_URL}/api/v1/expenses/parse-receipt`,
  
  // Voice
  voiceTranscribe: `${API_URL}/api/v1/voice/transcribe`,
  
  // Advisor
  advisorAsk: `${API_URL}/api/v1/advisor/ask`,
};

// Helper function to build URL with query params
export const buildUrl = (endpoint: string, params?: Record<string, string>) => {
  if (!params) return endpoint;
  const queryString = new URLSearchParams(params).toString();
  return `${endpoint}?${queryString}`;
};
