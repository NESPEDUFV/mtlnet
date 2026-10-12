# category_linear

## Why This
- Diagnostic linear probe: single nn.Linear(input_dim, num_classes) with
  no hidden layers. If this matches deeper heads, it proves the shared
  backbone is doing all the representational work -- the ideal outcome
  for a well-trained MTL system.

## Runtime Mapping
- Model registry key: `category_linear`
- Runtime class: `models.category.category_linear.head.CategoryHeadLinear`


## Evidence Status
- Current: `implemented`
- Last Reviewed: `2026-04-13`

## Sources
- In-repo implementation: `src/models/category/category_linear/head.py`
