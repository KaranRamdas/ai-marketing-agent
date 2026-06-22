# tools/roi_calculator.py

from crewai.tools import tool
import pandas as pd
import json

@tool
def calculate_roi(
    filepath: str,
    campaign: str = "all"
) -> str:
    """
    Calculate Return on Investment (ROI) and payback period for campaigns.
    
    Use this when you need to measure the profitability and efficiency
    of marketing spend.
    
    Args:
        filepath: Path to CSV file with marketing data
        campaign: Campaign to analyze ('all' for all campaigns)
    
    Returns:
        JSON with:
        - roi_percent: Return on Investment as percentage
        - net_profit: Revenue minus ad spend
        - payback_days: Estimated days to recover investment
        - profit_margin: (Revenue - Spend) / Revenue
    
    Example:
        calculate_roi('data.csv', 'Growth Campaign A')
    """
    
    try:
        # LOAD DATA
        df = pd.read_csv(filepath)
        
        required_cols = ['date', 'campaign_name', 'revenue', 'ad_spend']
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
        
        # CALCULATE ROI FOR EACH CAMPAIGN
        results = []
        
        for camp in df['campaign_name'].unique():
            camp_data = df[df['campaign_name'] == camp]
            
            # Calculate totals
            total_revenue = float(camp_data['revenue'].sum())
            total_spend = float(camp_data['ad_spend'].sum())
            
            # Calculate metrics
            profit = total_revenue - total_spend
            roi_percent = (profit / total_spend * 100) if total_spend > 0 else 0
            profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else 0
            roas = total_revenue / total_spend if total_spend > 0 else 0
            
            # Calculate payback days (when cumulative profit becomes positive)
            camp_data_sorted = camp_data.sort_values('date')
            cumulative_profit = 0
            payback_days = None
            
            for _, row in camp_data_sorted.iterrows():
                daily_profit = float(row['revenue']) - float(row['ad_spend'])
                cumulative_profit += daily_profit
                
                if cumulative_profit > 0 and payback_days is None:
                    days_diff = (row['date'] - camp_data_sorted['date'].min()).days
                    payback_days = float(days_diff)
            
            # Build result object
            campaign_result = {
                "campaign": str(camp),
                "total_revenue": float(round(total_revenue, 2)),
                "total_ad_spend": float(round(total_spend, 2)),
                "net_profit": float(round(profit, 2)),
                "roi_percent": float(round(roi_percent, 2)),
                "profit_margin_percent": float(round(profit_margin, 2)),
                "roas": float(round(roas, 2)),
                "payback_days": float(round(payback_days, 1)) if payback_days is not None else None
            }
            
            results.append(campaign_result)
        
        # CALCULATE SUMMARY
        total_all_revenue = sum(r['total_revenue'] for r in results)
        total_all_spend = sum(r['total_ad_spend'] for r in results)
        total_all_profit = sum(r['net_profit'] for r in results)
        avg_roi = sum(r['roi_percent'] for r in results) / len(results) if results else 0
        avg_roas = sum(r['roas'] for r in results) / len(results) if results else 0
        
        return json.dumps({
            "success": True,
            "roi_results": results,
            "summary": {
                "total_revenue": float(round(total_all_revenue, 2)),
                "total_spend": float(round(total_all_spend, 2)),
                "total_profit": float(round(total_all_profit, 2)),
                "average_roi_percent": float(round(avg_roi, 2)),
                "average_roas": float(round(avg_roas, 2))
            }
        })
    
    except FileNotFoundError:
        return json.dumps({
            "error": f"File not found: {filepath}"
        })
    except Exception as e:
        return json.dumps({
            "error": f"Error calculating ROI: {str(e)}",
            "error_type": type(e).__name__
        })