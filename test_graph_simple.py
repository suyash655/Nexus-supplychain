"""
Simple graph engine test
"""
import sys
sys.path.insert(0, 'backend')

try:
    import networkx as nx
    print("NetworkX imported successfully")
    print(f"NetworkX version: {nx.__version__}")
except Exception as e:
    print(f"NetworkX import failed: {e}")

try:
    from app.engines.graph_engine import SupplyChainGraph
    print("SupplyChainGraph imported successfully")
    
    graph = SupplyChainGraph()
    print("Graph instance created")
    
    # Test basic functionality with complete data
    import pandas as pd
    data = {
        'supplier': ['A', 'B', 'A'], 
        'sku': ['SKU1', 'SKU2', 'SKU1'], 
        'warehouse': ['WH1', 'WH2', 'WH1'],
        'region': ['R1', 'R2', 'R1'],
        'delay_days': [1, 2, 3], 
        'cost': [100, 200, 150]
    }
    df = pd.DataFrame(data)
    print(f"Test DataFrame:\n{df}")
    
    print("Building graph...")
    import time
    start = time.time()
    
    result = graph.build_from_data(df)
    
    elapsed = time.time() - start
    print(f"Graph build completed in {elapsed:.2f} seconds")
    print(f"Graph build result: {result}")
    
    print(f"Graph nodes: {graph.G.number_of_nodes()}")
    print(f"Graph edges: {graph.G.number_of_edges()}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
