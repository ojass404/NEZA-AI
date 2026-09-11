import React from 'react';
import ReactECharts from 'echarts-for-react';
import { Detection } from '../../../models/types';

interface PriorityBreakdownProps {
  detections: Detection[];
}

export const PriorityBreakdownChart: React.FC<PriorityBreakdownProps> = ({ detections }) => {
  const high = detections.filter((d) => d.priority === 'HIGH').length;
  const medium = detections.filter((d) => d.priority === 'MEDIUM').length;
  const low = detections.filter((d) => d.priority === 'LOW').length;

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
      data: ['HIGH', 'MEDIUM', 'LOW'],
      axisLine: { lineStyle: { color: '#CBD5E1' } },
      axisLabel: { color: '#64748B', fontSize: 11, fontFamily: 'monospace' },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#F1F5F9' } },
      axisLabel: { color: '#64748B', fontSize: 10, fontFamily: 'monospace' },
    },
    series: [
      {
        name: 'Priority Severity',
        type: 'bar',
        barWidth: '40%',
        data: [
          { value: high, itemStyle: { color: '#E8AF30', borderRadius: [6, 6, 0, 0] } },
          { value: medium, itemStyle: { color: '#E8C766', borderRadius: [6, 6, 0, 0] } },
          { value: low, itemStyle: { color: '#3361AC', borderRadius: [6, 6, 0, 0] } },
        ],
      },
    ],
  };

  return <ReactECharts option={option} style={{ height: '240px', width: '100%' }} />;
};
