/**
 * Email validation utilities
 */

export const validateEmailDomain = (email, allowedDomain = 'iiitdmj.ac.in') => {
  if (!email || email.trim() === '') {
    return { isValid: false, error: 'Email is required' };
  }

  const emailParts = email.split('@');
  if (emailParts.length !== 2) {
    return { isValid: false, error: 'Invalid email format' };
  }

  const domain = emailParts[1].toLowerCase().trim();

  if (domain !== allowedDomain) {
    return {
      isValid: false,
      error: `Email domain must be @${allowedDomain}`
    };
  }

  return { isValid: true, error: null };
};

export const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!email || !emailRegex.test(email)) {
    return { isValid: false, error: 'Invalid email format' };
  }
  return { isValid: true, error: null };
};
