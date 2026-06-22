# quick_test_tool3.py

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.roi_calculator import calculate_roi
import json

print("Testing Tool 3: ROI Calculator...")
print("-" * 50)

# Test 1: Calculate ROI for specific campaign
print("\n💰 Test 1: Calculating ROI for Growth Campaign A...")
result = calculate_roi(
    filepath='data/marketing_campaigns_production.csv',
    campaign='Growth Campaign A'
)

data = json.loads(result)
print(json.dumps(data, indent=2))

# Verify it worked
assert data.get('success') == True, "Tool failed!"
assert 'roi_results' in data, "Missing ROI results!"
print("✅ Test 1 PASSED!")

# Test 2: Calculate ROI for all campaigns
print("\n📊 Test 2: Calculating ROI for all campaigns...")
result = calculate_roi(
    filepath='data/marketing_campaigns_production.csv',
    campaign='all'
)

data = json.loads(result)
print(f"Total Revenue: ${data['summary']['total_revenue']:,.2f}")
print(f"Total Spend: ${data['summary']['total_spend']:,.2f}")
print(f"Total Profit: ${data['summary']['total_profit']:,.2f}")
print(f"Average ROI: {data['summary']['average_roi_percent']}%")
print(f"Average ROAS: {data['summary']['average_roas']}")

print("\nROI by Campaign:")
for result_item in data['roi_results']:
    print(f"  {result_item['campaign']}")
    print(f"    Revenue: ${result_item['total_revenue']:,.2f}")
    print(f"    Spend: ${result_item['total_ad_spend']:,.2f}")
    print(f"    Profit: ${result_item['net_profit']:,.2f}")
    print(f"    ROI: {result_item['roi_percent']:.2f}%")
    print(f"    Payback: {result_item['payback_days']} days")
    print()

# Verify it worked
assert data.get('success') == True, "Tool failed!"
assert len(data['roi_results']) > 0, "No results!"
print("✅ Test 2 PASSED!")

# Test 3: Identify best ROI campaign
print("\n🏆 Test 3: Finding best ROI campaign...")
result = calculate_roi(
    filepath='data/marketing_campaigns_production.csv',
    campaign='all'
)

data = json.loads(result)
best_roi = max(data['roi_results'], key=lambda x: x['roi_percent'])
worst_roi = min(data['roi_results'], key=lambda x: x['roi_percent'])

print(f"Best ROI: {best_roi['campaign']} ({best_roi['roi_percent']:.2f}%)")
print(f"Worst ROI: {worst_roi['campaign']} ({worst_roi['roi_percent']:.2f}%)")

assert data.get('success') == True, "Tool failed!"
print("✅ Test 3 PASSED!")

# Test 4: High profit vs high ROI
print("\n💡 Test 4: Comparing profit vs ROI...")
result = calculate_roi(
    filepath='data/marketing_campaigns_production.csv',
    campaign='all'
)

data = json.loads(result)
by_profit = sorted(data['roi_results'], key=lambda x: x['net_profit'], reverse=True)
by_roi = sorted(data['roi_results'], key=lambda x: x['roi_percent'], reverse=True)

print("Top 3 by Total Profit:")
for i, result_item in enumerate(by_profit[:3], 1):
    print(f"  {i}. {result_item['campaign']}: ${result_item['net_profit']:,.2f}")

print("\nTop 3 by ROI Percentage:")
for i, result_item in enumerate(by_roi[:3], 1):
    print(f"  {i}. {result_item['campaign']}: {result_item['roi_percent']:.2f}%")

assert data.get('success') == True, "Tool failed!"
print("✅ Test 4 PASSED!")

print("\n" + "=" * 50)
print("✅ ALL TOOL 3 TESTS PASSED!")
print("=" * 50)