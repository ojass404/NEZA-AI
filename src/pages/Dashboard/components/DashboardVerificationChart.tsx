import React from 'react';
import ReactECharts from 'echarts-for-react';
import { useAppState } from '../../../context/AppStateContext';

export const DashboardVerificationChart: React.FC = () => {
  const { detections } = useAppState();

  const verified = detections.filter((d) => d.verificationStatus === 'VERIFIED').length;
  const rejected = detections.filter((d) => d.verificationStatus === 'REJECTED').length;
  const pending = detections.filter((d) => d.verificationStatus === 'PENDING').length;

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: '#1e1e1e',
      borderColor: 'rgba(255,255,255,0.1)',
      textStyle: { color: 'rgba(255,255,255,0.8)', fontSize: 11, fontFamily: 'monospace' },
      formatter: '{b}: {c} ({d}%)',
    },
    legend: {
      bottom: '0%',
      left: 'center',
      itemWidth: 10,
      itemHeight: 10,
      textStyle: { color: 'rgba(255,255,255,0.45)', fontSize: 11 },
    },
    series: [
      {
        name: 'Verification Status',
        type: 'pie',
        radius: ['55%', '80%'],
        center: ['50%', '42%'],
        avoidLabelOverlap: false,
        label: { show: false },
        data: [
          { value: verified, name: 'Verified', itemStyle: { color: '#16A34A' } },
          { value: pending, name: 'Pending', itemStyle: { color: '#E8AF30' } },
          { value: rejected, name: 'Rejected', itemStyle: { color: '#DC2626' } },
        ],
      },
    ],
  };

  return <ReactECharts option={option} style={{ height: '220px', width: '100%' }} />;
};
