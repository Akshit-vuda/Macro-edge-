import React from 'react'
import { Newspaper, Search, Filter, ExternalLink, TrendingUp, TrendingDown } from 'lucide-react'

const newsArticles = [
  {
    headline: "Fed Signals Potential Rate Cuts in Q3 as Inflation Cools",
    summary: "Federal Reserve officials indicated they may begin cutting interest rates in the third quarter...",
    source: "Reuters",
    sentiment: 0.72,
    eventType: "monetary",
    assets: ["SPY", "TLT", "GLD"],
    publishedAt: "2 hours ago"
  },
  {
    headline: "Oil Surges on Middle East Tensions - USO Up 3.2%",
    summary: "Crude oil prices jumped over 3% amid ongoing geopolitical tensions in the Middle East...",
    source: "Bloomberg",
    sentiment: -0.45,
    eventType: "geopolitical",
    assets: ["USO", "XLE"],
    publishedAt: "4 hours ago"
  },
  {
    headline: "Gold Breakout: GLD Gains on Safe-Haven Demand",
    summary: "Gold ETFs saw inflows as investors sought safe havens amid market uncertainty...",
    source: "FT",
    sentiment: 0.58,
    eventType: "supply_chain",
    assets: ["GLD", "SLV"],
    publishedAt: "5 hours ago"
  },
  {
    headline: "Tech Rally Continues - XLK Leads Sector Gains",
    summary: "Technology sector outperformed with AI-driven buying pushing indices to new highs...",
    source: "WSJ",
    sentiment: 0.65,
    eventType: "earnings",
    assets: ["XLK", "QQQ"],
    publishedAt: "6 hours ago"
  },
  {
    headline: "Dollar Weakness Drives EM Currency Gains",
    summary: "Weakening dollar boosted emerging market currencies and international equities...",
    source: "Reuters",
    sentiment: 0.22,
    eventType: "monetary",
    assets: ["SPY", "EEM"],
    publishedAt: "8 hours ago"
  },
]

const News = () => {
  const getSentimentIcon = (sentiment: number) => {
    if (sentiment > 0.3) return <TrendingUp size={16} className="text-accent-green" />
    if (sentiment < -0.3) return <TrendingDown size={16} className="text-accent-red" />
    return null
  }

  const getSentimentLabel = (sentiment: number) => {
    if (sentiment > 0.3) return 'bullish'
    if (sentiment < -0.3) return 'bearish'
    return 'neutral'
  }

  const getSentimentColor = (sentiment: number) => {
    if (sentiment > 0.3) return 'text-accent-green bg-accent-green/10'
    if (sentiment < -0.3) return 'text-accent-red bg-accent-red/10'
    return 'text-text-muted bg-gray-800'
  }

  return (
    <div className="p-6 space-y-6">
      {/* Search & Filters */}
      <div className="flex items-center gap-4">
        <div className="flex-1 relative">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
          <input 
            type="text" 
            placeholder="Search news..."
            className="w-full bg-bg-card border border-gray-800 text-text-primary pl-10 pr-4 py-2.5 rounded-lg focus:outline-none focus:border-accent-blue"
          />
        </div>
        <button className="btn btn-ghost flex items-center gap-2">
          <Filter size={16} />
          Filters
        </button>
      </div>

      {/* Event Type Pills */}
      <div className="flex gap-2">
        {['All', 'Monetary', 'Geopolitical', 'Supply Chain', 'Earnings'].map((type, i) => (
          <button 
            key={type}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
              i === 0 
                ? 'bg-accent-blue text-white' 
                : 'bg-bg-card text-text-secondary hover:text-text-primary'
            }`}
          >
            {type}
          </button>
        ))}
      </div>

      {/* News Feed */}
      <div className="space-y-4">
        {newsArticles.map((article, idx) => (
          <div key={idx} className="card hover:border-gray-700 transition-colors">
            <div className="flex items-start gap-4">
              {/* Sentiment Indicator */}
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${getSentimentColor(article.sentiment)}`}>
                {getSentimentIcon(article.sentiment)}
              </div>

              {/* Content */}
              <div className="flex-1">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="text-text-primary font-medium leading-snug">
                    {article.headline}
                  </h3>
                  <span className="text-text-muted text-sm whitespace-nowrap ml-4">
                    {article.publishedAt}
                  </span>
                </div>

                <p className="text-text-secondary text-sm mb-3 line-clamp-2">
                  {article.summary}
                </p>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-text-muted text-sm">{article.source}</span>
                    <span className="text-text-muted text-sm">•</span>
                    <span className={`text-xs px-2 py-0.5 rounded ${getSentimentColor(article.sentiment)}`}>
                      {getSentimentLabel(article.sentiment)}
                    </span>
                    <span className="text-xs px-2 py-0.5 rounded bg-gray-800 text-text-secondary">
                      {article.eventType}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    {article.assets.map((asset, i) => (
                      <span key={i} className="font-mono text-xs text-accent-blue bg-accent-blue/10 px-2 py-1 rounded">
                        {asset}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Load More */}
      <div className="text-center">
        <button className="btn btn-ghost">
          Load More Articles
        </button>
      </div>
    </div>
  )
}

export default News