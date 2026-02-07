import React from 'react';

interface AnswerDisplayProps {
  answer: string;
}

export const AnswerDisplay: React.FC<AnswerDisplayProps> = ({ answer }) => {
  return (
    <div className="results-section">
      <h2 className="changes-header">Agent Response</h2>
      <div className="answer-card">
        <p className="answer-text">{answer}</p>
      </div>
    </div>
  );
};
