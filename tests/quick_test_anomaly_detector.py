# quick_test_tool5.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from tools.anomaly_detector import detect_anomalies
import json

print("Testing Tool 5: Anomaly Detector...")
print("-" * 50)

# Test 1: Detect ROAS anomalies
print("\n🎯 Test 1: Detecting ROAS anomalies for Growth Campaign A...")
result = detect_anomalies(
    filepath='data/marketing_campaigns_production.csv',
    campaign='Growth Campaign A',
    metric='roas',
    sensitivity=2.0
)

data = json.loads(result)
print(f"Average ROAS: {data['average_value']}")
print(f"Std Dev: {data['std_dev']}")
print(f"Anomalies Found: {data['anomalies_found']}")
print(f"\nInsights: {data['insights']}")

if data['anomalies']:
    print("\nAnomalies:")
    for anomaly in data['anomalies']:
        print(f"  {anomaly['date']}: {anomaly['type']} - {anomaly['value']} ({anomaly['percentage_change']:+.1f}%)")

# Verify it worked
assert data.get('success') == True, "Tool failed!"
assert 'anomalies' in data, "Missing anomalies data!"
assert 'insights' in data, "Missing insights!"
print("✅ Test 1 PASSED!")

# Test 2: Detect CTR anomalies
print("\n📊 Test 2: Detecting CTR anomalies for Retargeting Campaign...")
result = detect_anomalies(
    filepath='data/marketing_campaigns_production.csv',
    campaign='Retargeting Campaign',
    metric='ctr',
    sensitivity=2.0
)

data = json.loads(result)
print(f"Anomalies Found: {data['anomalies_found']}")
print(f"Insights: {data['insights']}")

assert data.get('success') == True, "Tool failed!"
print("✅ Test 2 PASSED!")

# Test 3: Detect conversion rate anomalies with higher sensitivity
print("\n🔍 Test 3: Detecting conversion rate anomalies (high sensitivity)...")
result = detect_anomalies(
    filepath='data/marketing_campaigns_production.csv',
    campaign='all',
    metric='conversion_rate',
    sensitivity=1.5  # Higher sensitivity = more anomalies
)

data = json.loads(result)
print(f"Total Anomalies (sensitivity=1.5): {data['anomalies_found']}")
print(f"Average Value: {data['average_value']:.2f}%")

assert data.get('success') == True, "Tool failed!"
print("✅ Test 3 PASSED!")

# Test 4: Detect CPC anomalies
print("\n💰 Test 4: Detecting CPC anomalies...")
result = detect_anomalies(
    filepath='data/marketing_campaigns_production.csv',
    campaign='Email Blast',
    metric='cpc',
    sensitivity=2.0
)

data = json.loads(result)
print(f"Average CPC: ${data['average_value']:.2f}")
print(f"Anomalies: {data['anomalies_found']}")
print(f"Insights: {data['insights']}")

assert data.get('success') == True, "Tool failed!"
print("✅ Test 4 PASSED!")

print("\n" + "=" * 50)
print("✅ ALL TOOL 5 TESTS PASSED!")
print("=" * 50)