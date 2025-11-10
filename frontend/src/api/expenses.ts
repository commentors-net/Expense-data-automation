/**
 * API client for expense-related operations
 */
import axios from 'axios';

// Configure base URL - default to localhost, can be overridden by environment variable
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface ExpenseData {
  date: string;
  category: string;
  description: string;
  amount: number;
}

export interface UploadResponse {
  imported: number;
  skipped: number;
  status: string;
  message?: string;
  storage_url?: string;
}

export interface PreviewResponse {
  status: string;
  total_rows: number;
  preview_rows: number;
  data: ExpenseData[];
  filename: string;
}

export interface ExpensesResponse {
  status: string;
  year: string;
  count: number;
  expenses: ExpenseData[];
}

export interface YearsResponse {
  status: string;
  years: string[];
  count: number;
}

export interface StatsResponse {
  status: string;
  year: string;
  total_expenses: number;
  total_amount: number;
  categories: {
    [key: string]: {
      count: number;
      total: number;
    };
  };
}

/**
 * Upload an Excel file and process expenses
 */
export const uploadExpenseFile = async (
  file: File,
  year: string,
  onProgress?: (progress: number) => void
): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('year', year);

  const response = await apiClient.post<UploadResponse>('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total && onProgress) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(progress);
      }
    },
  });

  return response.data;
};

/**
 * Preview normalized data without saving
 */
export const previewExpenseFile = async (
  file: File,
  year: string
): Promise<PreviewResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('year', year);

  const response = await apiClient.post<PreviewResponse>('/preview', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

/**
 * Get all years with expense data
 */
export const getAllYears = async (): Promise<YearsResponse> => {
  const response = await apiClient.get<YearsResponse>('/expenses');
  return response.data;
};

/**
 * Get expenses for a specific year
 */
export const getExpensesByYear = async (
  year: string,
  limit: number = 100
): Promise<ExpensesResponse> => {
  const response = await apiClient.get<ExpensesResponse>(`/expenses/${year}`, {
    params: { limit },
  });
  return response.data;
};

/**
 * Get statistics for a specific year
 */
export const getYearStats = async (year: string): Promise<StatsResponse> => {
  const response = await apiClient.get<StatsResponse>(`/stats/${year}`);
  return response.data;
};

/**
 * Delete all expenses for a specific year
 */
export const deleteYearExpenses = async (year: string): Promise<void> => {
  await apiClient.delete(`/expenses/${year}`);
};

export default apiClient;
