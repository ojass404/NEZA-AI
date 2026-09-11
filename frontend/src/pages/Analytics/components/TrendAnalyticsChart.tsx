import React from 'react';
import ReactECharts from 'echarts-for-react';

interface TrendAnalyticsChartProps {
  timeRange: string;
}

export const TrendAnalyticsChart: React.FC<TrendAnalyticsChartProps> = ({ timeRange }) => {
  const days = ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7', 'Day 8', 'Day 9', 'Day 10'];
  const values = [8, 14, 11, 22, 18, 27, 21, 33, 29, 38];

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
        name: '7-Day Rolling Avg',
        type: 'line',
        smooth: true,
        data: [7, 10, 11, 14, 16, 19, 21, 25, 27, 30],
        lineStyle: { color: '#E8AF30', width: 2.5 },
        itemStyle: { color: '#E8AF30' },
      },
    ],
  };

  return <ReactECharts option={option} style={{ height: '260px', width: '100%' }} />;
};
