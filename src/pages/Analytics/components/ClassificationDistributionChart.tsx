import React from 'react';
import ReactECharts from 'echarts-for-react';
import { Detection } from '../../../models/types';

interface ClassificationChartProps {
  detections: Detection[];
}

export const ClassificationDistributionChart: React.FC<ClassificationChartProps> = ({ detections }) => {
  const categories = [
    'Ghost Net / Fishing Gear',
    'Metal Debris / Scrap',
    'Pipe / Cable',
    'Container / Cargo',
    'Tire / Rubber',
    'Unknown Anomaly',
  ];

  const counts = categories.map((cat) => {
    return detections.filter((d) => d.classification.toLowerCase().includes(cat.split('/')[0].trim().toLowerCase())).length;
  });

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: '#FFFFFF',
      borderColor: '#E2E8F0',
      textStyle: { color: '#0F2043', fontSize: 11, fontFamily: 'monospace' },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '6%',
      top: '6%',
      containLabel: true,
    },
    xAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#F1F5F9' } },
      axisLabel: { color: '#64748B', fontSize: 10, fontFamily: 'monospace' },
    },
    yAxis: {
      type: 'category',
      data: categories,
      axisLine: { lineStyle: { color: '#CBD5E1' } },
      axisLabel: { color: '#475569', fontSize: 10 },
    },
    series: [
      {
        name: 'Detections Found',
        type: 'bar',
        data: counts,
        itemStyle: {
          color: '#3361AC',
          borderRadius: [0, 6, 6, 0],
        },
        emphasis: {
          itemStyle: { color: '#E8AF30' },
        },
      },
    ],
  };

  return <ReactECharts option={option} style={{ height: '260px', width: '100%' }} />;
};
