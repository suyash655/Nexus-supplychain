"""
Test graph engine directly
"""
import sys
sys.path.insert(0, 'backend')
import pandas as pd
from app.engines.graph_engine import SupplyChainGraph

# Create sample data
data = {
    'supplier': ['Global Logistics', 'Swift Source', 'Apex Supply', 'Global Logistics', 'Swift Source'],
    'sku': ['SKU-100', 'SKU-200', 'SKU-100', 'SKU-101', 'SKU-201'],
    'warehouse': ['WH-North', 'WH-South', 'WH-North', 'WH-North', 'WH-South'],
    'region': ['Region-1', 'Region-2', 'Region-1', 'Region-1', 'Region-3'],
    'delay_days': [4, 1, 7, 2, 1],
    'cost': [1200.50, 850.00, 1500.00, 1100.00, 900.00],
}

df = pd.DataFrame(data)
print("Sample DataFrame:")
print(df)

# Test graph engine
graph = SupplyChainGraph()
try:
    summary = graph.build_from_data(df)
    print("\nGraph Summary:")
    print(summary)
    
    print("\nResilience Metrics:")
    resilience = graph.get_resilience_metrics()
    print(resilience)
    
    print("\nCentrality Scores:")
    centrality = graph.get_centrality_scores()
    print(centrality)
    
    print("\nCritical Paths:")
    critical = graph.find_critical_paths()
    print(critical)
    
    print("\nDeep Tier Inference:")
    deep = graph.deep_tier_inference(df)
    print(deep)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
