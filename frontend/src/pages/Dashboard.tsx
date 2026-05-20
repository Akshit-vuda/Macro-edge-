import React from 'react'
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar
} from 'recharts'
import { ArrowUpRight, ArrowDownRight, TrendingUp, AlertTriangle, Activity } from 'lucide-react'

// Mock data
const portfolioData = [
  { date: 'Jan', value: 100000 },
  { date: 'Feb', value: 102500 },
  { date: 'Mar', value: 101200 },
  { date: 'Apr', value: 104800 },
  { date: 'May', value: 106500 },
  { date: 'Jun', value: 108200 },
]

const returnsData = [
  { day: 'Mon', gld: 0.5, slv: 0.8, uso: -0.3 },
  { day: 'Tue', gld: 0.2, slv: -0.1, uso: 1.2 },
  { day: 'Wed', gld: 1.1, slv: 0.9, uso: 0.4 },
  { day: 'Thu', gld: 0.3, slv: 0.5, uso: -0.8 },
  { day: 'Fri', gld: -0.2, slv: 0.1, uso: 0.6 },
]

const signalsData = [
  { ticker: 'GLD', direction: 'up', confidence: 72, horizon: 5, type: 'commodity' },
  { ticker: 'SLV', direction: 'up', confidence: 65, horizon: 3, type: 'commodity' },
  { ticker: 'USO', direction: 'down', confidence: 58, horizon: 7, type: 'commodity' },
  { ticker: 'SPY', direction: 'up', confidence: 61, horizon: 5, type: 'macro' },
]

const StatCard = ({ 
  title, 
  value, 
  change, 
  icon: Icon, 
  positive 
}: { 
  title: string
  value: string
  change?: string
  icon: React.ElementType
  positive?: boolean
}) => (
  <div className="card">
    <div className="flex items-start justify-between mb-3">
      <span className="text-text-secondary text-sm">{title}</span>
      <Icon size={20} className={positive ? 'text-accent-green' : 'text-text-muted'} />
    </div>
    <p className="text-2xl font-bold text-text-primary mb-1">{value}</p>
    {change && (
      <p className={`text-sm flex items-center gap-1 ${positive ? 'text-accent-green' : 'text-accent-red'}`}>
        {positive ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
        {change}
      </p>
    )}
  </div>
)

const SignalRow = ({ signal }: { signal: typeof signalsData[0] }) => (
  <tr className="border-b border-gray-800/50 hover:bg-white/5 transition-colors">
    <td className="py-3 px-4">
      <div className="flex items-center gap-2">
        <span className="font-mono font-bold text-text-primary">{signal.ticker}</span>
        <span className="text-xs text-text-muted px-2 py-0.5 bg-gray-800 rounded">{signal.type}</span>
      </div>
    </td>
    <td className="py-3 px-4">
      <span className={`flex items-center gap-1 ${
        signal.direction === 'up' ? 'text-accent-green' : 'text-accent-red'
      }`}>
        {signal.direction === 'up' ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
        <span className="capitalize font-medium">{signal.direction}</span>
      </span>
    </td>
    <td className="py-3 px-4">
      <div className="flex items-center gap-2">
        <div className="w-16 h-2 bg-gray-700 rounded-full overflow-hidden">
          <div 
            className={`h-full rounded-full ${signal.confidence >= 65 ? 'bg-accent-green' : 'bg-accent-amber'}`}
            style={{ width: `${signal.confidence}%` }}
          />
        </div>
        <span className="text-sm text-text-secondary">{signal.confidence}%</span>
      </div>
    </td>
    <td className="py-3 px-4 text-text-secondary text-sm">{signal.horizon}d</td>
  </tr>
)

const Dashboard = () => {
  return (
    <div className="p-6 space-y-6">
      {/* Stats Row */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard 
          title="Portfolio Value" 
          value="$108,200" 
          change="+8.2%"
          positive={true}
          icon={TrendingUp}
        />
        <StatCard 
          title="Today's P&L" 
          value="+$342" 
          change="+0.32%"
          positive={true}
          icon={Activity}
        />
        <StatCard 
          title="Active Signals" 
          value="4" 
          icon={LineChart}
        />
        <StatCard 
          title="Max Drawdown" 
          value="-2.1%" 
          change=" Within target"
          positive={true}
          icon={AlertTriangle}
        />
      </div>
      
      {/* Charts */}
      <div className="grid grid-cols-3 gap-4">
        {/* Portfolio Chart */}
        <div className="col-span-2 card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-text-primary">Portfolio Performance</h3>
            <div className="flex gap-2">
              <button className="px-3 py-1 text-xs bg-accent-blue/20 text-accent-blue rounded">1M</button>
              <button className="px-3 py-1 text-xs bg-transparent text-text-muted hover:text-text-secondary rounded">3M</button>
              <button className="px-3 py-1 text-xs bg-transparent text-text-muted hover:text-text-secondary rounded">1Y</button>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={portfolioData}>
              <defs>
                <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" stroke="#64748b" fontSize={12} />
              <YAxis 
                stroke="#64748b" 
                fontSize={12}
                tickFormatter={(v) => `$${(v/1000).toFixed(0)}k`}
              />
              <Tooltip 
                contentStyle={{ background: '#1a2332', border: 'none', borderRadius: '8px' }}
                formatter={(v: number) => [`$${v.toLocaleString()}`, 'Value']}
              />
              <Area 
                type="monotone" 
                dataKey="value" 
                stroke="#3b82f6" 
                fillOpacity={1} 
                fill="url(#colorValue)" 
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        
        {/* Returns Chart */}
        <div className="card">
          <h3 className="text-lg font-semibold text-text-primary mb-6">Daily Returns</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={returnsData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="day" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} tickFormatter={(v) => `${v}%`} />
              <Tooltip 
                contentStyle={{ background: '#1a2332', border: 'none', borderRadius: '8px' }}
                formatter={(v: number) => [`${v.toFixed(1)}%`, '']}
              />
              <Bar dataKey="gld" fill="#f59e0b" radius={[4, 4, 0, 0]} name="GLD" />
              <Bar dataKey="slv" fill="#94a3b8" radius={[4, 4, 0, 0]} name="SLV" />
              <Bar dataKey="uso" fill="#ef4444" radius={[4, 4, 0, 0]} name="USO" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      {/* Active Signals */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-text-primary">Active Signals</h3>
          <button className="btn btn-ghost text-sm">View All →</button>
        </div>
        <table className="w-full">
          <thead>
            <tr className="text-text-muted text-sm border-b border-gray-800">
              <th className="text-left py-3 px-4">Ticker</th>
              <th className="text-left py-3 px-4">Direction</th>
              <th className="text-left py-3 px-4">Confidence</th>
              <th className="text-left py-3 px-4">Horizon</th>
            </tr>
          </thead>
          <tbody>
            {signalsData.map((signal, i) => (
              <SignalRow key={i} signal={signal} />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default Dashboard