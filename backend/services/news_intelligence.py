"""
News Intelligence Module
News scraping and sentiment analysis.
"""

import asyncio
import logging
import feedparser
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import requests
from bs4 import BeautifulSoup
import json

from config.settings import NEWSAPI_KEY, RSS_FEEDS, TARGET_ASSETS

logger = logging.getLogger(__name__)

# Known ticker mappings for macro events
TICKER_MAP = {
    "gold": "GLD",
    "silver": "SLV",
    "oil": "USO",
    "crude": "USO",
    "brent": "USO",
    "wti": "USO",
    "sp500": "SPY",
    "spy": "SPY",
    "nasdaq": "QQQ",
    "qqq": "QQQ",
    "russell": "IWM",
    "iwm": "IWM",
    "treasury": "TLT",
    "tlt": "TLT",
    "dollar": "USD",
    "dxy": "USD",
}


def extract_entities(text: str) -> List[str]:
    """Extract ticker symbols from text."""
    text_lower = text.lower()
    entities = []
    
    for keyword, ticker in TICKER_MAP.items():
        if keyword in text_lower:
            entities.append(ticker)
    
    # Extract any explicit $XXXX patterns
    matches = re.findall(r'\$([A-Z]{2,5})\b', text)
    entities.extend(matches)
    
    return list(set(entities))


def classify_event(headline: str, summary: str = "") -> str:
    """Classify news into macro event categories."""
    text = (headline + " " + summary).lower()
    
    # Geopolitical - war, conflict, sanctions, treaties
    geo_keywords = ["war", "military", "conflict", "sanction", "treaty", 
                  "diplomat", "russia", "china", "iran", "ukraine", "israel"]
    if any(kw in text for kw in geo_keywords):
        return "geopolitical"
    
    # Monetary - Fed, rates, inflation, CPI, PPI
    mon_keywords = ["fed", "federal reserve", "interest rate", "inflation", 
                   "cpi", "ppi", "treasury", "policy"]
    if any(kw in text for kw in mon_keywords):
        return "monetary"
    
    # Supply chain
    supply_keywords = ["supply", "opec", "production", "output", "inventory"]
    if any(kw in text for kw in supply_keywords):
        return "supply_chain"
    
    # Natural disaster
    disaster_keywords = ["earthquake", "hurricane", "flood", "storm", "volcano"]
    if any(kw in text for kw in disaster_keywords):
        return "disaster"
    
    # Earnings
    earnings_keywords = ["earnings", "revenue", "quarterly", "profit", "guidance"]
    if any(kw in text for kw in earnings_keywords):
        return "earnings"
    
    return "general"


class NewsScraper:
    """Scrape news from RSS and NewsAPI."""
    
    def __init__(self, api_key: str = "", max_headlines: int = 100):
        self.api_key = api_key
        self.max_headlines = max_headlines
        self.rss_feeds = RSS_FEEDS
    
    async def scrape_rss(self) -> List[Dict]:
        """Scrape headlines from RSS feeds."""
        articles = []
        
        for feed_url in self.rss_feeds:
            try:
                response = requests.get(feed_url, timeout=10)
                feed = feedparser.parse(response.content)
                
                for entry in feed.entries[:20]:
                    # Parse date
                    published = None
                    if hasattr(entry, 'published'):
                        try:
                            published = datetime(*entry.published_parsed[:6])
                        except:
                            pass
                    
                    article = {
                        'headline': entry.title,
                        'summary': entry.get('summary', ''),
                        'source': feed.feed.get('title', feed_url),
                        'url': entry.link,
                        'published_at': published or datetime.utcnow(),
                    }
                    articles.append(article)
                    
            except Exception as e:
                logger.error(f"Error parsing {feed_url}: {e}")
                continue
        
        # Deduplicate
        seen = set()
        unique = []
        for a in articles:
            if a['url'] not in seen:
                seen.add(a['url'])
                unique.append(a)
        
        return unique[:self.max_headlines]
    
    async def scrape_newsapi(self, query: str = "market OR economy OR stock") -> List[Dict]:
        """Scrape from NewsAPI."""
        if not self.api_key:
            return []
        
        url = "https://newsapi.org/v2/everything"
        params = {
            'q': query,
            'apiKey': self.api_key,
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': self.max_headlines
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            
            if data.get('status') != 'ok':
                logger.error(f"NewsAPI error: {data.get('message')}")
                return []
            
            articles = []
            for a in data.get('articles', []):
                articles.append({
                    'headline': a['title'],
                    'summary': a.get('description', ''),
                    'source': a.get('source', {}).get('name', 'NewsAPI'),
                    'url': a['url'],
                    'published_at': a.get('publishedAt'),
                })
            
            return articles
            
        except Exception as e:
            logger.error(f"NewsAPI error: {e}")
            return []
    
    async def scrape_all(self) -> List[Dict]:
        """Scrape from all sources."""
        rss_task = self.scrape_rss()
        newsapi_task = self.scape_newsapi()
        
        rss_results, newsapi_results = await asyncio.gather(
            rss_task, newsapi_task
        )
        
        # Combine and deduplicate
        combined = rss_results + newsapi_results
        
        # Deduplicate by URL
        seen = set()
        unique = []
        for a in combined:
            if a['url'] not in seen:
                seen.add(a['url'])
                a['entities'] = extract_entities(a['headline'])
                a['event_type'] = classify_event(a['headline'], a.get('summary', ''))
                unique.append(a)
        
        # Sort by publish date
        unique.sort(key=lambda x: x.get('published_at', datetime.min), reverse=True)
        
        return unique[:self.max_headlines]


class SentimentAnalyzer:
    """
    Sentiment analysis using transformers.
    Uses FinBERT for financial text.
    """
    
    def __init__(self, model_name: str = "ProsusAI/finbert"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
    
    async def load_model(self):
        """Load FinBERT model."""
        if self.model is not None:
            return
        
        logger.info(f"Loading {self.model_name}")
        
        try:
            from transformers import AutoModelForSequenceClassification, AutoTokenizer
            import torch
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name
            )
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            
            logger.info(f"Loaded FinBERT on {self.device}")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            # Fallback to basic analysis
            self.use_fallback = True
    
    def analyze(self, text: str) -> Tuple[float, str]:
        """
        Analyze sentiment of text.
        Returns: (score, label)
        Score: -1 (negative) to 1 (positive)
        Label: 'positive', 'negative', 'neutral'
        """
        if not text:
            return 0.0, "neutral"
        
        # Use fallback if model not loaded
        if getattr(self, 'use_fallback', False) or self.model is None:
            return self._simple_analysis(text)
        
        try:
            import torch
            
            inputs = self.tokenizer(
                text, 
                return_tensors="pt", 
                truncation=True,
                max_length=512
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Map to sentiment
            # FinBERT: positive, negative, neutral
            neg_prob = probs[0][0].item()
            pos_prob = probs[0][1].item()
            neu_prob = probs[0][2].item()
            
            if pos_prob > neg_prob and pos_prob > neu_prob:
                score = pos_prob
                label = "positive"
            elif neg_prob > pos_prob and neg_prob > neu_prob:
                score = -neg_prob
                label = "negative"
            else:
                score = 0.0
                label = "neutral"
            
            return score, label
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return self._simple_analysis(text)
    
    def _simple_analysis(self, text: str) -> Tuple[float, str]:
        """
        Simple word-based sentiment fallback.
        """
        text_lower = text.lower()
        
        positive_words = [
            "gain", "rise", "surge", "rally", "bull", "growth", "profit",
            "beat", "upgrade", "buy", "long", "optimistic", "recovery"
        ]
        negative_words = [
            "fall", "drop", "crash", "bear", "loss", "decline", "miss",
            "downgrade", "sell", "short", "pessimistic", "recession", "crisis"
        ]
        
        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)
        
        total = pos_count + neg_count
        if total == 0:
            return 0.0, "neutral"
        
        if pos_count > neg_count:
            score = pos_count / total
            return score, "positive"
        elif neg_count > pos_count:
            score = -neg_count / total
            return score, "negative"
        else:
            return 0.0, "neutral"
    
    async def batch_analyze(self, texts: List[str]) -> List[Tuple[float, str]]:
        """Analyze multiple texts."""
        await self.load_model()
        return [self.analyze(t) for t in texts]


async def process_news_articles(db, news_scraper, sentiment_analyzer):
    """
    Main processing pipeline: scrape -> analyze -> store.
    """
    # Scrape
    articles = await news_scraper.scrape_all()
    logger.info(f"Scraped {len(articles)} articles")
    
    # Analyze
    for article in articles:
        headline = article['headline']
        summary = article.get('summary', '')
        text = headline + " " + summary
        
        score, label = sentiment_analyzer.analyze(text)
        
        article['sentiment_score'] = score
        article['sentiment_label'] = label
        
        # Store in DB
        await db.add_news_article(
            headline=headline,
            source=article['source'],
            url=article['url'],
            summary=summary,
            published_at=article.get('published_at'),
            sentiment_score=score,
            sentiment_label=label,
            entities=article.get('entities', []),
            event_type=article.get('event_type')
        )
    
    return articles