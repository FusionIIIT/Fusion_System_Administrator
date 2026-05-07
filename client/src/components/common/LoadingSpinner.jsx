import React from 'react';
import { Center, Loader } from '@mantine/core';

/**
 * LoadingSpinner Component
 * Reusable loading indicator for the application
 */

const LoadingSpinner = ({ 
  size = 'md', 
  color = 'blue', 
  fullScreen = false,
  text = 'Loading...'
}) => {
  if (fullScreen) {
    return (
      <Center h="100vh" w="100vw">
        <Loader size={size} color={color} />
      </Center>
    );
  }

  return (
    <Center h={200}>
      <Loader size={size} color={color} />
    </Center>
  );
};

export default LoadingSpinner;
