import React from 'react';
import ReactECharts from 'echarts-for-react';
import { Detection } from '../../../models/types';

interface ConfidenceHistogramProps {
  detections: Detection[];
}

export const ConfidenceHistogramChart: React.FC<ConfidenceHistogramProps> = ({ detections }) => {
  const bins = ['0-9%', '10-19%', '20-29%', '30-39%', '40-49%', '50-59%', '60-69%', '70-79%', '80-89%', '90-100%'];
  const binCounts = bins.map((_, index) => {
    const min = index / 10;
    const max = index === bins.length - 1 ? 1.01 : (index + 1) / 10;
    return detections.filter((d) => d.confidence >= min && d.confidence < max).length;
  });

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: '#FFFFFF',
      borderColor: '#E2E8F0',
      textStyle: { color: '#0F2043', fontSize: 11, fontFamily: 'monospace' },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '14%',
      top: '12%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: bins,
      axisLine: { lineStyle: { color: '#CBD5E1' } },
      axisLabel: { color: '#64748B', fontSize: 10, fontFamily: 'monospace', rotate: 35 },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#F1F5F9' } },
      axisLabel: { color: '#64748B', fontSize: 10, fontFamily: 'monospace' },
    },
    series: [
      {
        name: 'Confidence Score',
        type: 'bar',
        barWidth: '45%',
        data: binCounts,
        itemStyle: {
          color: (params: any) => {
            if (params.dataIndex === 3) return '#E8AF30';
            if (params.dataIndex === 2) return '#E8C766';
            return '#3361AC';
          },
          borderRadius: [6, 6, 0, 0],
        },
      },
    ],
  };

  return <ReactECharts option={option} style={{ height: '240px', width: '100%' }} />;
};
