# quick_test_tool2.py

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.campaign_comparator import compare_campaigns
import json

print("Testing Tool 2: Campaign Comparator...")
result = compare_campaigns(
    filepath='data/marketing_campaigns_production.csv',
    campaign_names='Growth Campaign A,Growth Campaign B'  # ← Comma-separated string
)

data = json.loads(result)
print("Result:")
print(json.dumps(data, indent=2))

# Verify it worked
assert data.get('success') == True, "Tool failed!"
assert 'comparison' in data, "Missing comparison data!"
print("\n✅ Tool 2 PASSED!")