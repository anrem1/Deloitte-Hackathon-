import React from 'react';

interface SummaryCardProps {
  label: string;
  value: string | number;
}

export const SummaryCard: React.FC<SummaryCardProps> = ({ label, value }) => {
  return (
    <div className="summary-card">
      <div className="summary-label">{label}</div>
      <div className="summary-value">{value}</div>
    </div>
  );
};