import apiClient from './api';

/**
 * Mail Service - Handles all email-related API calls
 * Centralizes communication with backend mail endpoints
 */

export const mailBatch = async (batch) => {
  const response = await apiClient.post('/users/mail-batch/', { batch });
  return response.data;
};

export const sendBulkEmails = async (emailData) => {
  const response = await apiClient.post('/users/send-bulk-emails/', emailData);
  return response.data;
};

export const getEmailHistory = async (filters) => {
  const response = await apiClient.get('/users/email-history/', { params: filters });
  return response.data;
};
