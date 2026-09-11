import React from 'react';
import { useAppState } from '../../../context/AppStateContext';
import ReactECharts from 'echarts-for-react';

interface TrendAnalyticsChartProps {
  timeRange: string;
}

export const TrendAnalyticsChart: React.FC<TrendAnalyticsChartProps> = ({ timeRange }) => {
  const {detections} = useAppState();
  const days = [...new Set(detections.map(d => d.timestamp.slice(0, 10)))].sort();
  const values = days.map(day => detections.filter(d => d.timestamp.startsWith(day)).length);

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
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
      data: days,
      axisLine: { lineStyle: { color: '#CBD5E1' } },
      axisLabel: { color: '#64748B', fontSize: 10, fontFamily: 'monospace' },
    },
    yAxis: {
      type: 'value',
      name: 'Anomalies Detected',
      nameTextStyle: { color: '#64748B', fontSize: 10 },
      splitLine: { lineStyle: { color: '#F1F5F9' } },
      axisLabel: { color: '#64748B', fontSize: 10, fontFamily: 'monospace' },
    },
    series: [
      {
        name: 'Detections',
        type: 'bar',
        barWidth: '40%',
        data: values,
        itemStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: '#3361AC' },
              { offset: 1, color: '#162F65' },
            ],
          },
          borderRadius: [4, 4, 0, 0],
        },
      },
      {
        name: 'Rolling average (up to 7 observation days)',
        type: 'line',
        smooth: true,
        data: values.map((_, i) => { const window = values.slice(Math.max(0, i - 6), i + 1); return window.reduce((a, b) => a + b, 0) / window.length; }),
        lineStyle: { color: '#E8AF30', width: 2.5 },
        itemStyle: { color: '#E8AF30' },
      },
    ],
  };

  return <ReactECharts option={option} style={{ height: '260px', width: '100%' }} />;
};
