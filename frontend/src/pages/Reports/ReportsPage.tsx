import React, { useState } from 'react';
import { downloadReport } from '../../api/client';
import { useAppState } from '../../context/AppStateContext';
import { Report } from '../../models/types';
import { DemoBadge } from '../../components/common/Badges';
import { ReportDossierView } from './components/ReportDossierView';
import {
  Download,
  Eye,
  Plus,
} from 'lucide-react';

export const ReportsPage: React.FC = () => {
  const { reports, scans, detections, generateReport, addToast } = useAppState();
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [isGenerateModalOpen, setIsGenerateModalOpen] = useState<boolean>(false);
  const [selectedScanForReport, setSelectedScanForReport] = useState<string>('');
  const [reportTitle, setReportTitle] = useState<string>('');

  const handleGenerate = async () => {
    try {
      const report = await generateReport(selectedScanForReport || scans[0]?.id, reportTitle.trim() || undefined);
      setSelectedReport(report); setIsGenerateModalOpen(false);
    } catch (e) { addToast('error', 'Report failed', (e as Error).message); }
  };
  const handleDownloadDemo = async (report: Report) => {
    try { await downloadReport(report.scanId, 'json'); }
    catch (e) { addToast('error', 'Export failed', (e as Error).message); }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-white/10">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl md:text-2xl font-extrabold text-white tracking-tight">
              Operational Anomaly Reports
            </h1>

          </div>

        </div>

        <button
          disabled={!scans.length} onClick={() => { setSelectedScanForReport(scans[0]?.id || ''); setIsGenerateModalOpen(true); }}
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-white text-black font-extrabold text-xs font-mono transition-all hover:bg-white/90 shadow-md self-start sm:self-auto"
        >
          <Plus className="w-4 h-4 stroke-[2.5]" />
          <span>Generate New Report</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {reports.map((rpt) => {
          const scan = scans.find((s) => s.id === rpt.scanId) || scans[0];
          const scanDets = detections.filter((d) => d.scanId === rpt.scanId);

          return (
            <div
              key={rpt.id}
              className="bg-[#161616] border border-white/8 rounded-2xl p-5 flex flex-col justify-between hover:border-white/20 hover:shadow-lg transition-all duration-200 hover:-translate-y-0.5"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono text-xs font-bold text-white/60">
                    {rpt.id}
                  </span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                    {rpt.status}
                  </span>
                </div>

                <h3 className="text-sm font-bold text-white mb-1.5 line-clamp-2">
                  {rpt.title}
                </h3>

                <p className="text-xs text-white/30 line-clamp-2 mb-3">
                  {rpt.executiveSummary}
                </p>

                <div className="p-3 bg-[#1e1e1e] rounded-xl border border-white/8 space-y-1.5 text-xs font-mono mb-4">
                  <div className="flex justify-between text-white/40">
                    <span>Survey:</span>
                    <span className="text-white/70 font-semibold truncate max-w-[150px]">{rpt.surveyName}</span>
                  </div>
                  <div className="flex justify-between text-white/40">
                    <span>Generated:</span>
                    <span className="text-white/60">{rpt.generatedAt.split(' ')[0]}</span>
                  </div>
                  <div className="flex justify-between text-white/40">
                    <span>Detections:</span>
                    <span className="text-white font-bold">{scanDets.length} targets</span>
                  </div>
                </div>
              </div>

              <div className="pt-3 border-t border-white/8 flex items-center gap-2">
                <button
                  onClick={() => setSelectedReport(rpt)}
                  className="flex-1 py-2 px-3 rounded-xl bg-white text-black text-xs font-semibold font-mono flex items-center justify-center gap-1.5 transition-all hover:bg-white/90"
                >
                  <Eye className="w-3.5 h-3.5" />
                  <span>View Dossier</span>
                </button>
                <button
                  onClick={() => handleDownloadDemo(rpt)}
                  className="py-2 px-3 rounded-xl bg-[#1e1e1e] border border-white/10 hover:border-white/20 text-white/60 text-xs font-mono font-semibold flex items-center gap-1.5 transition-colors"
                  title="Download Export File"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>JSON</span>
                </button>
                <button onClick={() => downloadReport(rpt.scanId, 'csv').catch(e => addToast('error', 'Export failed', e.message))}>CSV</button>
                <button onClick={() => downloadReport(rpt.scanId, 'geojson').catch(e => addToast('error', 'Export failed', e.message))}>GeoJSON</button>
              </div>
            </div>
          );
        })}
      </div>

      {selectedReport && (
        <ReportDossierView
          report={selectedReport}
          scan={scans.find((s) => s.id === selectedReport.scanId) || scans[0]}
          detections={detections.filter((d) => d.scanId === selectedReport.scanId)}
          onClose={() => setSelectedReport(null)}
          onDownload={() => handleDownloadDemo(selectedReport)}
        />
      )}

      {isGenerateModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs animate-fade-in">
          <div className="bg-[#161616] border border-white/10 rounded-2xl max-w-md w-full p-6 shadow-2xl text-white space-y-4">
            <h3 className="text-base font-bold text-white font-mono">
              Generate New Operational Report
            </h3>
            <p className="text-xs text-white/40 leading-relaxed">
              Synthesize sonar detections and human verification logs into a NEZA AI review report.
            </p>

            <div className="space-y-3 font-mono text-xs">
              <div>
                <label className="block text-white/50 mb-1 font-semibold">Target Survey:</label>
                <select
                  value={selectedScanForReport}
                  onChange={(e) => setSelectedScanForReport(e.target.value)}
                  className="w-full bg-[#1e1e1e] border border-white/10 rounded-lg p-2 text-white/80 focus:outline-hidden focus:border-white/20"
                >
                  {scans.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.id}: {s.surveyName}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-white/50 mb-1 font-semibold">Dossier Title (Optional):</label>
                <input
                  type="text"
                  placeholder="e.g. Marine Debris Assessment — Southern Transect"
                  value={reportTitle}
                  onChange={(e) => setReportTitle(e.target.value)}
                  className="w-full bg-[#1e1e1e] border border-white/10 rounded-lg p-2 text-white/80 placeholder-white/20 focus:outline-hidden focus:border-white/20"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2.5 pt-3 border-t border-white/8">
              <button
                onClick={() => setIsGenerateModalOpen(false)}
                className="px-3.5 py-1.5 rounded-lg text-xs font-mono text-white/50 hover:bg-white/5 border border-white/10 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleGenerate}
                className="px-4 py-2 rounded-xl bg-white text-black font-extrabold text-xs font-mono"
              >
                Create Report
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
