# Project Guidelines for Claude

## Jupyter Notebooks

**IMPORTANT**: When working with Jupyter notebooks or performing data analysis in this repository, always use the **percent format (.py)** instead of traditional .ipynb files.

### Notebook Format Rules

1. **File Extension**: Use `.py` files with percent format markers
2. **Cell Markers**:
   - Code cells: `# %%`
   - Markdown cells: `# %% [markdown]`
3. **Benefits**:
   - Git-friendly (better diffs and merges)
   - Works as regular Python files
   - Compatible with VS Code, PyCharm, Jupyter, and other tools

### Example Structure

```python
# %% [markdown]
# # Analysis Title

# %% [markdown]
# ## Section Header

# %%
# Code cell
import pandas as pd
df = pd.read_csv('data.csv')

# %%
# Another code cell
df.head()
```

### When This Applies

- Creating new analysis notebooks
- Performing exploratory data analysis
- Hypothesis testing
- Any statistical or data science work
- Visualization and reporting

**Never create .ipynb files** unless explicitly requested otherwise.
