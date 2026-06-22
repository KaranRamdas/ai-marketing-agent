# tools/budget_recommender.py

from crewai.tools import tool 

import pandas as pd
import json

@tool
def recommend_budget_allocation(
    filepath: str,
    total_budget: float = None,
    performance_metric: str = "roas"
) -> str:
    """
    Recommend how to allocate or adjust marketing budget across campaigns.
    
    Use this when you need to decide which campaigns to scale up, maintain,
    or pause based on their performance and efficiency.
    
    Args:
        filepath: Path to CSV file with marketing data
        total_budget: Optional total budget to allocate (will show allocation)
        performance_metric: Which metric to base recommendations on ('roas', 'ctr', 'conversion_rate')
    
    Returns:
        JSON with:
        - recommendations: Scale, maintain, or pause for each campaign
        - performance_ranking: Campaigns ranked by performance
        - budget_allocation: How to split budget (if total_budget provided)
    
    Example:
        recommend_budget_allocation('data.csv', total_budget=50000, performance_metric='roas')
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
        
        # CALCULATE METRICS PER CAMPAIGN
        campaign_stats = []
        
        for campaign in df['campaign_name'].unique():
            camp_data = df[df['campaign_name'] == campaign]
            
            total_impressions = camp_data['impressions'].sum()
            total_clicks = camp_data['clicks'].sum()
            total_conversions = camp_data['conversions'].sum()
            total_revenue = camp_data['revenue'].sum()
            total_ad_spend = camp_data['ad_spend'].sum()
            
            # Calculate metrics
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            cpc = total_ad_spend / total_clicks if total_clicks > 0 else 0
            rpc = total_revenue / total_clicks if total_clicks > 0 else 0
            conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
            roas = total_revenue / total_ad_spend if total_ad_spend > 0 else 0
            
            campaign_stats.append({
                "campaign": campaign,
                "ctr": ctr,
                "cpc": cpc,
                "rpc": rpc,
                "conversion_rate": conversion_rate,
                "roas": roas,
                "total_revenue": total_revenue,
                "total_ad_spend": total_ad_spend,
                "total_clicks": total_clicks
            })
        
        # RANK BY PERFORMANCE METRIC
        if performance_metric == "roas":
            ranked = sorted(campaign_stats, key=lambda x: x['roas'], reverse=True)
            metric_values = [c['roas'] for c in ranked]
        elif performance_metric == "ctr":
            ranked = sorted(campaign_stats, key=lambda x: x['ctr'], reverse=True)
            metric_values = [c['ctr'] for c in ranked]
        elif performance_metric == "conversion_rate":
            ranked = sorted(campaign_stats, key=lambda x: x['conversion_rate'], reverse=True)
            metric_values = [c['conversion_rate'] for c in ranked]
        else:
            return json.dumps({"error": f"Unknown metric: {performance_metric}"})
        
        # MAKE RECOMMENDATIONS
        recommendations = []
        
        for idx, campaign in enumerate(ranked):
            camp_name = campaign['campaign']
            metric_value = metric_values[idx]
            
            # Calculate percentile
            avg_metric = sum(metric_values) / len(metric_values)
            
            # Determine action
            if metric_value >= avg_metric * 1.2:  # 20% above average
                action = "SCALE"
                reasoning = f"Top performer with {performance_metric} of {metric_value:.2f}. Increase budget to capitalize on success."
                priority = "HIGH"
            elif metric_value >= avg_metric * 0.8:  # Within 80-120% of average
                action = "MAINTAIN"
                reasoning = f"Solid performer with {performance_metric} of {metric_value:.2f}. Keep current spending level."
                priority = "MEDIUM"
            else:
                action = "PAUSE_OR_OPTIMIZE"
                reasoning = f"Underperforming with {performance_metric} of {metric_value:.2f}. Either pause or significantly optimize before scaling."
                priority = "LOW"
            
            # Calculate potential
            if action == "SCALE":
                potential = "Scale by 25-50% to maximize ROI"
            elif action == "MAINTAIN":
                potential = "Test incremental increases; monitor performance"
            else:
                potential = "Optimize targeting/creative before increasing spend"
            
            recommendations.append({
                "rank": idx + 1,
                "campaign": camp_name,
                "action": action,
                "priority": priority,
                "metric_value": float(round(metric_value, 2)),
                "reasoning": reasoning,
                "potential": potential,
                "current_spend": float(round(campaign['total_ad_spend'], 2)),
                "revenue": float(round(campaign['total_revenue'], 2))
            })
        
        # BUDGET ALLOCATION (if total_budget provided)
        budget_allocation = None
        if total_budget:
            allocation = []
            scale_campaigns = [r for r in recommendations if r['action'] == 'SCALE']
            maintain_campaigns = [r for r in recommendations if r['action'] == 'MAINTAIN']
            
            if scale_campaigns:
                scale_budget = total_budget * 0.5  # 50% to scaling
                per_scale = scale_budget / len(scale_campaigns)
                for campaign in scale_campaigns:
                    allocation.append({
                        "campaign": campaign['campaign'],
                        "recommended_budget": float(round(per_scale, 2)),
                        "percentage": 50 / len(scale_campaigns)
                    })
            
            if maintain_campaigns:
                maintain_budget = total_budget * 0.35  # 35% to maintain
                per_maintain = maintain_budget / len(maintain_campaigns)
                for campaign in maintain_campaigns:
                    allocation.append({
                        "campaign": campaign['campaign'],
                        "recommended_budget": float(round(per_maintain, 2)),
                        "percentage": 35 / len(maintain_campaigns)
                    })
            
            # Remaining 15% for testing new campaigns
            allocation.append({
                "campaign": "NEW_CAMPAIGNS_TEST",
                "recommended_budget": float(round(total_budget * 0.15, 2)),
                "percentage": 15.0
            })
            
            budget_allocation = allocation
        
        return json.dumps({
            "success": True,
            "metric": performance_metric,
            "total_campaigns": len(recommendations),
            "recommendations": recommendations,
            "budget_allocation": budget_allocation,
            "summary": {
                "scale_count": sum(1 for r in recommendations if r['action'] == 'SCALE'),
                "maintain_count": sum(1 for r in recommendations if r['action'] == 'MAINTAIN'),
                "pause_count": sum(1 for r in recommendations if r['action'] == 'PAUSE_OR_OPTIMIZE')
            }
        })
    
    except Exception as e:
        return json.dumps({
            "error": f"Error recommending budget: {str(e)}",
            "error_type": type(e).__name__
        })