# quick_test_tool4.py

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.trend_analyzer import analyze_trends
import json

print("Testing Tool 4: Trend Analyzer...")
print("-" * 50)

# Test 1: Analyze trend for a specific campaign
print("\n📊 Test 1: Analyzing CTR trend for Growth Campaign A...")
result = analyze_trends(
    filepath='data/marketing_campaigns_production.csv',
    campaign='Growth Campaign A',
    metric='ctr',
    window_days=7
)

data = json.loads(result)
print(json.dumps(data, indent=2))

# Verify it worked
assert data.get('success') == True, "Tool failed!"
assert 'trend' in data, "Missing trend data!"
assert data['trend'] in ['improving', 'declining', 'stable'], "Invalid trend!"
print("✅ Test 1 PASSED!")

# Test 2: Analyze ROAS trend
print("\n📈 Test 2: Analyzing ROAS trend for Email Blast...")
result = analyze_trends(
    filepath='data/marketing_campaigns_production.csv',
    campaign='Email Blast',
    metric='roas',
    window_days=7
)

data = json.loads(result)
print(f"Trend: {data['trend_assessment']}")
print(f"Recommendation: {data['recommendation']}")

assert data.get('success') == True, "Tool failed!"
assert 'recommendation' in data, "Missing recommendation!"
print("✅ Test 2 PASSED!")

# Test 3: All campaigns trend
print("\n🔍 Test 3: Analyzing conversion rate for all campaigns...")
result = analyze_trends(
    filepath='data/marketing_campaigns_production.csv',
    campaign='all',
    metric='conversion_rate',
    window_days=7
)

data = json.loads(result)
print(f"Overall trend: {data['trend_assessment']}")
print(f"Change: {data['change_percent']}%")

assert data.get('success') == True, "Tool failed!"
print("✅ Test 3 PASSED!")

print("\n" + "=" * 50)
print("✅ ALL TOOL 4 TESTS PASSED!")
print("=" * 50)