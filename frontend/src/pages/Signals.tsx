import React from 'react'
import { ArrowUpRight, ArrowDownRight, Clock, CheckCircle, XCircle, Filter } from 'lucide-react'

const signals = [
  { ticker: 'GLD', direction: 'up', confidence: 72, horizon: 5, type: 'commodity', sentiment: 0.65, technical: 0.78, status: 'active' },
  { ticker: 'SLV', direction: 'up', confidence: 65, horizon: 3, type: 'commodity', sentiment: 0.58, technical: 0.71, status: 'active' },
  { ticker: 'USO', direction: 'down', confidence: 58, horizon: 7, type: 'commodity', sentiment: -0.42, technical: 0.65, status: 'pending' },
  { ticker: 'SPY', direction: 'up', confidence: 61, horizon: 5, type: 'macro', sentiment: 0.35, technical: 0.68, status: 'executed' },
  { ticker: 'QQQ', direction: 'up', confidence: 55, horizon: 5, type: 'macro', sentiment: 0.28, technical: 0.62, status: 'expired' },
  { ticker: 'TLT', direction: 'down', confidence: 52, horizon: 7, type: 'macro', sentiment: -0.15, technical: 0.58, status: 'pending' },
]

const Signals = () => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-accent-green'
      case 'pending': return 'text-accent-amber'
      case 'executed': return 'text-accent-blue'
      case 'expired': return 'text-text-muted'
      default: return 'text-text-secondary'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle size={14} />
      case 'pending': return <Clock size={14} />
      case 'executed': return <CheckCircle size={14} />
      case 'expired': return <XCircle size={14} />
      default: return null
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Filters */}
      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          <button className="btn btn-primary flex items-center gap-2">
            <Filter size={16} />
            Filter
          </button>
          <select className="bg-bg-card border border-gray-800 text-text-primary px-3 py-2 rounded-lg">
            <option>All Assets</option>
            <option>GLD</option>
            <option>SLV</option>
            <option>USO</option>
          </select>
          <select className="bg-bg-card border border-gray-800 text-text-primary px-3 py-2 rounded-lg">
            <option>All Directions</option>
            <option>Up</option>
            <option>Down</option>
          </select>
        </div>
        <div className="text-text-secondary">
          Showing <span className="text-text-primary font-medium">{signals.length}</span> signals
        </div>
      </div>

      {/* Signal Cards */}
      <div className="grid grid-cols-2 gap-4">
        {signals.map((signal, idx) => (
          <div key={idx} className="card hover:border-gray-700 transition-colors">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <span className="font-mono text-xl font-bold text-text-primary">{signal.ticker}</span>
                <span className={`flex items-center gap-1 ${
                  signal.direction === 'up' ? 'text-accent-green' : 'text-accent-red'
                }`}>
                  {signal.direction === 'up' ? <ArrowUpRight size={18} /> : <ArrowDownRight size={18} />}
                  <span className="capitalize font-medium">{signal.direction}</span>
                </span>
              </div>
              <div className={`flex items-center gap-1 ${getStatusColor(signal.status)}`}>
                {getStatusIcon(signal.status)}
                <span className="text-sm capitalize">{signal.status}</span>
              </div>
            </div>

            {/* Confidence */}
            <div className="mb-4">
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="text-text-secondary">Confidence</span>
                <span className="font-mono text-text-primary">{signal.confidence}%</span>
              </div>
              <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className={`h-full rounded-full ${
                    signal.confidence >= 65 ? 'bg-accent-green' : 
                    signal.confidence >= 55 ? 'bg-accent-amber' : 'bg-accent-red'
                  }`}
                  style={{ width: `${signal.confidence}%` }}
                />
              </div>
            </div>

            {/* Details */}
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-text-secondary block mb-1">Horizon</span>
                <span className="text-text-primary font-mono">{signal.horizon} days</span>
              </div>
              <div>
                <span className="text-text-secondary block mb-1">Sentiment</span>
                <span className={`font-mono ${signal.sentiment >= 0 ? 'text-accent-green' : 'text-accent-red'}`}>
                  {signal.sentiment > 0 ? '+' : ''}{signal.sentiment.toFixed(2)}
                </span>
              </div>
              <div>
                <span className="text-text-secondary block mb-1">Technical</span>
                <span className="text-text-primary font-mono">{signal.technical.toFixed(2)}</span>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-2 mt-4 pt-4 border-t border-gray-800">
              {signal.status === 'pending' && (
                <>
                  <button className="flex-1 btn bg-accent-green/20 text-accent-green hover:bg-accent-green/30">
                    Approve
                  </button>
                  <button className="flex-1 btn bg-accent-red/20 text-accent-red hover:bg-accent-red/30">
                    Reject
                  </button>
                </>
              )}
              {signal.status === 'active' && (
                <button className="flex-1 btn bg-accent-blue/20 text-accent-blue hover:bg-accent-blue/30">
                  Execute Trade
                </button>
              )}
              {signal.status === 'executed' && (
                <span className="flex-1 text-center py-2 text-text-muted text-sm">
                  Executed on Jun 15
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Signals