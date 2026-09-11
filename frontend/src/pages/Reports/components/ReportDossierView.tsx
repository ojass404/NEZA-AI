import React from 'react';
import { Report, Detection, SonarScan } from '../../../models/types';
import { PriorityBadge, VerificationBadge, DemoBadge } from '../../../components/common/Badges';
import {
  FileText,
  Download,
  Printer,
  X,
  AlertTriangle,
  Calendar,
} from 'lucide-react';

interface ReportDossierViewProps {
  report: Report;
  scan: SonarScan;
  detections: Detection[];
  onClose: () => void;
  onDownload: () => void;
}

export const ReportDossierView: React.FC<ReportDossierViewProps> = ({
  report,
  scan,
  detections,
  onClose,
  onDownload,
}) => {
  const handlePrint = () => {
    window.print();
  };

  const highPriorityDetections = detections.filter((d) => d.priority === 'HIGH');

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs overflow-y-auto animate-fade-in">
      <div className="bg-[#161616] border border-white/10 rounded-2xl max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl text-white relative">
        <div className="h-14 bg-[#111] border-b border-white/8 px-6 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-white/50" />
            <span className="font-mono text-xs font-bold text-white/70">
              DOSSIER {report.id}
            </span>
            <DemoBadge text="OFFICIAL NIOT / MoES FORMAT" />
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handlePrint}
              className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 text-white/60 text-xs font-mono font-semibold flex items-center gap-1.5 transition-colors"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>Print</span>
            </button>
            <button
              onClick={onDownload}
              className="px-3.5 py-1.5 rounded-xl bg-white hover:bg-white/90 text-black text-xs font-mono font-extrabold flex items-center gap-1.5 transition-all"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download Export</span>
            </button>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-white/30 hover:text-white hover:bg-white/8 transition-colors ml-2"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="p-8 overflow-y-auto space-y-6 font-sans">
          <div className="border-b border-white/10 pb-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="text-[11px] font-mono text-white/40 font-bold tracking-wider uppercase">
                {report.organization} • {report.department}
              </div>
              <h2 className="text-xl font-extrabold text-white mt-1 tracking-tight">
                {report.title}
              </h2>
              <div className="flex items-center gap-3 text-xs font-mono text-white/35 mt-1">
                <span className="flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5" /> {report.generatedAt}
                </span>
                <span>•</span>
                <span>Auditor: {report.generatedBy}</span>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-white/5 border border-white/10 text-right font-mono text-xs shrink-0">
              <div className="text-white/30 text-[10px] uppercase">Survey Reference</div>
              <div className="text-white font-bold">{scan.id}</div>
              <div className="text-white/40 text-[11px]">{scan.instrument}</div>
            </div>
          </div>

          <div className="p-4 bg-white/4 border border-white/10 rounded-xl space-y-1.5">
            <h4 className="text-xs font-mono font-bold text-white/60 uppercase">
              Executive Hydrographic Summary
            </h4>
            <p className="text-xs text-white/50 leading-relaxed">
              {report.executiveSummary}
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
            <div className="p-3 bg-white/4 border border-white/10 rounded-xl">
              <span className="text-[10px] text-white/35 uppercase block">Total Anomalies</span>
              <span className="text-lg font-bold text-white">{detections.length}</span>
            </div>
            <div className="p-3 bg-white/4 border border-white/10 rounded-xl">
              <span className="text-[10px] text-white/35 uppercase block font-semibold">High Priority</span>
              <span className="text-lg font-bold text-white">{highPriorityDetections.length}</span>
            </div>
            <div className="p-3 bg-white/4 border border-white/10 rounded-xl">
              <span className="text-[10px] text-white/35 uppercase block font-semibold">Verified</span>
              <span className="text-lg font-bold text-white">
                {detections.filter((d) => d.verificationStatus === 'VERIFIED').length}
              </span>
            </div>
            <div className="p-3 bg-white/4 border border-white/10 rounded-xl">
              <span className="text-[10px] text-white/35 uppercase block font-semibold">Pending Audit</span>
              <span className="text-lg font-bold text-white">
                {detections.filter((d) => d.verificationStatus === 'PENDING').length}
              </span>
            </div>
          </div>

          {highPriorityDetections.length > 0 && (
            <div className="space-y-3">
              <h4 className="text-xs font-mono font-bold text-white/60 uppercase flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4 text-white/40" />
                Critical Hazards Requiring Immediate Maritime Response
              </h4>
              <div className="space-y-2">
                {highPriorityDetections.map((det) => (
                  <div
                    key={det.id}
                    className="p-3.5 bg-white/4 border border-white/10 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-white">{det.id}</span>
                        <span className="font-semibold text-white/60">{det.classification}</span>
                        <PriorityBadge priority={det.priority} />
                      </div>
                      <div className="text-[11px] font-mono text-white/40 mt-1">
                        Dimensions: {det.dimensions.length}m × {det.dimensions.width}m × {det.dimensions.height}m (Area: {det.estimatedArea} m²)
                      </div>
                    </div>
                    <div className="text-right font-mono text-[11px]">
                      <div className="text-white/40">
                        {det.latitude?.toFixed(4)}°N, {det.longitude?.toFixed(4)}°E
                      </div>
                      <div className="mt-1">
                        <VerificationBadge status={det.verificationStatus} />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="space-y-2">
            <h4 className="text-xs font-mono font-bold text-white/60 uppercase">
              Complete Hydrographic Target Inventory
            </h4>
            <div className="overflow-x-auto border border-white/8 rounded-xl">
              <table className="w-full text-left text-xs">
                <thead className="bg-white/4 border-b border-white/8 text-[10px] font-mono uppercase text-white/35">
                  <tr>
                    <th className="p-2.5">ID</th>
                    <th className="p-2.5">Classification</th>
                    <th className="p-2.5">Confidence</th>
                    <th className="p-2.5">Priority</th>
                    <th className="p-2.5">Coordinates (Demo)</th>
                    <th className="p-2.5">Verification</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 font-mono text-[11px]">
                  {detections.map((det) => (
                    <tr key={det.id} className="hover:bg-white/3 transition-colors">
                      <td className="p-2.5 font-bold text-white/70">{det.id}</td>
                      <td className="p-2.5 font-sans font-medium text-white/60">{det.classification}</td>
                      <td className="p-2.5 text-white/50">{Math.round(det.confidence * 100)}%</td>
                      <td className="p-2.5"><PriorityBadge priority={det.priority} showIcon={false} /></td>
                      <td className="p-2.5 text-white/40">{det.latitude?.toFixed(4)}°N, {det.longitude?.toFixed(4)}°E</td>
                      <td className="p-2.5"><VerificationBadge status={det.verificationStatus} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
