#!/usr/bin/env python
"""
Generate synthetic data files required by DeepGO get_data.py
This creates mock data to demonstrate the complete pipeline.
"""
import pandas as pd
import numpy as np
import pickle
import os
from itertools import product

print("=== Generating Synthetic DeepGO Data Files ===\n")

# Create data/deepgo directory if it doesn't exist
os.makedirs('data/deepgo', exist_ok=True)

# 1. Generate ngrams.pkl - N-gram vocabulary for protein sequences
print("1. Generating ngrams.pkl...")

# Standard amino acids
amino_acids = ['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 
               'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y']

# Generate 3-grams (triplets) of amino acids
ngram_length = 3
ngrams = [''.join(combo) for combo in product(amino_acids, repeat=ngram_length)]

# Create ngrams dataframe
ngrams_df = pd.DataFrame({'ngrams': ngrams[:1000]})  # Use first 1000 for efficiency
ngrams_df.to_pickle('data/deepgo/ngrams.pkl')
print(f"   ✓ Created {len(ngrams_df)} n-grams of length {ngram_length}")

# 2. Generate swissprot_exp.pkl - Protein sequences and annotations
print("2. Generating swissprot_exp.pkl...")

np.random.seed(42)  # For reproducible results

# Generate synthetic protein data
num_proteins = 1000
protein_data = []

# Load existing GO functions for realistic annotations
bp_df = pd.read_pickle('data/deepgo/bp.pkl')
mf_df = pd.read_pickle('data/deepgo/mf.pkl')
cc_df = pd.read_pickle('data/deepgo/cc.pkl')

all_go_terms = (list(bp_df['functions']) + 
                list(mf_df['functions']) + 
                list(cc_df['functions']))

for i in range(num_proteins):
    # Generate random protein sequence (50-500 amino acids)
    seq_length = np.random.randint(50, 501)
    sequence = ''.join(np.random.choice(amino_acids, seq_length))
    
    # Generate protein identifier
    protein_id = f"P{i:05d}"
    accession = f"ACC{i:05d}"
    
    # Generate GO annotations (1-5 terms per protein)
    num_annots = np.random.randint(1, 6)
    selected_terms = np.random.choice(all_go_terms, num_annots, replace=False)
    
    # Format annotations as required by DeepGO (GO_ID|EXP_CODE)
    exp_codes = ['EXP', 'IDA', 'IPI', 'IMP', 'IGI', 'IEP']  # Experimental evidence codes
    annotations = [f"{term}|{np.random.choice(exp_codes)}" for term in selected_terms]
    
    protein_data.append({
        'proteins': protein_id,
        'accessions': accession,
        'sequences': sequence,
        'annots': annotations
    })

swissprot_df = pd.DataFrame(protein_data)
swissprot_df.to_pickle('data/deepgo/swissprot_exp.pkl')
print(f"   ✓ Created {len(swissprot_df)} protein entries with sequences and annotations")

# 3. Generate graph_new_embeddings.pkl - Protein network embeddings
print("3. Generating graph_new_embeddings.pkl...")

# Generate random embeddings for proteins (256-dimensional vectors)
embedding_dim = 256
embeddings_data = []

for i in range(num_proteins):
    accession = f"ACC{i:05d}"
    # Generate random embedding vector
    embedding = np.random.normal(0, 1, embedding_dim).astype(np.float32)
    
    embeddings_data.append({
        'accessions': accession,
        'embeddings': embedding
    })

embeddings_df = pd.DataFrame(embeddings_data)
embeddings_df.to_pickle('data/graph_new_embeddings.pkl')
print(f"   ✓ Created {len(embeddings_df)} protein embeddings ({embedding_dim}D)")

# 4. Generate protein_orgs.pkl - Organism information
print("4. Generating protein_orgs.pkl...")

# Create organism mapping (focus on human proteins for simplicity)
org_data = []
for i in range(num_proteins):
    protein_id = f"P{i:05d}"
    # Mostly human (9606), some mouse (10090), some other
    if i < 800:
        org_id = '9606'  # Human
    elif i < 950:
        org_id = '10090'  # Mouse
    else:
        org_id = '7227'   # Fruit fly
    
    org_data.append({
        'proteins': protein_id,
        'orgs': org_id
    })

orgs_df = pd.DataFrame(org_data)
orgs_df.to_pickle('data/protein_orgs.pkl')
print(f"   ✓ Created organism mappings for {len(orgs_df)} proteins")

print("\n=== Data Generation Complete ===")
print("Generated files:")
print("  ✓ data/deepgo/ngrams.pkl")
print("  ✓ data/deepgo/swissprot_exp.pkl")  
print("  ✓ data/graph_new_embeddings.pkl")
print("  ✓ data/protein_orgs.pkl")
print("\nYou can now run get_data.py to generate training/test datasets!")