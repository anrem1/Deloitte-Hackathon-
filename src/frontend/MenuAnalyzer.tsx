import React, { useState } from 'react';
import { AnalysisResults } from './types/MenuTypes';
import { analyzeMenuFile } from './utils/api.ts';
import { FileUpload } from './components/FileUpload';
import { LoadingSpinner } from './components/LoadingSpinner';
import { ResultsDisplay } from './components/ResultsDisplay';
import './styles/global.css';

export default function MenuAnalyzer() {
  const [file, setFile] = useState<File | null>(null);
  const [analyzing, setAnalyzing] = useState<boolean>(false);
  const [results, setResults] = useState<AnalysisResults | null>(null);

  const handleFileSelect = (selectedFile: File): void => {
    setFile(selectedFile);
    setResults(null);
  };

  const handleAnalyze = async (): Promise<void> => {
    if (!file) return;
    
    try {
      setAnalyzing(true);
      const analysisResults = await analyzeMenuFile(file);
      setResults(analysisResults);
    } catch (error) {
      console.error('Analysis failed:', error);
      // TODO: Add error handling UI
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

      <FileUpload 
        file={file}
        onFileSelect={handleFileSelect}
        onAnalyze={handleAnalyze}
        analyzing={analyzing}
      />

      {analyzing && <LoadingSpinner />}

      {results && !analyzing && <ResultsDisplay results={results} />}
    </div>
  );
}