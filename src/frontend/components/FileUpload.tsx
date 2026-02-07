import React, { useRef, DragEvent, ChangeEvent } from 'react';
import { Upload, FileText } from 'lucide-react';

interface FileUploadProps {
  file: File | null;
  onFileSelect: (file: File) => void;
  onAnalyze: () => void;
  analyzing: boolean;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  file,
  onFileSelect,
  onAnalyze,
  analyzing
}) => {
  const [dragActive, setDragActive] = React.useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: DragEvent<HTMLDivElement>): void => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>): void => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>): void => {
    if (e.target.files && e.target.files[0]) {
      onFileSelect(e.target.files[0]);
    }
  };

  return (
    <div 
      className={`upload-section ${dragActive ? 'drag-active' : ''}`}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      {!file ? (
        <div 
          className="upload-zone" 
          onClick={() => fileInputRef.current?.click()}
        >
          <Upload className="upload-icon" />
          <p className="upload-text">Drop your menu here or click to upload</p>
          <p className="upload-hint">Supports PDF, DOCX, XLS, CSV, and image files</p>
          <input
            ref={fileInputRef}
            type="file"
            onChange={handleFileChange}
            accept=".pdf,.docx,.doc,.xlsx,.xls,.csv,.png,.jpg,.jpeg"
          />
        </div>
      ) : (
        <div className="file-info">
          <div className="file-details">
            <FileText className="file-icon" />
            <span className="file-name">{file.name}</span>
          </div>
          <button 
            className="analyze-btn" 
            onClick={onAnalyze}
            disabled={analyzing}
          >
            {analyzing ? 'Analyzing...' : 'Analyze Menu'}
          </button>
        </div>
      )}
    </div>
  );
};