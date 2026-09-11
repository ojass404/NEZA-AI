import React from 'react';
import ReactECharts from 'echarts-for-react';
import { Detection } from '../../../models/types';

interface VerificationDonutProps {
  detections: Detection[];
}

export const VerificationDonutChart: React.FC<VerificationDonutProps> = ({ detections }) => {
  const verified = detections.filter((d) => d.verificationStatus === 'CONFIRMED').length;
  const rejected = detections.filter((d) => d.verificationStatus === 'REJECTED').length;
  const pending = detections.filter((d) => d.verificationStatus === 'PENDING').length;

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: '#FFFFFF',
      borderColor: '#E2E8F0',
      textStyle: { color: '#0F2043', fontSize: 11, fontFamily: 'monospace' },
      formatter: '{b}: {c} ({d}%)',
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
      textStyle: { color: '#475569', fontSize: 11 },
      itemWidth: 12,
      itemHeight: 12,
    },
    series: [
      {
        name: 'Verification Ratio',
        type: 'pie',
        radius: ['50%', '75%'],
        center: ['40%', '50%'],
        avoidLabelOverlap: false,
        label: { show: false },
        data: [
          { value: verified, name: 'Verified', itemStyle: { color: '#16A34A' } },
          { value: pending, name: 'Pending Review', itemStyle: { color: '#E8AF30' } },
          { value: rejected, name: 'Rejected', itemStyle: { color: '#DC2626' } },
        ],
      },
    ],
  };

  return <ReactECharts option={option} style={{ height: '240px', width: '100%' }} />;
};
