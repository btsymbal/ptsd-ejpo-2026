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

## Python Environment

**IMPORTANT**: When running Python scripts or notebooks in this repository, always use the **jupyter_env** conda environment.

### Running Python Scripts

Use the full path to the Python interpreter:
```bash
/opt/anaconda3/envs/jupyter_env/bin/python script_name.py
```

### Why This Matters

- The `jupyter_env` environment contains all required dependencies (pandas, numpy, matplotlib, etc.)
- Using the system Python or wrong environment will result in missing packages or version conflicts
- All data analysis and preprocessing scripts depend on this environment
