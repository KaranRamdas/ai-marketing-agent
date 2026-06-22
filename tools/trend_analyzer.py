# tools/trend_analyzer.py

from crewai.tools import tool
import pandas as pd
import json

@tool
def analyze_trends(
    filepath: str,
    campaign: str = "all",
    metric: str = "ctr",
    window_days: int = 7
) -> str:
    """
    Analyze if campaign metrics are improving, declining, or stable over time.
    
    Use this when you need to understand if a campaign's performance is
    trending up, down, or remaining steady.
    
    Args:
        filepath: Path to CSV file with marketing data
        campaign: Campaign to analyze ('all' for all campaigns)
        metric: Which metric to analyze ('ctr', 'roas', 'conversion_rate', 'cpc')
        window_days: Number of days to use for trend calculation (default 7)
    
    Returns:
        JSON with:
        - trend: 'improving', 'declining', or 'stable'
        - trend_percentage: How much the metric changed
        - daily_values: Daily metric values
        - recommendation: What to do based on trend
    
    Example:
        analyze_trends('data.csv', 'Growth Campaign A', 'roas', 7)
    """
    
    try:
        # LOAD DATA
        df = pd.read_csv(filepath)
        
        required_cols = ['date', 'campaign_name', 'impressions', 'clicks',
                        'conversions', 'revenue', 'ad_spend']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            return json.dumps({"error": f"Missing columns: {missing_cols}"})
        
        df['date'] = pd.to_datetime(df['date'])
        
        # FILTER BY CAMPAIGN
        if campaign != "all":
            df = df[df['campaign_name'] == campaign]
            if df.empty:
                return json.dumps({
                    "error": f"Campaign '{campaign}' not found"
                })
        
        # GROUP BY DATE AND CALCULATE METRICS
        daily_data = df.groupby('date').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'conversions': 'sum',
            'revenue': 'sum',
            'ad_spend': 'sum'
        }).reset_index()
        
        daily_data = daily_data.sort_values('date')
        
        # CALCULATE REQUESTED METRIC FOR EACH DAY
        if metric == "ctr":
            daily_data['metric'] = (daily_data['clicks'] / daily_data['impressions'] * 100)
            metric_display = "CTR (%)"
        elif metric == "roas":
            daily_data['metric'] = (daily_data['revenue'] / daily_data['ad_spend'])
            metric_display = "ROAS"
        elif metric == "conversion_rate":
            daily_data['metric'] = (daily_data['conversions'] / daily_data['clicks'] * 100)
            metric_display = "Conversion Rate (%)"
        elif metric == "cpc":
            daily_data['metric'] = (daily_data['ad_spend'] / daily_data['clicks'])
            metric_display = "CPC ($)"
        else:
            return json.dumps({"error": f"Unknown metric: {metric}"})
        
        # CALCULATE TREND
        if len(daily_data) < 2:
            return json.dumps({
                "error": "Not enough data to analyze trend"
            })
        
        # Split into two periods
        midpoint = len(daily_data) // 2
        first_period = daily_data.iloc[:midpoint]['metric'].mean()
        second_period = daily_data.iloc[midpoint:]['metric'].mean()
        
        # Determine trend
        change_percent = ((second_period - first_period) / first_period * 100) if first_period > 0 else 0
        
        if abs(change_percent) < 5:
            trend = "stable"
            trend_assessment = f"Relatively stable ({change_percent:.1f}% change)"
        elif change_percent > 5:
            trend = "improving"
            trend_assessment = f"Improving (+{change_percent:.1f}%)"
        else:
            trend = "declining"
            trend_assessment = f"Declining ({change_percent:.1f}%)"
        
        # RECOMMENDATION
        if trend == "improving":
            if metric in ["ctr", "roas", "conversion_rate"]:
                recommendation = "Keep scaling - strong upward momentum!"
            else:  # cpc
                recommendation = "Excellent - cost per click decreasing, maintain strategy"
        elif trend == "declining":
            if metric in ["ctr", "roas", "conversion_rate"]:
                recommendation = "Investigate decline - may need optimization or pause"
            else:  # cpc
                recommendation = "Costs rising - review targeting and bidding strategy"
        else:  # stable
            recommendation = "Performance is steady - consider testing new elements"
        
        # PREPARE RESPONSE
        daily_values = []
        for idx, row in daily_data.iterrows():
            daily_values.append({
                "date": row['date'].strftime('%Y-%m-%d'),
                "value": float(round(row['metric'], 2))
            })
        
        return json.dumps({
            "success": True,
            "campaign": campaign if campaign != "all" else "All Campaigns",
            "metric": metric,
            "metric_display": metric_display,
            "trend": trend,
            "trend_assessment": trend_assessment,
            "change_percent": float(round(change_percent, 2)),
            "first_period_avg": float(round(first_period, 2)),
            "second_period_avg": float(round(second_period, 2)),
            "daily_values": daily_values,
            "recommendation": recommendation
        })
    
    except Exception as e:
        return json.dumps({
            "error": f"Error analyzing trends: {str(e)}",
            "error_type": type(e).__name__
        })