import matplotlib
matplotlib.use('Agg')  # Use headless backend for testing

import matplotlib.pyplot as plt
import numpy as np
from hypothesis import given, settings, strategies as st
import pytest

# Strategy for valid coordinates (avoiding NaN, inf)
float_strategy = st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False)
# Strategy for positive floats for error values
positive_float = st.floats(min_value=0.1, max_value=100, allow_nan=False, allow_infinity=False)
# Strategy for lists of valid floats
coord_list = st.lists(float_strategy, min_size=3, max_size=20)
# Strategy for error values
error_list = st.lists(positive_float, min_size=3, max_size=20)

@given(st.lists(st.floats(min_value=0, max_value=100), min_size=10, max_size=100))
@settings(max_examples=100, deadline=None)
def test_errorbar(data):
    x_vals = list(range(len(data)))
    y_err = [5] * len(data)
    fig, ax = plt.subplots()
    ax.errorbar(x_vals, data, yerr=y_err)

    # Ensure that at least one line was plotted
    assert len(ax.lines) > 0

    plt.close(fig)

@given(coord_list, coord_list, error_list)
@settings(max_examples=50, deadline=None)
def test_errorbar_xerr(x_vals, y_vals, x_err):
    """Test error bars with x-axis errors using property-based testing."""
    # Make sure all lists are the same length by truncating to shortest
    min_len = min(len(x_vals), len(y_vals), len(x_err))
    x_vals, y_vals, x_err = x_vals[:min_len], y_vals[:min_len], x_err[:min_len]
    
    fig, ax = plt.subplots()
    ax.errorbar(x_vals, y_vals, xerr=x_err)
    
    # Check that error bars were created
    assert len(ax.lines) > 0
    
    plt.close(fig)

@given(coord_list, coord_list, error_list, error_list)
@settings(max_examples=50, deadline=None)
def test_errorbar_both_directions(x_vals, y_vals, x_err, y_err):
    """Test error bars in both x and y directions using property-based testing."""
    # Make sure all lists are the same length by truncating to shortest
    min_len = min(len(x_vals), len(y_vals), len(x_err), len(y_err))
    x_vals = x_vals[:min_len]
    y_vals = y_vals[:min_len]
    x_err = x_err[:min_len]
    y_err = y_err[:min_len]
    
    fig, ax = plt.subplots()
    ax.errorbar(x_vals, y_vals, xerr=x_err, yerr=y_err)
    
    # Check that error bars were created
    assert len(ax.lines) > 0
    
    plt.close(fig)

@given(coord_list, coord_list, error_list, error_list)
@settings(max_examples=50, deadline=None)
def test_errorbar_asymmetric(x_vals, y_vals, lower_err, upper_err):
    """Test asymmetric error bars using property-based testing."""
    # Make sure all lists are the same length
    min_len = min(len(x_vals), len(y_vals), len(lower_err), len(upper_err))
    x_vals = x_vals[:min_len]
    y_vals = y_vals[:min_len]
    lower_err = lower_err[:min_len]
    upper_err = upper_err[:min_len]
    
    # Create asymmetric errors
    y_err = [lower_err, upper_err]
    
    fig, ax = plt.subplots()
    ax.errorbar(x_vals, y_vals, yerr=y_err)
    
    # Check that error bars were created
    assert len(ax.lines) > 0
    
    plt.close(fig)

@given(
    coord_list, 
    coord_list, 
    error_list,
    st.sampled_from(['o', 's', '^', 'D', 'v']),  # Marker formats
    st.sampled_from(['red', 'blue', 'green', 'black']),  # Colors
    st.floats(min_value=0.5, max_value=5),  # Line widths
    st.integers(min_value=0, max_value=10)  # Cap sizes
)
@settings(max_examples=50, deadline=None)
def test_errorbar_formatting(x_vals, y_vals, y_err, marker, color, linewidth, capsize):
    """Test error bar formatting options using property-based testing."""
    # Make sure all lists are the same length
    min_len = min(len(x_vals), len(y_vals), len(y_err))
    x_vals = x_vals[:min_len]
    y_vals = y_vals[:min_len]
    y_err = y_err[:min_len]
    
    fig, ax = plt.subplots()
    ax.errorbar(
        x_vals, y_vals, yerr=y_err,
        fmt=marker,
        ecolor=color,
        elinewidth=linewidth,
        capsize=capsize
    )
    
    # Check that error bars were created
    assert len(ax.lines) > 0
    
    plt.close(fig)

# Edge cases are better tested with specific values, but we can use
# Hypothesis to generate some edge case scenarios
def test_errorbar_edge_cases():
    """Test error bar edge cases."""
    # Empty data
    fig, ax = plt.subplots()
    ax.errorbar([], [], yerr=[])
    plt.close(fig)
    
    # NaN values
    fig, ax = plt.subplots()
    x_vals = [1, 2, 3]
    y_vals = [10, np.nan, 30]
    y_err = [1, 1, 1]
    ax.errorbar(x_vals, y_vals, yerr=y_err)
    plt.close(fig)
    
    # Very large values
    fig, ax = plt.subplots()
    x_vals = [1, 2, 3]
    y_vals = [1e8, 2e8, 3e8]
    y_err = [1e7, 1e7, 1e7]
    ax.errorbar(x_vals, y_vals, yerr=y_err)
    plt.close(fig)

@given(st.integers(min_value=1, max_value=10))
@settings(max_examples=5, deadline=None)
def test_errorbar_extreme_values(size):
    """Test error bar with extreme values using property-based testing."""
    # Create arrays with very large and very small values
    x_vals = list(range(size))
    y_vals = [10**n for n in range(size)]
    y_err = [10**(n-2) for n in range(size)]
    
    fig, ax = plt.subplots()
    ax.errorbar(x_vals, y_vals, yerr=y_err)
    plt.close(fig)
    
    # Very small values
    y_vals = [10**-n for n in range(1, size+1)]
    y_err = [10**-(n+2) for n in range(1, size+1)]
    
    fig, ax = plt.subplots()
    ax.errorbar(x_vals, y_vals, yerr=y_err)
    plt.close(fig)
    
# =========================================================== test session starts ============================================================
# platform win32 -- Python 3.13.2, pytest-8.3.5, pluggy-1.5.0 -- C:\Github\Git_34wizrd\matplotlib-testing\env\Scripts\python.exe
# cachedir: .pytest_cache
# hypothesis profile 'default' -> database=DirectoryBasedExampleDatabase(WindowsPath('C:/Github/Git_34wizrd/matplotlib-testing/.hypothesis/examples'))
# Matplotlib: 3.10.1
# Freetype: 2.6.1
# rootdir: C:\Github\Git_34wizrd\matplotlib-testing
# plugins: hypothesis-6.130.8, cov-6.1.1, mpl-0.17.0
# collected 7 items

# tests/test_errorbar.py::test_errorbar PASSED                                                                                          [ 14%]
# tests/test_errorbar.py::test_errorbar_xerr PASSED                                                                                     [ 28%]
# tests/test_errorbar.py::test_errorbar_both_directions PASSED                                                                          [ 42%]
# tests/test_errorbar.py::test_errorbar_asymmetric PASSED                                                                               [ 57%]
# tests/test_errorbar.py::test_errorbar_formatting PASSED                                                                               [ 71%]
# tests/test_errorbar.py::test_errorbar_edge_cases PASSED                                                                               [ 85%]
# tests/test_errorbar.py::test_errorbar_extreme_values PASSED                                                                           [100%]

# ============================================================ 7 passed in 4.26s ============================================================= 