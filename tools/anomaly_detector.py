# tools/anomaly_detector.py

from crewai.tools import tool 
import pandas as pd
import json

@tool
def detect_anomalies(
    filepath: str,
    campaign: str = "all",
    metric: str = "roas",
    sensitivity: float = 2.0
) -> str:
    """
    Detect anomalies (unusual spikes or dips) in campaign performance metrics.
    
    Use this when you want to identify days when campaign performance was
    unexpectedly high or low compared to normal patterns.
    
    Args:
        filepath: Path to CSV file with marketing data
        campaign: Campaign to analyze ('all' for all campaigns)
        metric: Which metric to analyze ('roas', 'ctr', 'conversion_rate', 'cpc')
        sensitivity: How sensitive to anomalies (1.5-3.0, higher = more sensitive)
    
    Returns:
        JSON with:
        - anomalies: List of days with unusual performance
        - anomaly_type: 'spike' (unusually high) or 'dip' (unusually low)
        - average_value: Normal performance baseline
        - insights: What the anomalies mean
    
    Example:
        detect_anomalies('data.csv', 'Growth Campaign A', 'roas', 2.0)
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
        
        # GROUP BY DATE
        daily_data = df.groupby('date').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'conversions': 'sum',
            'revenue': 'sum',
            'ad_spend': 'sum'
        }).reset_index()
        
        daily_data = daily_data.sort_values('date')
        
        # CALCULATE METRIC
        if metric == "roas":
            daily_data['metric'] = (daily_data['revenue'] / daily_data['ad_spend']).fillna(0)
            metric_display = "ROAS"
        elif metric == "ctr":
            daily_data['metric'] = (daily_data['clicks'] / daily_data['impressions'] * 100).fillna(0)
            metric_display = "CTR (%)"
        elif metric == "conversion_rate":
            daily_data['metric'] = (daily_data['conversions'] / daily_data['clicks'] * 100).fillna(0)
            metric_display = "Conversion Rate (%)"
        elif metric == "cpc":
            daily_data['metric'] = (daily_data['ad_spend'] / daily_data['clicks']).fillna(0)
            metric_display = "CPC ($)"
        else:
            return json.dumps({"error": f"Unknown metric: {metric}"})
        
        if len(daily_data) < 3:
            return json.dumps({
                "error": "Not enough data to detect anomalies"
            })
        
        # CALCULATE STATISTICS
        mean_value = daily_data['metric'].mean()
        std_value = daily_data['metric'].std()
        
        if std_value == 0:
            return json.dumps({
                "error": "No variation in metric - cannot detect anomalies"
            })
        
        # DETECT ANOMALIES
        threshold = sensitivity * std_value
        anomalies = []
        
        for idx, row in daily_data.iterrows():
            value = row['metric']
            z_score = (value - mean_value) / std_value
            
            # Anomaly if more than threshold standard deviations away
            if abs(z_score) > sensitivity:
                anomaly_type = "spike" if value > mean_value else "dip"
                anomaly_severity = abs(z_score)
                
                anomalies.append({
                    "date": row['date'].strftime('%Y-%m-%d'),
                    "value": float(round(value, 2)),
                    "type": anomaly_type,
                    "severity": float(round(anomaly_severity, 2)),
                    "deviation_from_mean": float(round(value - mean_value, 2)),
                    "percentage_change": float(round((value - mean_value) / mean_value * 100, 1)) if mean_value > 0 else 0
                })
        
        # GENERATE INSIGHTS
        if not anomalies:
            insights = "No significant anomalies detected. Performance is consistent."
        else:
            spike_count = sum(1 for a in anomalies if a['type'] == 'spike')
            dip_count = sum(1 for a in anomalies if a['type'] == 'dip')
            
            if spike_count > dip_count:
                insights = f"Found {spike_count} positive spikes - investigate what caused the upswings to replicate success."
            elif dip_count > spike_count:
                insights = f"Found {dip_count} negative dips - investigate what caused the downturns to avoid them."
            else:
                insights = f"Found {spike_count} spikes and {dip_count} dips - performance is highly variable, review campaign consistency."
        
        return json.dumps({
            "success": True,
            "campaign": campaign if campaign != "all" else "All Campaigns",
            "metric": metric,
            "metric_display": metric_display,
            "average_value": float(round(mean_value, 2)),
            "std_dev": float(round(std_value, 2)),
            "sensitivity_threshold": float(sensitivity),
            "anomalies_found": len(anomalies),
            "anomalies": anomalies,
            "insights": insights
        })
    
    except Exception as e:
        return json.dumps({
            "error": f"Error detecting anomalies: {str(e)}",
            "error_type": type(e).__name__
        })