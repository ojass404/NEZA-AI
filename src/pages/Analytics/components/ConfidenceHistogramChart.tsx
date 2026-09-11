import React from 'react';
import ReactECharts from 'echarts-for-react';
import { Detection } from '../../../models/types';

interface ConfidenceHistogramProps {
  detections: Detection[];
}

export const ConfidenceHistogramChart: React.FC<ConfidenceHistogramProps> = ({ detections }) => {
  const bins = ['60-69%', '70-79%', '80-89%', '90-100%'];
  const binCounts = [
    detections.filter((d) => d.confidence >= 0.6 && d.confidence < 0.7).length,
    detections.filter((d) => d.confidence >= 0.7 && d.confidence < 0.8).length,
    detections.filter((d) => d.confidence >= 0.8 && d.confidence < 0.9).length,
    detections.filter((d) => d.confidence >= 0.9).length,
  ];

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
      bottom: '6%',
      top: '12%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: bins,
      axisLine: { lineStyle: { color: '#CBD5E1' } },
      axisLabel: { color: '#64748B', fontSize: 10, fontFamily: 'monospace' },
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
