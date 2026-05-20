"""
SentimentModel: News & headline sentiment analysis
Simulates FinBERT for financial sentiment
Uses: NLP-based keyword scoring
Output: bullish/bearish/neutral with confidence
"""

import numpy as np
from typing import List, Dict, Tuple
from collections import Counter


class SentimentModel:
    """
    Analyzes news headlines and social sentiment
    Uses financial keywords and phrase matching
    """
    
    # Financial sentiment lexicon
    BULLISH_KEYWORDS = [
        "bullish", "buy", "upgrade", "beat", "exceed", "growth", "profit",
        "surge", "soar", "rally", "gain", "positive", "optimistic", "breakout",
        "outperform", "strong", "recovery", "recover", "expand", "innovation",
        "success", "deal", "partnership", "launch", "beat estimates"
    ]
    
    BEARISH_KEYWORDS = [
        "bearish", "sell", "downgrade", "miss", "below", "loss", "decline",
        "plunge", "drop", "fall", "negative", "pessimistic", "breakdown",
        "underperform", "weak", "crisis", "risk", "warning", "cut",
        "layoff", "lawsuit", "investigate", "fraud", "bankruptcy", "miss estimates"
    ]
    
    UNCERTAINTY_KEYWORDS = [
        "uncertain", "unclear", "may", "might", "could", "possible",
        "potential", "speculation", "debate", "concern", "watch", "monitor"
    ]
    
    def __init__(self, symbol: str = "SPY"):
        self.symbol = symbol
        self.word_weights = {
            "extreme_positive": 2.0,
            "positive": 1.0,
            "neutral": 0.0,
            "negative": -1.0,
            "extreme_negative": -2.0
        }
        
        # Extended weights
        self._build_lexicon()
        
    def _build_lexicon(self):
        """Build weighted sentiment lexicon"""
        
        # Strong bullish words (weight = 2)
        self.bullish_extreme = ["breakout", "all-time high", "record high", 
                               "beat", "crush", "soar", "surge"]
        
        # Strong bearish (weight = -2)
        self.bearish_extreme = ["crash", "plunge", "collapse", "bankruptcy",
                               "fraud", "scandal", "investigation"]
        
    def preprocess(self, text: str) -> str:
        """Clean and tokenize text"""
        text = text.lower()
        # Remove punctuation, keep alphanumeric
        for c in "!@#$%^&*()_+-=[]{}|;:,.<>?/`~":
            text = text.replace(c, " ")
        return text
    
    def score_headline(self, headline: str) -> Tuple[float, str]:
        """
        Score a single headline
        Returns: (score, strength)
        """
        text = self.preprocess(headline)
        words = text.split()
        
        bullish_count = 0
        bearish_count = 0
        uncertainty_count = 0
        
        for word in words:
            if word in self.bullish_extreme:
                bullish_count += 2
            elif word in self.bearish_extreme:
                bearish_count += 2
            elif word in self.BULLISH_KEYWORDS:
                bullish_count += 1
            elif word in self.BEARISH_KEYWORDS:
                bearish_count += 1
            elif word in self.UNCERTAINTY_KEYWORDS:
                uncertainty_count += 1
        
        # Calculate score (-1 to 1)
        total = bullish_count + bearish_count + 1e-10
        
        if total == 0:
            return 0.0, "neutral"
            
        score = (bullish_count - bearish_count) / (bullish_count + bearish_count)
        
        if abs(score) > 0.5:
            strength = "extreme_positive" if score > 0 else "extreme_negative"
        elif abs(score) > 0.2:
            strength = "positive" if score > 0 else "negative"
        else:
            strength = "neutral"
            
        # Reduce for uncertainty
        if uncertainty_count > 0:
            score *= 0.7
            
        return score, strength
    
    def analyze_headlines(self, headlines: List[str]) -> Dict:
        """
        Analyze multiple headlines
        Returns aggregated sentiment
        """
        
        if not headlines:
            return {
                "sentiment": "neutral",
                "score": 0.0,
                "confidence": 0.5,
                "headlines_analyzed": 0
            }
            
        scores = []
        strengths = []
        
        for headline in headlines:
            score, strength = self.score_headline(headline)
            scores.append(score)
            strengths.append(strength)
        
        # Aggregate stats
        avg_score = np.mean(scores)
        
        # Count agreement
        strength_counts = Counter(strengths)
        agreement = max(strength_counts.values()) / len(strengths)
        
        # Determine sentiment label
        if avg_score > 0.2:
            sentiment = "bullish"
        elif avg_score < -0.2:
            sentiment = "bearish"
        else:
            sentiment = "neutral"
            
        # Confidence based on agreement and magnitude
        confidence = min(0.5 + agreement * 0.25 + abs(avg_score) * 0.25, 0.95)
        
        return {
            "sentiment": sentiment,
            "score": float(avg_score),
            "confidence": float(confidence),
            "headlines_analyzed": len(headlines),
            "strength_distribution": dict(strength_counts),
            "individual_scores": [round(s, 2) for s in scores]
        }
    
    def analyze_sources(self, headlines_by_source: Dict[str, List[str]]) -> Dict:
        """
        Analyze headlines grouped by source
        Returns per-source and aggregate sentiment
        """
        
        source_sentiments = {}
        
        for source, headlines in headlines_by_source.items():
            source_sentiments[source] = self.analyze_headlines(headlines)
        
        # Aggregate across sources
        all_sentiments = [s["score"] for s in source_sentiments.values()]
        overall = self.analyze_headlines([
            h for heads in headlines_by_source.values() 
            for h in heads
        ])
        
        return {
            "overall": overall,
            "by_source": source_sentiments,
            "sources_analyzed": len(headlines_by_source)
        }
    
    def get_market_impact(self, sentiment_score: float) -> str:
        """Predict market impact based on sentiment"""
        
        if sentiment_score > 0.5:
            return "strongly_positive"
        elif sentiment_score > 0.2:
            return "positive"
        elif sentiment_score < -0.5:
            return "strongly_negative"
        elif sentiment_score < -0.2:
            return "negative"
        else:
            return "neutral"
    
    def create_trade_signal(self, sentiment_score: float, 
                           confidence: float) -> str:
        """Create trading signal from sentiment"""
        
        if confidence < 0.55:
            return "HOLD"
            
        if sentiment_score > 0.3:
            return "BUY"
        elif sentiment_score < -0.3:
            return "SELL"
        else:
            return "HOLD"


# Convenience function
def analyze_sentiment(headlines: List[str]) -> dict:
    """Analyze sentiment from headlines"""
    model = SentimentModel()
    return model.analyze_headlines(headlines)


if __name__ == "__main__":
    # Test with sample headlines
    test_headlines = [
        "Fed signals rate cut as inflation cools",
        "Tech stocks rally on strong earnings beat",
        "Trade tensions weigh on market sentiment",
        "Banks report record quarterly profit",
        "Economy shows signs of recovery",
        "Investors watchful amid uncertainty"
    ]
    
    print("Sentiment Analysis Test:\n")
    
    result = analyze_sentiment(test_headlines)
    
    for k, v in result.items():
        print(f"{k}: {v}")
    
    # Create trading signal
    model = SentimentModel()
    signal = model.create_trade_signal(
        result["score"], 
        result["confidence"]
    )
    print(f"\nTrading Signal: {signal}")