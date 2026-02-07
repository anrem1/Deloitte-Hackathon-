import React from 'react';
import { AnalysisResults } from '../types/MenuTypes';
import { SummaryCard } from './SummaryCard';
import { ChangeCard } from './ChangeCard';

interface ResultsDisplayProps {
  results: AnalysisResults;
}

export const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ results }) => {
  return (
    <div className="results-section">
      <div className="summary-cards">
        <SummaryCard 
          label="Total Items" 
          value={results.summary.totalItems} 
        />
        <SummaryCard 
          label="Changes Suggested" 
          value={results.summary.itemsNeedingChange} 
        />
        <SummaryCard 
          label="Revenue Potential" 
          value={`$${results.summary.potentialRevenueIncrease.toLocaleString()}/mo`} 
        />
        <SummaryCard 
          label="Confidence Score" 
          value={`${results.summary.confidenceScore}%`} 
        />
      </div>

      <h2 className="changes-header">Recommended Changes</h2>
      
      <div className="changes-list">
        {results.changes.map((change, index) => (
          <ChangeCard 
            key={change.id} 
            change={change} 
            index={index} 
          />
        ))}
      </div>
    </div>
  );
};