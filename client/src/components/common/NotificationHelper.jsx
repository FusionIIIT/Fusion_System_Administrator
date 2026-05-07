import { showNotification } from '@mantine/notifications';
import { rem } from '@mantine/core';
import { FaCheck, FaTimes } from 'react-icons/fa';

/**
 * Notification Helper Utility
 * Centralized notification handling for consistent UX
 */

const xIcon = <FaTimes style={{ width: rem(20), height: rem(20) }} />;
const checkIcon = <FaCheck style={{ width: rem(20), height: rem(20) }} />;

export const showSuccessNotification = ({ 
  title = 'Success', 
  message, 
  position = 'top-center',
  autoClose = 5000 
}) => {
  showNotification({
    icon: checkIcon,
    title,
    message,
    position,
    withCloseButton: true,
    autoClose,
    color: 'green',
  });
};

export const showErrorNotification = ({ 
  title = 'Error', 
  message, 
  position = 'top-center',
  autoClose = 5000 
}) => {
  showNotification({
    icon: xIcon,
    title,
    message,
    position,
    withCloseButton: true,
    autoClose,
    color: 'red',
  });
};

export const handleApiError = (error, customMessage = 'An error occurred') => {
  const errorMessage = error.response
    ? `${JSON.stringify(error.response.data.error) || 
         JSON.stringify(error.response.data.data) || 
         JSON.stringify(error.response.data.message)}`
    : error.request
    ? 'No response received from the server'
    : `${error.message || customMessage}`;

  showErrorNotification({
    title: 'Error',
    message: errorMessage,
  });

  return errorMessage;
};

export default {
  showSuccessNotification,
  showErrorNotification,
  handleApiError,
};
