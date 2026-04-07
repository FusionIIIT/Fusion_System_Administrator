/**
 * Application-wide constants
 */

// User Types
export const USER_TYPES = {
  STUDENT: 'student',
  FACULTY: 'faculty',
  STAFF: 'staff',
};

// Programmes
export const PROGRAMMES = ['B.Tech', 'B.Des', 'M.Tech', 'M.Des', 'PhD'];

// Categories
export const CATEGORIES = ['GEN', 'OBC', 'SC', 'ST'];

// Gender Options
export const GENDER_OPTIONS = [
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' },
];

// Title Options
export const TITLE_OPTIONS = ['Dr.', 'Mr.', 'Mrs.', 'Ms.'];

// Designation Types
export const DESIGNATION_TYPES = {
  FACULTY: 'faculty',
  STAFF: 'staff',
};

// Notification Positions
export const NOTIFICATION_POSITIONS = {
  TOP_CENTER: 'top-center',
  TOP_RIGHT: 'top-right',
  BOTTOM_RIGHT: 'bottom-right',
};

// File Upload
export const MAX_FILE_SIZE_MB = 5;
export const ALLOWED_FILE_TYPES = ['text/csv'];

// API Endpoints (for reference)
export const API_ENDPOINTS = {
  USERS: '/users',
  ROLES: '/roles',
  DEPARTMENTS: '/departments',
  BATCHES: '/batches',
  DESIGNATIONS: '/designations',
};

// Pagination
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  PAGE_SIZE_OPTIONS: [10, 20, 50, 100],
};

// Date Formats
export const DATE_FORMATS = {
  DISPLAY: 'DD MMMM YYYY',
  SHORT: 'DD MMM YYYY',
  INPUT: 'YYYY-MM-DD',
};
