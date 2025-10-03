#!/usr/bin/env python
"""
Load and examine the DeepGO annotation files using multiple loading methods
This script loads the bp.pkl and mf.pkl files correctly with fallback methods
"""
import pickle
import pandas as pd
import numpy as np

print("=== Loading DeepGO Annotation Files ===\n")

def safe_load_pkl(filepath, description):
    """Safely load pickle files with multiple fallback methods"""
    print(f"Loading {description}...")
    
    # Method 1: Try numpy load first
    try:
        data = np.load(filepath, allow_pickle=True)
        print(f"✓ Successfully loaded {filepath} with numpy.load")
        return data
    except Exception as e:
        print(f"  numpy.load failed: {str(e)[:50]}...")
    
    # Method 2: Try direct pickle load
    try:
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        print(f"✓ Successfully loaded {filepath} with pickle.load")
        return data
    except Exception as e:
        print(f"  pickle.load failed: {str(e)[:50]}...")
    
    # Method 3: Try pandas with error handling
    try:
        data = pd.read_pickle(filepath)
        print(f"✓ Successfully loaded {filepath} with pandas.read_pickle")
        return data
    except Exception as e:
        print(f"  pandas.read_pickle failed: {str(e)[:50]}...")
    
    print(f"✗ Failed to load {filepath}")
    return None

def analyze_data(data, name):
    """Analyze the loaded data structure"""
    if data is None:
        return
    
    print(f"\n--- {name} Analysis ---")
    print(f"Type: {type(data)}")
    
    if hasattr(data, 'shape'):
        print(f"Shape: {data.shape}")
    elif hasattr(data, '__len__'):
        print(f"Length: {len(data)}")
    
    if hasattr(data, 'columns'):
        print(f"Columns: {list(data.columns)}")
        if 'functions' in data.columns:
            print(f"Sample functions (first 3):")
            for i, func in enumerate(data['functions'].head(3)):
                print(f"  {i+1}. {func}")
    elif hasattr(data, 'keys') and callable(data.keys):
        print(f"Keys: {list(data.keys())[:5]}")
    elif isinstance(data, (list, tuple)):
        print(f"First few items: {data[:3]}")

# Load all annotation files
files_to_load = [
    ('data/deepgo/bp.pkl', 'Biological Process annotations'),
    ('data/deepgo/mf.pkl', 'Molecular Function annotations'),
    ('data/deepgo/cc.pkl', 'Cellular Component annotations')
]

loaded_data = {}

for filepath, description in files_to_load:
    data = safe_load_pkl(filepath, description)
    if data is not None:
        category = filepath.split('/')[-1].replace('.pkl', '')
        loaded_data[category] = data
        analyze_data(data, description)

print(f"\n=== Summary ===")
print(f"Successfully loaded {len(loaded_data)} out of {len(files_to_load)} files")
if loaded_data:
    print(f"Available data: {list(loaded_data.keys())}")
    
    # Try to show total function counts
    total_functions = 0
    for name, data in loaded_data.items():
        if hasattr(data, '__len__'):
            count = len(data)
            print(f"  {name}: {count} items")
            total_functions += count
    
    if total_functions > 0:
        print(f"Total items across all categories: {total_functions}")

print(f"\n=== Loading Complete ===")

# Show how to access the data
if loaded_data:
    print(f"\n=== Usage Example ===")
    print("# Access the loaded data like this:")
    for name in loaded_data.keys():
        print(f"# {name}_data = loaded_data['{name}']")
    
    # Show actual example if bp is loaded
    if 'bp' in loaded_data:
        bp_data = loaded_data['bp']
        print(f"\n# Example: First item from BP data")
        if hasattr(bp_data, 'iloc'):
            print(f"# first_bp_function = bp_data.iloc[0]")
        elif hasattr(bp_data, '__getitem__'):
            try:
                print(f"# first_item = bp_data[0]")
                print(f"# Result: {bp_data[0] if len(bp_data) > 0 else 'No data'}")
            except:
                pass