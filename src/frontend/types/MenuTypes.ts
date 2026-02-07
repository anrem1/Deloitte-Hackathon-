export type ChangeCategory = 'pricing' | 'wording' | 'removal' | 'addition';
export type ImpactLevel = 'high' | 'medium' | 'low';

export interface MenuChange {
  id: number;
  category: ChangeCategory;
  itemName: string;
  currentValue: string;
  suggestedValue: string;
  reasoning: string;
  impact: ImpactLevel;
  expectedLift: string;
}

export interface AnalysisResults {
  summary: {
    totalItems: number;
    itemsNeedingChange: number;
    potentialRevenueIncrease: number;
    confidenceScore: number;
  };
  changes: MenuChange[];
}