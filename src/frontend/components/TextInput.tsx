import React from 'react';
import { MessageSquare } from 'lucide-react';

interface TextInputProps {
  value: string;
  onChange: (value: string) => void;
  onAnalyze: () => void;
  analyzing: boolean;
}

export const TextInput: React.FC<TextInputProps> = ({
  value,
  onChange,
  onAnalyze,
  analyzing
}) => {
  return (
    <div className="upload-section">
      <div className="text-input">
        <div className="text-input-header">
          <MessageSquare className="text-input-icon" />
          <div>
            <p className="upload-text">Paste your menu text</p>
            <p className="upload-hint">Provide menu items, prices, and descriptions for analysis</p>
          </div>
        </div>

        <textarea
          className="menu-textarea"
          placeholder="Example: Margherita Pizza - $12.99 - Fresh mozzarella, basil, tomato..."
          value={value}
          onChange={(event) => onChange(event.target.value)}
          rows={10}
        />

        <div className="text-input-actions">
          <button
            className="analyze-btn"
            onClick={onAnalyze}
            disabled={analyzing || !value.trim()}
          >
            {analyzing ? 'Analyzing...' : 'Analyze Menu'}
          </button>
        </div>
      </div>
    </div>
  );
};
