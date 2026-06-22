# tools/metric_calculator.py

from crewai.tools import tool
import pandas as pd
import json

@tool
def calculate_marketing_metrics(
    filepath: str,
    campaign: str = "all",
    channel: str = "all",
    start_date: str = None,
    end_date: str = None
) -> str:
    """
    Calculate key marketing metrics (CTR, CPC, RPC, Conversion Rate).
    
    Use this tool when you need to analyze campaign performance metrics
    including Click-Through Rate, Cost Per Click, Revenue Per Click,
    and conversion rates.
    
    Args:
        filepath: Path to CSV file with columns: date, campaign_name, channel,
                 impressions, clicks, conversions, revenue, ad_spend, reach
        campaign: Campaign to analyze ('all' for all campaigns, or 'Growth Campaign A')
        channel: Marketing channel ('all' for all, or 'Google Ads', 'Facebook', etc.)
        start_date: Optional filter (format: YYYY-MM-DD)
        end_date: Optional filter (format: YYYY-MM-DD)
    
    Returns:
        JSON with metrics for each campaign:
        - ctr_percent: Click-Through Rate as percentage
        - cpc: Cost Per Click
        - rpc: Revenue Per Click
        - conversion_rate_percent: Percentage of clicks that convert
        - total_impressions, clicks, revenue, ad_spend
        - roas: Return on Ad Spend
    
    Example:
        calculate_marketing_metrics('data/marketing_campaigns_production.csv', 
                                   'Growth Campaign A')
        → {
            'campaign': 'Growth Campaign A',
            'ctr_percent': 5.5,
            'cpc': 1.23,
            'rpc': 5.50,
            'conversion_rate': 9.94,
            'roas': 4.13,
            'impressions': 281000,
            'clicks': 15455,
            ...
        }
    
    Constraints:
        - CSV must have all required columns
        - Dates must be valid (YYYY-MM-DD format)
        - Campaign names are case-sensitive
    """
    
    import pandas as pd
    import json
    
    try:
        # STEP 1: LOAD AND VALIDATE DATA
        df = pd.read_csv(filepath)
        
        # Check required columns
        required_cols = ['date', 'campaign_name', 'channel', 'impressions', 
                        'clicks', 'conversions', 'revenue', 'ad_spend', 'reach']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            return json.dumps({
                "error": f"Missing columns: {missing_cols}",
                "available_columns": list(df.columns)
            })
        
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # STEP 2: FILTER DATA
        filtered_df = df.copy()
        
        # Filter by campaign
        if campaign != "all":
            filtered_df = filtered_df[filtered_df['campaign_name'] == campaign]
            if filtered_df.empty:
                return json.dumps({
                    "error": f"Campaign '{campaign}' not found",
                    "available_campaigns": df['campaign_name'].unique().tolist()
                })
        
        # Filter by channel
        if channel != "all":
            filtered_df = filtered_df[filtered_df['channel'] == channel]
            if filtered_df.empty:
                return json.dumps({
                    "error": f"Channel '{channel}' not found",
                    "available_channels": df['channel'].unique().tolist()
                })
        
        # Filter by date range
        if start_date:
            filtered_df = filtered_df[filtered_df['date'] >= pd.to_datetime(start_date)]
        if end_date:
            filtered_df = filtered_df[filtered_df['date'] <= pd.to_datetime(end_date)]
        
        if filtered_df.empty:
            return json.dumps({
                "error": "No data found with provided filters"
            })
        
        # STEP 3: CALCULATE METRICS
        results = []
        
        # Group by campaign (and channel if specified)
        if campaign == "all":
            group_cols = ['campaign_name']
        else:
            group_cols = ['campaign_name']
        
        for camp in filtered_df['campaign_name'].unique():
            camp_data = filtered_df[filtered_df['campaign_name'] == camp]
            
            # Sum up metrics
            total_impressions = camp_data['impressions'].sum()
            total_clicks = camp_data['clicks'].sum()
            total_conversions = camp_data['conversions'].sum()
            total_revenue = camp_data['revenue'].sum()
            total_ad_spend = camp_data['ad_spend'].sum()
            total_reach = camp_data['reach'].sum()
            
            # Validate we have data
            if total_clicks == 0:
                continue  # Skip campaigns with no clicks
            
            # Calculate metrics
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            cpc = total_ad_spend / total_clicks if total_clicks > 0 else 0
            rpc = total_revenue / total_clicks if total_clicks > 0 else 0
            conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
            roas = total_revenue / total_ad_spend if total_ad_spend > 0 else 0
            
            # Performance assessment
            if ctr > 5:
                ctr_assessment = "Excellent"
            elif ctr > 3.5:
                ctr_assessment = "Good"
            elif ctr > 2:
                ctr_assessment = "Average"
            else:
                ctr_assessment = "Low"
            
            if roas > 3:
                roas_assessment = "Excellent ROI"
            elif roas > 1.5:
                roas_assessment = "Good ROI"
            else:
                roas_assessment = "Poor ROI"
            
            campaign_result = {
                    "campaign": str(camp),
                    "ctr_percent": float(round(ctr, 2)),
                    "cpc": float(round(cpc, 2)),
                    "rpc": float(round(rpc, 2)),
                    "conversion_rate_percent": float(round(conversion_rate, 2)),
                    "roas": float(round(roas, 2)),
                    "total_impressions": int(total_impressions.item()),
                    "total_clicks": int(total_clicks.item()),
                    "total_conversions": int(total_conversions.item()),
                    "total_revenue": float(round(total_revenue, 2)),
                    "total_ad_spend": float(round(total_ad_spend, 2)),
                    "total_reach": int(total_reach.item())
                }
            results.append(campaign_result)
        
        # STEP 4: RETURN RESULTS
        if not results:
            return json.dumps({"error": "No valid data to calculate metrics"})
        
        return json.dumps({
            "success": True,
            "metrics": results,
            "summary": {
                "total_campaigns": len(results),
                "total_revenue": sum(r['total_revenue'] for r in results),
                "total_ad_spend": sum(r['total_ad_spend'] for r in results),
                "average_ctr": round(sum(r['ctr_percent'] for r in results) / len(results), 2),
                "average_roas": round(sum(r['roas'] for r in results) / len(results), 2)
            }
        })
    
    except FileNotFoundError:
        return json.dumps({
            "error": f"File not found: {filepath}",
            "suggestion": "Check the file path is correct"
        })
    except Exception as e:
        return json.dumps({
            "error": f"Unexpected error: {str(e)}",
            "error_type": type(e).__name__
        })
    
