import { useEffect, useRef, useState } from 'react';
import { createChart } from 'lightweight-charts';

interface Signal {
  asset: string;
  entry: number;
  stop_loss: number;
  take_profit_1: number;
  direction: string;
}

const Dashboard = () => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const [signals, setSignals] = useState<Signal[]>([]);
  const [activeAsset, setActiveAsset] = useState<string>('BTC/USD');

  useEffect(() => {
    fetch('/api/signals')
      .then(res => res.json())
      .then(data => setSignals(data))
      .catch(err => console.error("API Error:", err));
  }, []);

  useEffect(() => {
    if (!chartContainerRef.current) return;
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 450,
      layout: { background: { color: '#0F172A' }, textColor: '#94A3B8' },
    });
    
    const candleSeries = (chart as any).addCandlestickSeries();
    candleSeries.setData([
      { time: '2023-09-01', open: 25000, high: 26000, low: 24000, close: 25500 },
      { time: '2023-09-02', open: 25500, high: 27000, low: 25000, close: 26500 },
    ]);

    return () => chart.remove();
  }, [activeAsset]);

  return (
    <div style={{ backgroundColor: '#0F172A', color: 'white', height: '100vh', width: '100vw', display: 'flex', flexDirection: 'column', fontFamily: 'sans-serif' }}>
      <header style={{ padding: '20px', borderBottom: '1px solid #1E293B' }}>
        <h1 style={{ color: '#006a61', fontSize: '24px', fontWeight: 'bold' }}>QUANT ANALYST PRO</h1>
      </header>
      <div style={{ display: 'flex', flex: 1, padding: '20px' }}>
        <div style={{ flex: 1 }}>
          <div ref={chartContainerRef} />
        </div>
        <div style={{ width: '300px', marginLeft: '20px' }}>
          <h3 style={{ color: '#94A3B8' }}>Segnali</h3>
          {signals.map((s, i) => (
            <div key={i} style={{ background: '#1E293B', padding: '10px', marginBottom: '10px' }}>
              {s.asset}: {s.direction}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
export default Dashboard;
