import React, { useState } from 'react';
import { askAgent } from './utils/api.ts';
import { TextInput } from './components/TextInput';
import { LoadingSpinner } from './components/LoadingSpinner';
import { AnswerDisplay } from './components/AnswerDisplay';
import './styles/global.css';

export default function MenuAnalyzer() {
  const [menuText, setMenuText] = useState<string>('');
  const [analyzing, setAnalyzing] = useState<boolean>(false);
  const [answer, setAnswer] = useState<string>('');
  const [error, setError] = useState<string>('');

  const handleAnalyze = async (): Promise<void> => {
    if (!menuText.trim()) return;
    
    try {
      setAnalyzing(true);
      setError('');
      const response = await askAgent(menuText.trim());
      setAnswer(response);
    } catch (error) {
      console.error('Analysis failed:', error);
      setError('Analysis failed. Please try again.');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="menu-analyzer">
      <header>
        <h1>Menu Engineer</h1>
        <p className="subtitle">AI-powered menu optimization for maximum profitability</p>
      </header>

      <TextInput
        value={menuText}
        onChange={setMenuText}
        onAnalyze={handleAnalyze}
        analyzing={analyzing}
      />

      {analyzing && <LoadingSpinner />}

      {error && !analyzing && <div className="error-banner">{error}</div>}

      {answer && !analyzing && <AnswerDisplay answer={answer} />}
    </div>
  );
}