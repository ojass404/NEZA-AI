import React from 'react';
import { useAppState } from '../../../context/AppStateContext';
import ReactECharts from 'echarts-for-react';

export const DashboardActivityChart: React.FC = () => {
  const {detections} = useAppState();
  const days = [...new Set(detections.map(d => d.timestamp.slice(0, 10)))].sort();
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1e1e1e',
      borderColor: 'rgba(255,255,255,0.1)',
      textStyle: { color: 'rgba(255,255,255,0.8)', fontSize: 11, fontFamily: 'monospace' },
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
      boundaryGap: false,
      data: days,
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
      axisLabel: { color: 'rgba(255,255,255,0.35)', fontSize: 10, fontFamily: 'monospace' },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } },
      axisLabel: { color: 'rgba(255,255,255,0.35)', fontSize: 10, fontFamily: 'monospace' },
    },
    series: [
      {
        name: 'AI Detections',
        type: 'line',
        smooth: true,
        data: days.map(day => detections.filter(d => d.timestamp.startsWith(day)).length),
        lineStyle: { color: 'rgba(255,255,255,0.9)', width: 2.5 },
        itemStyle: { color: '#ffffff' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(255, 255, 255, 0.15)' },
              { offset: 1, color: 'rgba(255, 255, 255, 0.0)' },
            ],
          },
        },
      },
      {
        name: 'High Priority',
        type: 'line',
        smooth: true,
        data: days.map(day => detections.filter(d => d.timestamp.startsWith(day) && d.priority === 'HIGH').length),
        lineStyle: { color: 'rgba(255,255,255,0.35)', width: 2, type: 'dashed' },
        itemStyle: { color: 'rgba(255,255,255,0.35)' },
      },
    ],
  };

  return <ReactECharts option={option} style={{ height: '220px', width: '100%' }} />;
};
