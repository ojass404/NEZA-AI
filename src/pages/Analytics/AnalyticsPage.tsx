import React from 'react';
import { useAppState } from '../../context/AppStateContext';
import { StatCard } from '../../components/common/StatCard';
import { DemoBadge } from '../../components/common/Badges';
import { TrendAnalyticsChart } from './components/TrendAnalyticsChart';
import { ClassificationDistributionChart } from './components/ClassificationDistributionChart';
import { ConfidenceHistogramChart } from './components/ConfidenceHistogramChart';
import { VerificationDonutChart } from './components/VerificationDonutChart';
import { PriorityBreakdownChart } from './components/PriorityBreakdownChart';
import { Target, AlertTriangle, CheckCircle2, XCircle, Clock, Filter } from 'lucide-react';

export const AnalyticsPage: React.FC = () => {
  const { detections, scans, analyticsFilters, setAnalyticsFilters } = useAppState();

  const filteredDetections = detections.filter((det) => {
    if (analyticsFilters.survey !== 'ALL' && det.scanId !== analyticsFilters.survey) return false;
    if (analyticsFilters.priority !== 'ALL' && det.priority !== analyticsFilters.priority) return false;
    if (analyticsFilters.classification !== 'ALL' && !det.classification.includes(analyticsFilters.classification)) return false;
    return true;
  });

  const totalDetections = filteredDetections.length;
  const highPriority = filteredDetections.filter((d) => d.priority === 'HIGH').length;
  const verified = filteredDetections.filter((d) => d.verificationStatus === 'VERIFIED').length;
  const rejected = filteredDetections.filter((d) => d.verificationStatus === 'REJECTED').length;
  const pending = filteredDetections.filter((d) => d.verificationStatus === 'PENDING').length;

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-white/10">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl md:text-2xl font-extrabold text-white tracking-tight">
              Survey Analytics
            </h1>

          </div>
          <p className="text-xs md:text-sm text-white/40 mt-0.5">
            Detection trends, confidence distributions, and human validation metrics.
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-[#161616] border border-white/8 rounded-xl p-3.5 flex flex-wrap items-center gap-3 text-xs font-mono">
        <div className="flex items-center gap-1.5 text-white/60 font-bold">
          <Filter className="w-3.5 h-3.5" />
          <span>FILTERS:</span>
        </div>

        <select
          value={analyticsFilters.survey}
          onChange={(e) => setAnalyticsFilters((prev) => ({ ...prev, survey: e.target.value }))}
          className="bg-[#1e1e1e] border border-white/10 rounded-lg px-2.5 py-1 text-white/70 font-semibold focus:outline-hidden focus:border-white/20"
        >
          <option value="ALL">All Surveys</option>
          {scans.map((s) => (
            <option key={s.id} value={s.id}>
              {s.id}: {s.surveyName.substring(0, 24)}...
            </option>
          ))}
        </select>

        <select
          value={analyticsFilters.priority}
          onChange={(e) => setAnalyticsFilters((prev) => ({ ...prev, priority: e.target.value }))}
          className="bg-[#1e1e1e] border border-white/10 rounded-lg px-2.5 py-1 text-white/70 font-semibold focus:outline-hidden focus:border-white/20"
        >
          <option value="ALL">All Priorities</option>
          <option value="HIGH">High Priority</option>
          <option value="MEDIUM">Medium Priority</option>
          <option value="LOW">Low Priority</option>
        </select>

        <button
          onClick={() => setAnalyticsFilters({ survey: 'ALL', priority: 'ALL', classification: 'ALL', timeRange: '30D' })}
          className="ml-auto text-[11px] text-white/40 font-semibold hover:text-white transition-colors"
        >
          Reset Filters
        </button>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3.5">
        <StatCard title="Total Detections" value={totalDetections} subtitle="In filter" icon={Target} accentColor="cobalt" />
        <StatCard title="High Priority" value={highPriority} subtitle="Critical hazards" icon={AlertTriangle} accentColor="buttercup" />
        <StatCard title="Verified" value={verified} subtitle="Validated" icon={CheckCircle2} accentColor="gold" />
        <StatCard title="Rejected" value={rejected} subtitle="False alarms" icon={XCircle} accentColor="royal" />
        <StatCard title="Pending" value={pending} subtitle="Awaiting review" icon={Clock} accentColor="buttercup" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-[#161616] border border-white/8 rounded-2xl p-5">
          <h3 className="text-sm font-bold text-white mb-0.5">
            Detection Trend Over Survey Timeline
          </h3>
          <p className="text-xs text-white/30 mb-2">
            Anomalies logged per survey flight.
          </p>
          <TrendAnalyticsChart timeRange={analyticsFilters.timeRange} />
        </div>

        <div className="bg-[#161616] border border-white/8 rounded-2xl p-5">
          <h3 className="text-sm font-bold text-white mb-0.5">
            Classification Taxonomy Breakdown
          </h3>
          <p className="text-xs text-white/30 mb-2">
            Distribution of detected marine debris categories.
          </p>
          <ClassificationDistributionChart detections={filteredDetections} />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-[#161616] border border-white/8 rounded-2xl p-5">
          <h3 className="text-sm font-bold text-white mb-0.5">
            AI Confidence Distribution
          </h3>
          <ConfidenceHistogramChart detections={filteredDetections} />
        </div>

        <div className="bg-[#161616] border border-white/8 rounded-2xl p-5">
          <h3 className="text-sm font-bold text-white mb-0.5">
            Human Verification Audit Ratio
          </h3>
          <VerificationDonutChart detections={filteredDetections} />
        </div>

        <div className="bg-[#161616] border border-white/8 rounded-2xl p-5">
          <h3 className="text-sm font-bold text-white mb-0.5">
            Hazard Priority Severity
          </h3>
          <PriorityBreakdownChart detections={filteredDetections} />
        </div>
      </div>
    </div>
  );
};
