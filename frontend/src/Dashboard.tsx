import { useEffect, useRef, useState } from 'react';
import { createChart, type IChartApi } from 'lightweight-charts';

interface Signal {
  asset: string;
  entry: number;
  stop_loss: number;
  take_profit_1: number;
  direction: string;
}

const Dashboard = () => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const [signals, setSignals] = useState<Signal[]>([]);
  const [activeAsset, setActiveAsset] = useState<string>('BTC/USD');

  useEffect(() => {
    fetch('http://localhost:4000/api/signals')
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
      grid: { vertLines: { color: '#1E293B' }, horzLines: { color: '#1E293B' } },
    });
    chartRef.current = chart;
    const candleSeries = (chart as any).addCandlestickSeries();
    
    candleSeries.setData([
      { time: '2023-09-01', open: 25000, high: 26000, low: 24000, close: 25500 },
      { time: '2023-09-02', open: 25500, high: 27000, low: 25000, close: 26500 },
    ]);

    const smaSeries = (chart as any).addLineSeries({ color: '#006a61', lineWidth: 1 });
    smaSeries.setData([
      { time: '2023-09-01', value: 25000 },
      { time: '2023-09-02', value: 25500 },
    ]);

    return () => chart.remove();
  }, [activeAsset]);

  return (
    <div style={{ backgroundColor: '#0F172A', color: 'white', minHeight: '100vh', display: 'flex', flexDirection: 'column', fontFamily: 'sans-serif' }}>
      <header style={{ padding: '15px 20px', borderBottom: '1px solid #1E293B', display: 'flex', justifyContent: 'space-between' }}>
        <h1 style={{ color: '#006a61', fontSize: '24px', fontWeight: 'bold' }}>QUANT ANALYST PRO</h1>
        <div style={{ color: '#94A3B8' }}>Asset: <strong style={{ color: 'white' }}>{activeAsset}</strong></div>
      </header>
      <div style={{ display: 'flex', flex: 1 }}>
        <div style={{ flex: 1, padding: '20px' }}>
          <div ref={chartContainerRef} style={{ border: '1px solid #1E293B', borderRadius: '8px', overflow: 'hidden' }} />
          
          <div style={{ marginTop: '20px', backgroundColor: '#1E293B', padding: '15px', borderRadius: '8px' }}>
            <h3 style={{ margin: '0 0 10px 0', fontSize: '14px', color: '#94A3B8' }}>Live Signals Feed</h3>
            {signals.length === 0 ? <p style={{ fontSize: '12px', color: '#64748B' }}>In attesa di segnali dall'agente...</p> : 
              signals.map((s, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #0F172A' }}>
                  <span>{s.asset}</span>
                  <span style={{ color: s.direction === 'LONG' ? '#26a69a' : '#ef5350' }}>{s.direction}</span>
                  <span>Entry: {s.entry}</span>
                </div>
              ))
            }
          </div>
        </div>
        <div style={{ width: '250px', borderLeft: '1px solid #1E293B', padding: '20px' }}>
          <h3 style={{ color: '#94A3B8', fontSize: '14px', marginBottom: '15px' }}>Watchlist</h3>
          {['BTC/USD', 'ETH/USD', 'SOL/USD'].map(a => (
            <div key={a} onClick={() => setActiveAsset(a)} style={{ 
              padding: '12px', 
              background: activeAsset === a ? '#006a61' : '#1E293B', 
              marginBottom: '8px', 
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
              transition: 'background 0.2s'
            }}>{a}</div>
          ))}
        </div>
      </div>
    </div>
  );
};
export default Dashboard;
