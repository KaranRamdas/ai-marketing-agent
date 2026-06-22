# quick_test_tool6.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from tools.budget_recommender import recommend_budget_allocation
import json

print("Testing Tool 6: Budget Recommender...")
print("-" * 50)

# Test 1: Recommendations based on ROAS (no budget allocation)
print("\n💡 Test 1: Budget recommendations based on ROAS...")
result = recommend_budget_allocation(
    filepath='data/marketing_campaigns_production.csv',
    performance_metric='roas'
)

data = json.loads(result)
print(f"Total Campaigns: {data['total_campaigns']}")
print(f"Summary: {data['summary']}")

print("\nRecommendations:")
for rec in data['recommendations']:
    print(f"  #{rec['rank']} {rec['campaign']}")
    print(f"     Action: {rec['action']} (Priority: {rec['priority']})")
    print(f"     ROAS: {rec['metric_value']}")
    print(f"     Reasoning: {rec['reasoning']}")
    print()

# Verify it worked
assert data.get('success') == True, "Tool failed!"
assert 'recommendations' in data, "Missing recommendations!"
assert 'summary' in data, "Missing summary!"
print("✅ Test 1 PASSED!")

# Test 2: Recommendations with budget allocation
print("\n💰 Test 2: Budget allocation recommendations (total budget: $50,000)...")
result = recommend_budget_allocation(
    filepath='data/marketing_campaigns_production.csv',
    total_budget=50000.0,
    performance_metric='roas'
)

data = json.loads(result)
print(f"\nTotal Budget to Allocate: $50,000")
print("\nBudget Allocation:")
if data['budget_allocation']:
    total_allocated = 0
    for allocation in data['budget_allocation']:
        print(f"  {allocation['campaign']}: ${allocation['recommended_budget']:,.2f} ({allocation['percentage']:.1f}%)")
        if allocation['campaign'] != 'NEW_CAMPAIGNS_TEST':
            total_allocated += allocation['recommended_budget']
    print(f"  Total Allocated: ${total_allocated:,.2f}")

assert data.get('success') == True, "Tool failed!"
assert data['budget_allocation'] is not None, "Missing budget allocation!"
print("✅ Test 2 PASSED!")

# Test 3: Recommendations based on CTR
print("\n📈 Test 3: Budget recommendations based on CTR...")
result = recommend_budget_allocation(
    filepath='data/marketing_campaigns_production.csv',
    total_budget=75000.0,
    performance_metric='ctr'
)

data = json.loads(result)
print(f"\nMetric Used: CTR")
print(f"Campaigns to SCALE: {data['summary']['scale_count']}")
print(f"Campaigns to MAINTAIN: {data['summary']['maintain_count']}")
print(f"Campaigns to PAUSE/OPTIMIZE: {data['summary']['pause_count']}")

print("\nTop 3 Performers by CTR:")
for rec in data['recommendations'][:3]:
    print(f"  {rec['rank']}. {rec['campaign']} - {rec['metric_value']:.2f}% CTR")

assert data.get('success') == True, "Tool failed!"
print("✅ Test 3 PASSED!")

# Test 4: Recommendations based on conversion rate
print("\n🎯 Test 4: Budget recommendations based on conversion rate...")
result = recommend_budget_allocation(
    filepath='data/marketing_campaigns_production.csv',
    performance_metric='conversion_rate'
)

data = json.loads(result)
print(f"\nMetric Used: Conversion Rate")
print("\nRanking by Conversion Rate:")
for rec in data['recommendations']:
    print(f"  #{rec['rank']} {rec['campaign']}: {rec['metric_value']:.2f}% - {rec['action']}")

print(f"\nPotential Actions:")
print(f"  - Scale: {data['summary']['scale_count']} campaign(s)")
print(f"  - Maintain: {data['summary']['maintain_count']} campaign(s)")
print(f"  - Pause/Optimize: {data['summary']['pause_count']} campaign(s)")

assert data.get('success') == True, "Tool failed!"
print("✅ Test 4 PASSED!")

print("\n" + "=" * 50)
print("✅ ALL TOOL 6 TESTS PASSED!")
print("=" * 50)