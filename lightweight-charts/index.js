import { createChart, CandlestickSeries, HistogramSeries, ColorType } from 'lightweight-charts';
import Papa from 'papaparse';

const chartOptions = {
  height: 0.95 * window.innerHeight,
  autoSize: true,
  timeScale: {
    timeVisible: true,
    secondsVisible: false,
    borderColor: '#696969'
  },
  rightPriceScale: {
    borderColor: '#696969',
    scaleMargins: {
      top: 0.05,
      bottom: 0.1
    }
  },
  layout: {
    background: {
      type: ColorType.Solid,
      color: '#FAFAD2'
    },
    textColor: '#696969'
  }
};

const candlestickOptions = {
  upColor: '#32CD32', wickUpColor: '#32CD32', borderUpColor: '#28A028',
  downColor: '#FF6347', wickDownColor: '#FF6347', borderDownColor: '#CC503A',
}

const histogramOptions = {
  priceFormat: {
    type: 'volume',
  },
  priceLineVisible: false,
  color: '#4682B4',
  autoscaleInfoProvider: () => ({
    priceRange: {
      minValue: 0,
      maxValue: 5*10**6,
    },
  })
}

fetch('/SPY_5min_twelvedata.csv')
  .then(response => response.text())
  .then(csvText => {
    const results = Papa.parse(csvText, {
      header: true,
      skipEmptyLines: true
    });
    return results.data;
  })
  .then(data => {
    return data
      .map(row => ({
        // convert %Y-%m-%d %H:%M:%S to unix timestamp
        // https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/UTCTimestamp
        time: Math.floor(new Date(row.timestamp).getTime() / 1000),
        open: parseFloat(row.open),
        high: parseFloat(row.high),
        low: parseFloat(row.low),
        close: parseFloat(row.close),
        volume: parseInt(row.volume)
      }))
      .sort((a, b) => a.time - b.time);
    ;
  })
  .then(parsedData => {
    const chart = createChart(document.body, chartOptions);
    const candlestickSeries = chart.addSeries(CandlestickSeries, candlestickOptions);
    candlestickSeries.setData(parsedData);

    const volumeSeries = chart.addSeries(HistogramSeries, histogramOptions, 1);
    volumeSeries.setData(parsedData.map(d => ({ time: d.time, value: d.volume })));
  });
