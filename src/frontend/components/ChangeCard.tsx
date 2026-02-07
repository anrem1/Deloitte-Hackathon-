import React from 'react';
import { TrendingUp } from 'lucide-react';
import { MenuChange } from '../types/MenuTypes';
import { getCategoryIcon, getImpactClass } from '../utils/helpers';

interface ChangeCardProps {
  change: MenuChange;
  index: number;
}

export const ChangeCard: React.FC<ChangeCardProps> = ({ change, index }) => {
  const CategoryIcon = getCategoryIcon(change.category);

  return (
    <div 
      className="change-card"
      style={{ animationDelay: `${index * 0.1}s` }}
    >
      <div className="change-header">
        <div className="change-title">
          <span className={`category-badge ${change.category}`}>
            <CategoryIcon className="category-icon" />
            {change.category}
          </span>
          <h3 className="item-name">{change.itemName}</h3>
        </div>
        <span className={`impact-badge ${getImpactClass(change.impact)}`}>
          {change.impact} impact
        </span>
      </div>
      
      <div className="change-details">
        <div className="change-row">
          <span className="change-label">Current</span>
          <span className="change-value">{change.currentValue}</span>
        </div>
        <div className="change-row">
          <span className="change-label">Suggested</span>
          <span className="change-value suggested-value">{change.suggestedValue}</span>
        </div>
      </div>
      
      <div className="reasoning">{change.reasoning}</div>
      
      <div className="expected-lift">
        <TrendingUp className="lift-icon" />
        {change.expectedLift}
      </div>
    </div>
  );
};