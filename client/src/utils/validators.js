/**
 * Validation utilities for form inputs
 */

export const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validatePhone = (phone) => {
  const phoneRegex = /^\d{10}$/;
  return phoneRegex.test(phone.replace(/[-\s]/g, ''));
};

export const validateRequired = (value) => {
  if (typeof value === 'string') {
    return value.trim().length > 0;
  }
  return value !== null && value !== undefined;
};

export const validateRollNumber = (rollNo) => {
  // Adjust pattern based on your institute's roll number format
  const rollRegex = /^[A-Z0-9]{6,}$/i;
  return rollRegex.test(rollNo);
};

export const validateDate = (date) => {
  if (!date) return false;
  const dateObj = new Date(date);
  return !isNaN(dateObj.getTime());
};

export const validateFileSize = (file, maxSizeMB = 5) => {
  if (!file) return true;
  const maxSizeBytes = maxSizeMB * 1024 * 1024;
  return file.size <= maxSizeBytes;
};

export const validateFileType = (file, allowedTypes = ['text/csv']) => {
  if (!file) return true;
  return allowedTypes.includes(file.type);
};

// Form validation helper
export const validateForm = (formData, validationRules) => {
  const errors = {};
  
  Object.keys(validationRules).forEach((field) => {
    const value = formData[field];
    const rules = validationRules[field];
    
    if (rules.required && !validateRequired(value)) {
      errors[field] = `${field} is required`;
    } else if (rules.email && value && !validateEmail(value)) {
      errors[field] = 'Invalid email address';
    } else if (rules.phone && value && !validatePhone(value)) {
      errors[field] = 'Invalid phone number';
    } else if (rules.pattern && value && !rules.pattern.test(value)) {
      errors[field] = rules.patternMessage || 'Invalid format';
    }
  });
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};
