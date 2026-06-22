import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from tools.metric_calculator import calculate_marketing_metrics

print("Testing metric calculator...")
result = calculate_marketing_metrics('data/marketing_campaigns_production.csv')
print("Result:")
print(result)