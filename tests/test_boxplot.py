import matplotlib
matplotlib.use('Agg')  # Use headless backend for testing

import matplotlib.pyplot as plt
import numpy as np
from hypothesis import given, settings, strategies as st
from hypothesis import assume, HealthCheck
import pytest

# Basic test with known data
def test_basic_boxplot():
    """Test basic boxplot functionality with known data"""
    data = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    ]
    fig, ax = plt.subplots()
    box = ax.boxplot(data)
    
    # Check that boxes, medians, and whiskers were created
    assert len(box['boxes']) == len(data)
    assert len(box['medians']) == len(data)
    assert len(box['whiskers']) == 2 * len(data)
    
    plt.close(fig)

# Test with outliers
def test_boxplot_outliers():
    """Test boxplot with outliers"""
    # Data with clear outliers
    data = [[1, 2, 3, 4, 5, 20, 3, 4, 5, 3]]
    
    fig, ax = plt.subplots()
    box = ax.boxplot(data)
    
    # Check that fliers (outliers) are present
    assert len(box['fliers']) == len(data)
    # Check that there are actual points in the outliers
    assert len(box['fliers'][0].get_data()[0]) > 0
    
    plt.close(fig)

# Test different orientations
def test_boxplot_horizontal():
    """Test horizontal boxplot orientation"""
    data = [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]
    
    fig, ax = plt.subplots()
    box = ax.boxplot(data, vert=False)
    
    # For horizontal orientation, the median line should be vertical
    for median in box['medians']:
        x_data = median.get_xdata()
        # In a horizontal boxplot, the x values of the median line should be the same
        assert x_data[0] == x_data[1]
    
    plt.close(fig)

# Test styling
def test_boxplot_styling():
    """Test boxplot styling options"""
    data = [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]
    
    fig, ax = plt.subplots()
    box = ax.boxplot(data, notch=True, patch_artist=True, 
                    boxprops=dict(facecolor='lightblue'),
                    medianprops=dict(color='red', linewidth=2))
    
    # Check that styling was applied
    # Use the actual RGB values that matplotlib assigns for lightblue
    actual_color = box['boxes'][0].get_facecolor()[0:3]
    # Just check that it's some shade of blue (higher blue component than red/green)
    assert actual_color[2] > actual_color[0]  # blue > red
    assert actual_color[2] > actual_color[1]  # blue > green
    assert box['medians'][0].get_color() == 'red'
    assert box['medians'][0].get_linewidth() == 2
    
    plt.close(fig)

# Test with NaN and Inf values
def test_boxplot_nan_inf():
    """Test boxplot with NaN and Inf values"""
    data = [[1, 2, np.nan, 4, np.inf, -np.inf, 7, 8, 9, 10]]
    
    fig, ax = plt.subplots()
    # This should not crash but may generate RuntimeWarning due to NaN/Inf values
    with pytest.warns(RuntimeWarning, match="invalid value encountered in reduce"):
        box = ax.boxplot(data)
    
    # Valid values should still create a box
    assert len(box['boxes']) == 1
    
    plt.close(fig)

# Test labels
def test_boxplot_labels():
    """Test boxplot with labels"""
    data = [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]]
    labels = ['Group A', 'Group B']
    
    fig, ax = plt.subplots()
    ax.boxplot(data, labels=labels)
    
    # Check that labels are set correctly
    tick_labels = [tick.get_text() for tick in ax.get_xticklabels()]
    assert 'Group A' in tick_labels
    assert 'Group B' in tick_labels
    
    plt.close(fig)

# Fuzz test with Hypothesis
@given(
    st.lists(
        st.lists(st.floats(min_value=0, max_value=100), min_size=10, max_size=50),
        min_size=1,
        max_size=5
    )
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow], deadline=None)
def test_boxplot_fuzz(data):
    # Avoid groups with too little spread or too few unique values
    assume(all(len(set(group)) > 3 and (max(group) - min(group)) > 1e-2 for group in data))

    fig, ax = plt.subplots()
    box = ax.boxplot(data)

    # Check that boxes were created (using the returned dict instead of patches)
    assert len(box['boxes']) == len(data)
    plt.close(fig)

# Test flat data
def test_boxplot_flat_data():
    """Test boxplot with flat data (no variance)"""
    data = [[1.0] * 10]  # Flat input with no variance
    
    fig, ax = plt.subplots()
    box = ax.boxplot(data)
    
    # Even with flat data, boxes should be created
    assert len(box['boxes']) == len(data)
    
    # The box should have zero height (Q1 = Q3)
    box_path = box['boxes'][0].get_path()
    box_vertices = box_path.vertices
    y_values = box_vertices[:, 1]
    # Get unique y values (there should be at most 2 for a flat box)
    unique_y = np.unique(y_values)
    assert len(unique_y) <= 2
    
    plt.close(fig)


# TEST CASES
# Basic boxplot functionality - A simple test with known data to verify basic boxplot rendering
# Boxplot with outliers - Test when data has clear outliers to ensure they're properly displayed
# Multiple boxplots - Test side-by-side boxplots with different configurations
# Testing styling options - Like colors, notch shapes, etc.
# Testing boxplot with NaN/Inf values - Similar to your bar chart tests
# Testing horizontal vs vertical orientation
# Testing labels and annotations

# =========================================================== test session starts ============================================================
# platform win32 -- Python 3.13.2, pytest-8.3.5, pluggy-1.5.0 -- C:\Github\Git_34wizrd\matplotlib-testing\env\Scripts\python.exe
# cachedir: .pytest_cache
# hypothesis profile 'default' -> database=DirectoryBasedExampleDatabase(WindowsPath('C:/Github/Git_34wizrd/matplotlib-testing/.hypothesis/examples'))
# Matplotlib: 3.10.1
# Freetype: 2.6.1
# rootdir: C:\Github\Git_34wizrd\matplotlib-testing
# plugins: hypothesis-6.130.8, cov-6.1.1, mpl-0.17.0
# collected 8 items

# tests/test_boxplot.py::test_basic_boxplot PASSED                                                                                      [ 12%]
# tests/test_boxplot.py::test_boxplot_outliers PASSED                                                                                   [ 25%]
# tests/test_boxplot.py::test_boxplot_horizontal PASSED                                                                                 [ 37%]
# tests/test_boxplot.py::test_boxplot_styling PASSED                                                                                    [ 50%]
# tests/test_boxplot.py::test_boxplot_nan_inf PASSED                                                                                    [ 62%]
# tests/test_boxplot.py::test_boxplot_labels PASSED                                                                                     [ 75%]
# tests/test_boxplot.py::test_boxplot_fuzz PASSED                                                                                       [ 87%]
# tests/test_boxplot.py::test_boxplot_flat_data PASSED                                                                                  [100%]

# ============================================================= warnings summary =============================================================
# tests/test_boxplot.py::test_boxplot_horizontal
#   C:\Github\Git_34wizrd\matplotlib-testing\tests\test_boxplot.py:49: PendingDeprecationWarning: vert: bool will be deprecated in a future version. Use orientation: {'vertical', 'horizontal'} instead.
#     box = ax.boxplot(data, vert=False)

# tests/test_boxplot.py::test_boxplot_labels
#   C:\Github\Git_34wizrd\matplotlib-testing\tests\test_boxplot.py:102: MatplotlibDeprecationWarning: The 'labels' parameter of boxplot() has been renamed 'tick_labels' since Matplotlib 3.9; support for the old name will be dropped in 3.11.
#     ax.boxplot(data, labels=labels)

# -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
# ====================================================== 8 passed, 2 warnings in 3.26s ======================================================= 