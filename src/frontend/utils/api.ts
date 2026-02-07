import { AnalysisResults } from '../types/MenuTypes';

export const analyzeMenuFile = async (file: File): Promise<AnalysisResults> => {
  // TODO: Replace with actual API call to Python backend
  // const formData = new FormData();
  // formData.append('menu', file);
  // 
  // const response = await fetch('BACKEND_URL/analyze', {
  //   method: 'POST',
  //   body: formData
  // });
  // 
  // if (!response.ok) {
  //   throw new Error('Analysis failed');
  // }
  // 
  // return response.json();

  // Mock API call with delay
  await new Promise(resolve => setTimeout(resolve, 2500));

  // Mock response data
  return {
    summary: {
      totalItems: 47,
      itemsNeedingChange: 12,
      potentialRevenueIncrease: 2840,
      confidenceScore: 87
    },
    changes: [
      {
        id: 1,
        category: 'pricing',
        itemName: 'Margherita Pizza',
        currentValue: '$12.99',
        suggestedValue: '$14.99',
        reasoning: 'Below market average by 18%. Competitor analysis shows pricing power.',
        impact: 'high',
        expectedLift: '+$420/month'
      },
      {
        id: 2,
        category: 'wording',
        itemName: 'Chicken Sandwich',
        currentValue: 'Grilled chicken breast',
        suggestedValue: 'Heritage-raised chicken breast, wood-grilled',
        reasoning: 'Premium descriptors increase perceived value and justify pricing.',
        impact: 'medium',
        expectedLift: '+$180/month'
      },
      {
        id: 3,
        category: 'pricing',
        itemName: 'Caesar Salad',
        currentValue: '$9.50',
        suggestedValue: '$8.95',
        reasoning: 'Overpriced compared to portion size. Reduce to increase volume.',
        impact: 'medium',
        expectedLift: '+$215/month'
      },
      {
        id: 4,
        category: 'removal',
        itemName: 'Tuna Melt',
        currentValue: 'Active menu item',
        suggestedValue: 'Remove from menu',
        reasoning: 'Low sales velocity, high food cost percentage (42%). Consider as special.',
        impact: 'low',
        expectedLift: '+$95/month savings'
      },
      {
        id: 5,
        category: 'wording',
        itemName: 'Chocolate Cake',
        currentValue: 'Rich chocolate cake',
        suggestedValue: 'Belgian dark chocolate torte with espresso glaze',
        reasoning: 'Elevate dessert language to match premium positioning.',
        impact: 'high',
        expectedLift: '+$340/month'
      },
      {
        id: 6,
        category: 'pricing',
        itemName: 'House Burger',
        currentValue: '$13.50',
        suggestedValue: '$15.95',
        reasoning: 'Flagship item underpriced. Customer willingness-to-pay analysis supports increase.',
        impact: 'high',
        expectedLift: '+$580/month'
      },
      {
        id: 7,
        category: 'addition',
        itemName: 'Truffle Fries',
        currentValue: 'Not on menu',
        suggestedValue: 'Add as premium side - $8.95',
        reasoning: 'High-margin add-on. Trending item with low complexity.',
        impact: 'medium',
        expectedLift: '+$410/month'
      },
      {
        id: 8,
        category: 'wording',
        itemName: 'Steak',
        currentValue: '8oz ribeye steak',
        suggestedValue: '8oz prime ribeye, dry-aged 21 days, charcoal-grilled',
        reasoning: 'Justify premium price point with craft descriptors.',
        impact: 'high',
        expectedLift: '+$520/month'
      }
    ]
  };
};