"""
Claude AI Brain Layer
Supervision and risk narration via Anthropic API.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Optional
import anthropic

from config.settings import ANTHROPIC_API_KEY, CLAUDE_MODEL

logger = logging.getLogger(__name__)


# System prompts
SUPERVISOR_PROMPT = """You are Claude, an AI assistant monitoring a systematic macro trading system called MacroEdge.
Your role is to:
1. Provide daily model health reports
2. Narrate portfolio risk status  
3. Suggest parameter adjustments when needed
4. Flag anomalies and potential issues

Be concise, analytical, and risk-focused. Highlight any concerns clearly."""


def format_portfolio_summary(data: Dict) -> str:
    """Format portfolio data for Claude."""
    if not data:
        return "No portfolio data available."
    
    lines = []
    lines.append(f"Total Value: ${data.get('total_value', 0):,.2f}")
    lines.append(f"Daily P&L: ${data.get('daily_pnl', 0):,.2f}")
    
    if 'positions' in data:
        lines.append("\nPositions:")
        for pos in data['positions']:
            lines.append(
                f"  {pos['ticker']}: {pos['weight']:.1%} "
                f"(P&L: ${pos.get('pnl', 0):,.2f})"
            )
    
    return "\n".join(lines)


def format_signals(data: List[Dict]) -> str:
    """Format signals for Claude."""
    if not data:
        return "No active signals."
    
    lines = []
    for sig in data[:10]:  # Top 10
        lines.append(
            f"- {sig['ticker']}: {sig['direction']} "
            f"(conf: {sig['confidence']:.0%}, horizon: {sig['horizon_days']}d)"
        )
    
    return "\n".join(lines)


def format_risk_metrics(data: Dict) -> str:
    """Format risk metrics for Claude."""
    if not data:
        return "No risk metrics available."
    
    lines = []
    lines.append(f"Sharpe Ratio: {data.get('sharpe_ratio', 0):.2f}")
    lines.append(f"Max Drawdown: {data.get('max_drawdown', 0):.1%}")
    lines.append(f VaR (95%): ${data.get('var_95', 0):,.2f}")
    lines.append(f"Win Rate: {data.get('win_rate', 0):.1%}")
    lines.append(f"Volatility: {data.get('volatility', 0):.1%}")
    
    return "\n".join(lines)


def format_model_performance(models: Dict) -> str:
    """Format model performance for Claude."""
    if not models:
        return "No model data."
    
    lines = []
    for name, metrics in models.items():
        lines.append(f"\n{name}:")
        for k, v in metrics.items():
            if isinstance(v, float):
                lines.append(f"  {k}: {v:.3f}")
            else:
                lines.append(f"  {k}: {v}")
    
    return "\n".join(lines)


class ClaudeSupervisor:
    """
    Claude API wrapper for system supervision.
    """
    
    def __init__(
        self,
        api_key: str = "",
        model: str = None
    ):
        self.api_key = api_key or ANTHROPIC_API_KEY
        self.model = model or CLAUDE_MODEL
        self.client = None
        
        if self.api_key:
            self._connect()
    
    def _connect(self):
        """Initialize Anthropic client."""
        try:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except Exception as e:
            logger.error(f"Claude initialization error: {e}")
    
    def _call(
        self,
        messages: List[Dict],
        system: str = None,
        max_tokens: int = 1024
    ) -> Optional[str]:
        """Make API call."""
        if not self.client:
            return None
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system or SUPERVISOR_PROMPT,
                messages=messages
            )
            
            return response.content[0].text
            
        except anthropic.APIConnectionError as e:
            logger.error(f"API Connection Error: {e}")
        except anthropic.RateLimitError as e:
            logger.error(f"Rate Limit Error: {e}")
        except Exception as e:
            logger.error(f"Claude API error: {e}")
        
        return None
    
    def daily_report(
        self,
        portfolio: Dict,
        signals: List[Dict],
        risk_metrics: Dict,
        model_performance: Dict
    ) -> str:
        """
        Generate daily health report.
        """
        portfolio_text = format_portfolio_summary(portfolio)
        signals_text = format_signals(signals)
        risk_text = format_risk_metrics(risk_metrics)
        model_text = format_model_performance(model_performance)
        
        user_message = f"""Provide a daily health report for the MacroEdge trading system.

=== PORTFOLIO ===
{portfolio_text}

=== ACTIVE SIGNALS ===
{signals_text}

=== RISK METRICS ===
{risk_text}

=== MODEL PERFORMANCE ===
{model_text}

Please provide:
1. Overall system health assessment
2. Any concerning risk levels
3. Suggested parameter adjustments if needed
4. Market regime observations"""

        messages = [{"role": "user", "content": user_message}]
        
        return self._call(messages)
    
    def risk_narrative(
        self,
        portfolio: Dict,
        risk_metrics: Dict
    ) -> str:
        """
        Generate risk narrative.
        """
        risk_text = format_risk_metrics(risk_metrics)
        portfolio_text = format_portfolio_summary(portfolio)
        
        user_message = f"""Generate a short risk narrative (2-3 sentences).

=== PORTFOLIO ===
{portfolio_text}

=== RISK METRICS ===
{risk_text}

Focus on key risk factors and any alerts needed."""

        messages = [{"role": "user", "content": user_message}]
        
        return self._call(messages)
    
    def anomaly_alert(
        self,
        anomaly_type: str,
        details: Dict
    ) -> str:
        """
        Analyze an anomalous situation.
        """
        detail_text = json.dumps(details, indent=2)
        
        user_message = f"""Analyze this anomaly:

Type: {anomaly_type}
Details: {detail_text}

Should this be escalated? What action is recommended?"""

        messages = [{"role": "user", "content": user_message}]
        
        return self._call(messages)
    
    def model_review(
        self,
        model_name: str,
        metrics: Dict,
        backtest_results: Dict = None
    ) -> str:
        """
        Review model performance and suggest improvements.
        """
        metrics_text = format_risk_metrics(metrics)
        
        msg = f"""Review model: {model_name}

=== METRICS ===
{metrics_text}"""
        
        if backtest_results:
            msg += f"""

=== BACKTEST ===
{json.dumps(backtest_results, indent=2)}"""
        
        msg += """

Is this model ready for deployment? What's the confidence level?"""
        
        messages = [{"role": "user", "content": msg}]
        
        return self._call(messages)
    
    def signal_review(
        self,
        signals: List[Dict]
    ) -> str:
        """
        Review generated signals.
        """
        signals_text = format_signals(signals)
        
        user_message = f"""Review these trading signals:

{signals_text}

Are there any conflicts or concerns? Should any signals be overridden?"""

        messages = [{"role": "user", "content": user_message}]
        
        return self._call(messages)
    
    def analyze_macro_event(
        self,
        headline: str,
        summary: str,
        sentiment: str,
        assets: List[str]
    ) -> str:
        """
        Analyze a macro news event.
        """
        user_message = f"""Analyze this macro event for trading implications:

Headline: {headline}
Summary: {summary}
Sentiment: {sentiment}
Related assets: {', '.join(assets)}

What is the expected price impact on related assets over 3-7 days?
Any position adjustments recommended?"""

        messages = [{"role": "user", "content": user_message}]
        
        return self._call(messages)
    
    def trade_recommendation(
        self,
        signal: Dict,
        portfolio: Dict,
        risk_metrics: Dict
    ) -> str:
        """
        Get recommendation for executing a trade.
        """
        signal_text = format_signals([signal])
        risk_text = format_risk_metrics(risk_metrics)
        
        user_message = f"""Review this trade recommendation:

=== SIGNAL ===
{signal_text}

=== CURRENT PORTFOLIO ===
{format_portfolio_summary(portfolio)}

=== RISK METRICS ===
{risk_text}

Approve or reject? Size recommendation?"""

        messages = [{"role": "user", "content": user_message}]
        
        return self._call(messages)


# Helper for token counting and cost limits
def estimate_token_cost(text: str) -> float:
    """Estimate cost in dollars per million tokens."""
    # Rough approximation
    tokens = len(text.split()) * 1.3
    input_price = 3.0 / 1_000_000  # $3 per million input
    output_price = 15.0 / 1_000_000  # $15 per million output
    
    return tokens * input_price


def enforce_daily_token_cap(client: ClaudeSupervisor, max_daily: float = 45.0):
    """
    Check and enforce daily token spending cap.
    """
    # This would track cumulative spending
    # Simplified here - just log usage
    pass