import React, { useState, useRef } from 'react';
import { Upload, FileCode, CheckCircle2, Play, RefreshCw } from 'lucide-react';
import { DemoBadge } from '../../../components/common/Badges';

interface UploadZoneProps {
  onStartAnalysis: (file: File) => void;
  isProcessing: boolean;
}

export const UploadZone: React.FC<UploadZoneProps> = ({ onStartAnalysis, isProcessing }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setSelectedFile(file);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
    }
  };

  return (
    <div className="bg-[#161616] border border-white/8 rounded-2xl p-6 space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            Upload Side-Scan Sonar Data
            <DemoBadge text="SUPPORTED: PNG / JPEG / TIFF" />
          </h2>
          <p className="text-xs text-white/40 mt-0.5">
            Select or drag hydrographic survey acoustic files to initiate automated AI anomaly detection.
          </p>
        </div>


      </div>

      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-7 text-center cursor-pointer transition-all duration-200 ${
          isDragging
            ? 'border-white/40 bg-white/5'
            : 'border-white/10 bg-white/3 hover:border-white/25 hover:bg-white/5'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".png,.jpg,.jpeg,.tiff,.tif"
          onChange={handleFileChange}
          className="hidden"
        />

        <div className="w-12 h-12 mx-auto rounded-full bg-white/8 border border-white/10 text-white/50 flex items-center justify-center mb-3">
          <Upload className="w-6 h-6" />
        </div>

        <h3 className="text-sm font-bold text-white mb-1">
          Drop sonar data here
        </h3>
        <p className="text-xs text-white/40 mb-3">
          or <span className="text-white font-semibold underline">browse files</span> from your local workstation
        </p>

        <div className="flex flex-wrap justify-center gap-2 text-[10px] font-mono text-white/40">
          <span className="px-2 py-0.5 rounded bg-white/5 border border-white/10">TIFF</span>
          <span className="px-2 py-0.5 rounded bg-white/5 border border-white/10">JPEG</span>
          <span className="px-2 py-0.5 rounded bg-white/5 border border-white/10">PNG</span>
          <span className="px-2 py-0.5 rounded bg-white/5 border border-white/10">PNG / JPG</span>
        </div>
      </div>

      {selectedFile && (
        <div className="p-4 bg-white/4 border border-white/10 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 animate-fade-in">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-white/8 text-white/60">
              <FileCode className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-bold text-white truncate max-w-xs sm:max-w-md">
                  {selectedFile.name}
                </span>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-white/10 text-white/60 border border-white/10 flex items-center gap-1 font-semibold">
                  <CheckCircle2 className="w-2.5 h-2.5" /> Ready
                </span>
              </div>
              <div className="flex items-center gap-3 text-[11px] font-mono text-white/35 mt-0.5">
                <span>{(selectedFile.size / (1024 * 1024)).toFixed(1)} MB</span>
                <span>•</span>
                <span>{selectedFile.type}</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 self-end sm:self-auto">
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                setSelectedFile(null);
              }}
              disabled={isProcessing}
              className="px-3 py-1.5 rounded-lg text-xs font-mono text-white/50 hover:bg-white/8 border border-white/10 transition-colors"
            >
              Remove
            </button>
            <button
              type="button"
              onClick={() => onStartAnalysis(selectedFile)}
              disabled={isProcessing}
              className="px-4 py-2 rounded-xl bg-white hover:bg-white/90 text-black text-xs font-extrabold font-mono flex items-center gap-1.5 transition-all"
            >
              {isProcessing ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>Start AI Analysis</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
