import React from 'react';
import ReactECharts from 'echarts-for-react';

export const DashboardActivityChart: React.FC = () => {
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
      data: ['04 Sep', '05 Sep', '06 Sep', '07 Sep', '08 Sep', '09 Sep', '10 Sep'],
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
        data: [12, 19, 15, 27, 22, 31, 24],
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
        data: [2, 4, 3, 6, 5, 8, 5],
        lineStyle: { color: 'rgba(255,255,255,0.35)', width: 2, type: 'dashed' },
        itemStyle: { color: 'rgba(255,255,255,0.35)' },
      },
    ],
  };

  return <ReactECharts option={option} style={{ height: '220px', width: '100%' }} />;
};
