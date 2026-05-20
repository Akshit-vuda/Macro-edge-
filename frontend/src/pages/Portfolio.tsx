import React from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'
import { 
  Wallet, 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  RefreshCw,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react'

// Mock data
const holdings = [
  { ticker: 'GLD', weight: 35, pnl: 1250, pnlPct: 3.2 },
  { ticker: 'SLV', weight: 25, pnl: 580, pnlPct: 2.1 },
  { ticker: 'USO', weight: 15, pnl: -320, pnlPct: -1.8 },
  { ticker: 'SPY', weight: 15, pnl: 420, pnlPct: 2.5 },
  { ticker: 'CASH', weight: 10, pnl: 0, pnlPct: 0 },
]

const allocationData = holdings.filter(h => h.ticker !== 'CASH').map(h => ({
  name: h.ticker,
  value: h.weight
}))

const colors = ['#f59e0b', '#94a3b8', '#ef4444', '#3b82f6', '#10b981']

const equityCurve = [
  { date: 'Week 1', value: 100000 },
  { date: 'Week 2', value: 101200 },
  { date: 'Week 3', value: 100800 },
  { date: 'Week 4', value: 102500 },
  { date: 'Week 5', value: 103800 },
  { date: 'Week 6', value: 105200 },
  { date: 'Week 7', value: 104500 },
  { date: 'Week 8', value: 106500 },
  { date: 'Week 9', value: 107200 },
  { date: 'Week 10', value: 108200 },
]

const riskMetrics = {
  sharpe: 1.12,
  maxDrawdown: -2.1,
  volatility: 8.5,
  winRate: 58,
  var95: -1250,
  beta: 0.72
}

const Portfolio = () => {
  return (
    <div className="p-6 space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center gap-2 mb-2">
            <Wallet size={18} className="text-accent-blue" />
            <span className="text-text-secondary text-sm">Total Value</span>
          </div>
          <p className="text-2xl font-bold text-text-primary">$108,200</p>
          <p className="text-sm text-accent-green flex items-center gap-1 mt-1">
            <ArrowUpRight size={14} /> +$8,200 (+8.2%)
          </p>
        </div>

        <div className="card">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp size={18} className="text-accent-green" />
            <span className="text-text-secondary text-sm">Today</span>
          </div>
          <p className="text-2xl font-bold text-text-primary">+$342</p>
          <p className="text-sm text-accent-green flex items-center gap-1 mt-1">
            +0.32%
          </p>
        </div>

        <div className="card">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle size={18} className="text-accent-amber" />
            <span className="text-text-secondary text-sm">Max DD</span>
          </div>
          <p className="text-2xl font-bold text-text-primary">-2.1%</p>
          <p className="text-sm text-text-secondary mt-1">of $108k peak</p>
        </div>

        <div className="card">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp size={18} className="text-accent-green" />
            <span className="text-text-secondary text-sm">Win Rate</span>
          </div>
          <p className="text-2xl font-bold text-text-primary">58%</p>
          <p className="text-sm text-text-secondary mt-1">Last 20 trades</p>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-3 gap-4">
        {/* Allocation Pie */}
        <div className="card">
          <h3 className="text-lg font-semibold text-text-primary mb-4">Allocation</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={allocationData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={2}
                dataKey="value"
              >
                {allocationData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ background: '#1a2332', border: 'none', borderRadius: '8px' }}
                formatter={(v: number) => [`${v}%`, 'Weight']}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex flex-wrap gap-3 pt-4">
            {allocationData.map((item, i) => (
              <div key={item.name} className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: colors[i] }} />
                <span className="text-sm text-text-secondary">{item.name}</span>
                <span className="text-sm font-mono text-text-primary">{item.value}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Equity Curve */}
        <div className="col-span-2 card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-text-primary">Equity Curve</h3>
            <button className="btn btn-ghost p-2">
              <RefreshCw size={16} />
            </button>
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={equityCurve}>
              <defs>
                <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} tickFormatter={(v) => `$${(v/1000).toFixed(0)}k`} />
              <Tooltip 
                contentStyle={{ background: '#1a2332', border: 'none', borderRadius: '8px' }}
                formatter={(v: number) => [`$${v.toLocaleString()}`, 'Value']}
              />
              <Area 
                type="monotone" 
                dataKey="value" 
                stroke="#10b981" 
                fillOpacity={1} 
                fill="url(#colorEquity)" 
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Holdings Table */}
      <div className="card">
        <h3 className="text-lg font-semibold text-text-primary mb-4">Holdings</h3>
        <table className="w-full">
          <thead>
            <tr className="text-text-muted text-sm border-b border-gray-800">
              <th className="text-left py-3 px-4">Ticker</th>
              <th className="text-right py-3 px-4">Weight</th>
              <th className="text-right py-3 px-4">P&L</th>
              <th className="text-right py-3 px-4">Return</th>
              <th className="text-right py-3 px-4">Actions</th>
            </tr>
          </thead>
          <tbody>
            {holdings.map((holding, i) => (
              <tr key={i} className="border-b border-gray-800/50 hover:bg-white/5">
                <td className="py-3 px-4">
                  <span className="font-mono font-bold text-text-primary">{holding.ticker}</span>
                </td>
                <td className="py-3 px-4 text-right">
                  <div className="flex items-center justify-end gap-2">
                    <div className="w-20 h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-accent-blue rounded-full"
                        style={{ width: `${holding.weight}%` }}
                      />
                    </div>
                    <span className="font-mono text-text-primary">{holding.weight}%</span>
                  </div>
                </td>
                <td className={`py-3 px-4 text-right font-mono ${holding.pnl >= 0 ? 'text-accent-green' : 'text-accent-red'}`}>
                  {holding.pnl >= 0 ? '+' : ''}${holding.pnl.toLocaleString()}
                </td>
                <td className={`py-3 px-4 text-right font-mono ${holding.pnlPct >= 0 ? 'text-accent-green' : 'text-accent-red'}`}>
                  {holding.pnlPct > 0 ? '+' : ''}{holding.pnlPct}%
                </td>
                <td className="py-3 px-4 text-right">
                  {holding.ticker !== 'CASH' && (
                    <button className="text-sm text-accent-red hover:underline">Sell</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Risk Metrics */}
      <div className="card">
        <h3 className="text-lg font-semibold text-text-primary mb-4">Risk Metrics</h3>
        <div className="grid grid-cols-6 gap-4">
          <div className="text-center">
            <p className="text-2xl font-bold text-text-primary">{riskMetrics.sharpe.toFixed(2)}</p>
            <p className="text-text-muted text-sm">Sharpe</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-accent-green">{riskMetrics.maxDrawdown}%</p>
            <p className="text-text-muted text-sm">Max DD</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-text-primary">{riskMetrics.volatility}%</p>
            <p className="text-text-muted text-sm">Volatility</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-text-primary">{riskMetrics.winRate}%</p>
            <p className="text-text-muted text-sm">Win Rate</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-accent-red">${riskMetrics.var95.toLocaleString()}</p>
            <p className="text-text-muted text-sm">VaR 95%</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-text-primary">{riskMetrics.beta.toFixed(2)}</p>
            <p className="text-text-muted text-sm">Beta</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Portfolio