import React from 'react'
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import { 
  LayoutDashboard, 
  LineChart, 
  Globe, 
  Settings, 
  Bell, 
  Wallet,
  TrendingUp,
  Activity
} from 'lucide-react'
import Dashboard from './pages/Dashboard'
import Signals from './pages/Signals'
import News from './pages/News'
import Portfolio from './pages/Portfolio'

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/signals', icon: TrendingUp, label: 'Signals' },
  { path: '/news', icon: Globe, label: 'News' },
  { path: '/portfolio', icon: Wallet, label: 'Portfolio' },
]

function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen bg-bg-primary">
        {/* Sidebar */}
        <aside className="w-64 bg-bg-secondary border-r border-gray-800 p-4 flex flex-col">
          <div className="flex items-center gap-3 mb-8 px-2">
            <Activity className="w-8 h-8 text-accent-blue" />
            <div>
              <h1 className="text-xl font-bold text-text-primary">MacroEdge</h1>
              <p className="text-xs text-text-muted">Intelligence Platform</p>
            </div>
          </div>
          
          <nav className="flex-1 space-y-1">
            {navItems.map(({ path, icon: Icon, label }) => (
              <NavLink
                key={path}
                to={path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
                    isActive
                      ? 'bg-accent-blue/10 text-accent-blue'
                      : 'text-text-secondary hover:text-text-primary hover:bg-white/5'
                  }`
                }
              >
                <Icon size={20} />
                <span className="font-medium">{label}</span>
              </NavLink>
            ))}
          </nav>
          
          <div className="border-t border-gray-800 pt-4 mt-4">
            <NavLink
              to="/settings"
              className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-text-secondary hover:text-text-primary hover:bg-white/5 transition-all"
            >
              <Settings size={20} />
              <span className="font-medium">Settings</span>
            </NavLink>
          </div>
        </aside>
        
        {/* Main content */}
        <main className="flex-1 overflow-auto">
          <header className="h-16 bg-bg-secondary border-b border-gray-800 flex items-center justify-between px-6">
            <h2 className="text-lg font-semibold text-text-primary">
              {window.location.pathname === '/' && 'Dashboard'}
              {window.location.pathname === '/signals' && 'Trading Signals'}
              {window.location.pathname === '/news' && 'News Intelligence'}
              {window.location.pathname === '/portfolio' && 'Portfolio'}
            </h2>
            
            <div className="flex items-center gap-4">
              <button className="relative p-2 text-text-secondary hover:text-text-primary transition-colors">
                <Bell size={20} />
                <span className="absolute top-1 right-1 w-2 h-2 bg-accent-red rounded-full" />
              </button>
              
              <div className="flex items-center gap-3 pl-4 border-l border-gray-800">
                <div className="text-right">
                  <p className="text-sm font-medium text-text-primary">Demo Account</p>
                  <p className="text-xs text-accent-green">Paper Trading</p>
                </div>
                <div className="w-10 h-10 rounded-full bg-accent-blue/20 flex items-center justify-center">
                  <span className="text-accent-blue font-bold">M</span>
                </div>
              </div>
            </div>
          </header>
          
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/signals" element={<Signals />} />
            <Route path="/news" element={<News />} />
            <Route path="/portfolio" element={<Portfolio />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App