import React from 'react';

export const LoadingSpinner: React.FC = () => {
  return (
    <div className="analyzing">
      <div className="spinner"></div>
      <p className="analyzing-text">Analyzing your menu...</p>
      <p className="analyzing-hint">Examining pricing, descriptions, and market positioning</p>
    </div>
  );
};