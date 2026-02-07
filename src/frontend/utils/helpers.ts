import { ChangeCategory, ImpactLevel } from '../types/MenuTypes';
import { DollarSign, FileText, X, Zap, AlertCircle, LucideIcon } from 'lucide-react';

export const getCategoryIcon = (category: ChangeCategory): LucideIcon => {
  const iconMap: Record<ChangeCategory, LucideIcon> = {
    pricing: DollarSign,
    wording: FileText,
    removal: X,
    addition: Zap,
  };
  
  return iconMap[category] || AlertCircle;
};

export const getImpactClass = (impact: ImpactLevel): string => {
  const classMap: Record<ImpactLevel, string> = {
    high: 'impact-high',
    medium: 'impact-medium',
    low: 'impact-low',
  };
  
  return classMap[impact] || '';
};