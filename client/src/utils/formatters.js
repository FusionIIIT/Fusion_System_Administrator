/**
 * Formatting utilities for data display
 */

export const formatDate = (date) => {
  if (!date) return '';
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return dateObj.toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

export const formatShortDate = (date) => {
  if (!date) return '';
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return dateObj.toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

export const formatDateTime = (date) => {
  if (!date) return '';
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return dateObj.toLocaleString('en-IN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const formatName = (firstName, lastName) => {
  const first = firstName?.trim() || '';
  const last = lastName?.trim() || '';
  
  if (!first && !last) return '';
  if (!last) return first;
  return `${first} ${last}`;
};

export const formatFullName = (person) => {
  if (!person) return '';
  
  if (person.full_name) {
    return person.full_name;
  }
  
  const first = person.first_name?.trim() || '';
  const last = person.last_name?.trim() || '';
  
  if (!first && !last) return '';
  if (!last) return first;
  return `${first} ${last}`;
};

export const formatPhoneNumber = (phone) => {
  if (!phone) return '';
  const cleaned = phone.replace(/\D/g, '');
  if (cleaned.length !== 10) return phone;
  return `${cleaned.slice(0, 5)}-${cleaned.slice(5)}`;
};

export const capitalizeFirst = (str) => {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
};

export const formatUserRole = (userType) => {
  if (!userType) return '';
  return userType.charAt(0).toUpperCase() + userType.slice(1);
};

export const formatBatchYear = (year) => {
  if (!year) return '';
  return `Batch of ${year}`;
};

export const truncateText = (text, maxLength = 50) => {
  if (!text || text.length <= maxLength) return text;
  return `${text.slice(0, maxLength)}...`;
};
