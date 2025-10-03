#!/usr/bin/env python
"""
Simple script to load and examine DeepGO annotation files
Based on user's request to load bp.pkl and mf.pkl
"""
import pandas as pd

print("Loading DeepGO annotation files...")

# Load the annotation files
bp_data = pd.read_pickle('deepgo/data/deepgo/bp.pkl')
mf_data = pd.read_pickle('deepgo/data/deepgo/mf.pkl')

print(f"✓ Loaded bp.pkl: {len(bp_data)} Biological Process functions")
print(f"✓ Loaded mf.pkl: {len(mf_data)} Molecular Function annotations")

print("\n=== Biological Process (BP) Data ===")
print(f"Shape: {bp_data.shape}")
print(f"Columns: {list(bp_data.columns)}")
print("First 5 functions:")
for i, func in enumerate(bp_data['functions'].head(5)):
    print(f"  {i+1}. {func}")

print("\n=== Molecular Function (MF) Data ===") 
print(f"Shape: {mf_data.shape}")
print(f"Columns: {list(mf_data.columns)}")
print("First 5 functions:")
for i, func in enumerate(mf_data['functions'].head(5)):
    print(f"  {i+1}. {func}")

print(f"\n=== Summary ===")
print(f"Total BP functions: {len(bp_data)}")
print(f"Total MF functions: {len(mf_data)}")
print(f"Combined total: {len(bp_data) + len(mf_data)}")

# Make data available for further use
print(f"\n=== Data Access ===")
print("The loaded data is available as:")
print("  bp_data - Biological Process annotations")
print("  mf_data - Molecular Function annotations")
print("\nExample usage:")
print("  bp_data.head()           # View first few rows")
print("  mf_data['functions'][0]  # Get first function ID")
print("  len(bp_data)             # Count of BP functions")