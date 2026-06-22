# tools/campaign_comparator.py

from crewai.tools import tool 
import pandas as pd
import json
from .metric_calculator import calculate_marketing_metrics

@tool
def compare_campaigns(
    filepath: str,
    campaign_names: str = "all"
) -> str:
    """
    Compare performance between two or more campaigns.
    
    Use this when you need to determine which campaigns are performing
    better on specific metrics and get a ranking.
    
    Args:
        filepath: Path to CSV file
        campaign_names: Comma-separated list ('Campaign A,Campaign B')
                       or 'all' to compare all campaigns
    
    Returns:
        JSON with:
        - comparison: Side-by-side metrics
        - winner_by_metric: Which campaign wins on each metric
        - overall_winner: Best performing campaign
    
    Example:
        compare_campaigns('data.csv', 'Growth Campaign A,Growth Campaign B')
    """
    
    try:
        # Get all campaign metrics
        result_str = calculate_marketing_metrics(filepath, campaign='all')
        result = json.loads(result_str)
        
        if not result.get('success'):
            return result_str
        
        metrics = result['metrics']
        
        # If specific campaigns requested, filter
        if campaign_names != "all":
            camps_to_compare = [c.strip() for c in campaign_names.split(',')]
            metrics = [m for m in metrics if m['campaign'] in camps_to_compare]
        
        if len(metrics) < 2:
            return json.dumps({
                "error": "Need at least 2 campaigns to compare"
            })
        
        # Compare on key metrics
        comparison_data = {
            "campaigns_compared": [m['campaign'] for m in metrics],
            "metrics_comparison": metrics,
            "winners": {
                "highest_ctr": max(metrics, key=lambda x: x['ctr_percent'])['campaign'],
                "highest_rpc": max(metrics, key=lambda x: x['rpc'])['campaign'],
                "highest_roas": max(metrics, key=lambda x: x['roas'])['campaign'],
                "lowest_cpc": min(metrics, key=lambda x: x['cpc'])['campaign'],
                "highest_conversion_rate": max(metrics, key=lambda x: x['conversion_rate_percent'])['campaign'],
                "highest_revenue": max(metrics, key=lambda x: x['total_revenue'])['campaign']
            },
            "ranking_by_roas": sorted(metrics, key=lambda x: x['roas'], reverse=True)
        }
        
        return json.dumps({
            "success": True,
            "comparison": comparison_data
        })
    
    except Exception as e:
        return json.dumps({"error": str(e)})