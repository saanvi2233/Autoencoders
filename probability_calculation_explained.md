# 🧬 Probability Calculation in Protein Function Prediction

## 📊 Complete Pipeline

```
Protein ESM2 Embedding → Neural Network → Logits → Sigmoid → Probabilities
     (256 dims)            (MLPModel)      (raw)     (σ)      [0, 1]
```

---

## 1️⃣ Neural Network Forward Pass

### Model Architecture
```python
Input: 256-dim ESM2 embedding
  ↓
Layer 1: Linear(256 → 512) → ReLU → Dropout(0.5)
  ↓
Layer 2: Linear(512 → 256) → ReLU → Dropout(0.5)
  ↓
Output: Linear(256 → 932)  [NO activation]
  ↓
Output: 932 raw logits (range: -∞ to +∞)
```

### Code
```python
logits = model(batch_x)  # Shape: (batch_size, 932)
```

**Logits Example** (for one protein):
```python
logits = [-3.2, 2.5, 0.1, -1.0, 4.3, ...]
# Raw neural network outputs (932 values)
# Can be any real number
```

---

## 2️⃣ Sigmoid Transformation (Logits → Probabilities)

### The Sigmoid Function
```
σ(z) = 1 / (1 + e^(-z))
```

### Code
```python
probs = torch.sigmoid(logits)  # Shape: (batch_size, 932)
```

### Transformation Table
| Logit (z) | Sigmoid(z) | Interpretation |
|-----------|------------|----------------|
| -5.0      | 0.007      | 0.7% - Almost impossible |
| -3.0      | 0.047      | 4.7% - Very unlikely |
| -1.0      | 0.269      | 26.9% - Unlikely |
| **0.0**   | **0.500**  | **50% - Neutral** |
| +1.0      | 0.731      | 73.1% - Likely |
| +3.0      | 0.953      | 95.3% - Very likely |
| +5.0      | 0.993      | 99.3% - Almost certain |

### Example Calculation
```python
logits = [-3.2, 2.5, 0.1, -1.0, 4.3]

probs = torch.sigmoid(logits)
# Result: [0.039, 0.924, 0.525, 0.269, 0.987]

# Interpretation:
# GO term 0: 3.9% probability (unlikely)
# GO term 1: 92.4% probability (very likely) ✓
# GO term 2: 52.5% probability (borderline)
# GO term 3: 26.9% probability (unlikely)
# GO term 4: 98.7% probability (very likely) ✓
```

---

## 3️⃣ Binary Predictions (Threshold = 0.5)

```python
y_pred = (probs > 0.5).astype(int)
# [0.039, 0.924, 0.525, 0.269, 0.987] → [0, 1, 1, 0, 1]
```

---

# 🎯 Hierarchical Consistency Loss

## What is `p_child - p_parent`?

### Biological Rule
```
IF protein has CHILD function
THEN protein MUST have PARENT function

Example:
- Child: "ribosome biogenesis" (GO:0042254)
- Parent: "translation" (GO:0006412)
- Root: "biological process" (GO:0008150)

Rule: Can't do ribosome biogenesis without doing translation!
```

### In Probability Terms
```
p_child ≤ p_parent  (ALWAYS!)

✅ Valid: p_child=0.3, p_parent=0.8  (child < parent)
✅ Valid: p_child=0.5, p_parent=0.5  (child = parent)
❌ Invalid: p_child=0.9, p_parent=0.4  (VIOLATION!)
```

---

## Mathematical Formulation

### Step 1: Find Maximum Parent Probability

For each GO term (child), find its parents from ancestor matrix A:

```python
# Remove self-connections
mask = A.clone()
mask.fill_diagonal_(0)

# For each child, find max probability among all parents
masked = preds.unsqueeze(2) * mask.unsqueeze(0)
parents_max, _ = masked.max(dim=2)  # Max parent prob per child
```

**Example**:
```
GO Hierarchy:
    A (root)
    ├── B (child of A)
    └── C (child of A and B)

Predictions: p_A=0.3, p_B=0.6, p_C=0.9

For GO:B → parents = [A] → parents_max = 0.3
For GO:C → parents = [A, B] → parents_max = max(0.3, 0.6) = 0.6
```

### Step 2: Calculate Violations

```python
violations = F.relu(p_child - p_parent + margin)
```

**This is `p_child - p_parent`!**

| p_child | p_parent | Difference | Violation |
|---------|----------|------------|-----------|
| 0.3     | 0.8      | -0.5       | **0.0** (no penalty) ✅ |
| 0.5     | 0.5      | 0.0        | **0.0** (no penalty) ✅ |
| **0.9** | **0.4**  | **+0.5**   | **0.5** (PENALIZED!) ❌ |

**F.relu()** = Only penalize **positive** violations (when child > parent)

```python
F.relu(p_child - p_parent) = max(0, p_child - p_parent)
```

### Step 3: Mean Loss Across Batch

```python
hierarchy_loss = violations.mean()
```

---

## Concrete Example

### Scenario
```
GO Hierarchy:
    GO:A (biological process)
    └── GO:B (translation)
        └── GO:C (ribosome biogenesis)

Ancestor Matrix A:
      A   B   C
  A [[1,  0,  0],   # A: only itself
  B  [1,  1,  0],   # B: has A and itself
  C  [1,  1,  1]]   # C: has A, B, and itself
```

### Model Predictions (BAD - violates hierarchy!)
```python
probs = [0.3, 0.6, 0.9]  # [p_A, p_B, p_C]
```

### Violation Calculation

**For GO:B** (child of A):
```python
p_child = 0.6  (GO:B)
p_parent = 0.3  (GO:A is only parent)

violation_B = max(0, 0.6 - 0.3) = 0.3  ❌ VIOLATION!
```

**For GO:C** (child of A and B):
```python
p_child = 0.9  (GO:C)
parents = [0.3 (A), 0.6 (B)]
p_parent = max(0.3, 0.6) = 0.6  (strongest parent)

violation_C = max(0, 0.9 - 0.6) = 0.3  ❌ VIOLATION!
```

**For GO:A** (root - no parents):
```python
violation_A = 0  (no parents to check)
```

### Total Loss
```python
violations = [0.0, 0.3, 0.3]
hierarchy_loss = mean([0.0, 0.3, 0.3]) = 0.2
```

---

## Why This Works

### Gradient Effect During Training

When `hierarchy_loss = 0.2`:
```python
total_loss = BCE_loss + λ_h × hierarchy_loss
total_loss = 0.234 + 0.5 × 0.2
total_loss = 0.334
```

**Backpropagation pushes**:
- **Decrease** `p_C` from 0.9 → ~0.6 (reduce child)
- **Increase** `p_B` from 0.6 → ~0.8 (boost parent)
- Result: `p_C ≤ p_B ≤ p_A` (respects hierarchy!)

### Training Progress

| Epoch | p_A  | p_B  | p_C  | Hierarchy Loss | Status |
|-------|------|------|------|----------------|--------|
| 0     | 0.3  | 0.6  | 0.9  | 0.200          | ❌ Violations |
| 5     | 0.4  | 0.7  | 0.8  | 0.075          | ⚠️ Small violation |
| 10    | 0.5  | 0.7  | 0.7  | 0.000          | ✅ Valid! |
| 20    | 0.6  | 0.8  | 0.8  | 0.000          | ✅ Valid! |

---

## Summary: What is `p_child - p_parent`?

**Definition**: The amount by which a child GO term's probability **exceeds** its parent's probability.

**Purpose**: Measures how much the model **violates** the biological hierarchy rule.

**Action**:
- When **positive** (child > parent) → Add penalty to loss → Model learns to fix it
- When **zero or negative** (child ≤ parent) → No penalty → Valid prediction

**Result**: Neural network learns to make **biologically consistent** predictions that respect the Gene Ontology hierarchy!

---

## Key Formula
```python
hierarchy_loss = mean(max(0, p_child - p_parent))
                      ↑              ↑
                  Only penalize   Violation
                  violations       amount
```

**With λ_h = 0.5**: The hierarchy constraint has moderate influence, balancing prediction accuracy (BCE loss) with biological validity (hierarchy loss).
