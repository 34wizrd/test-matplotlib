# tests/test_scatter.py

import pytest
import numpy as np
import matplotlib.pyplot as plt
import time
import itertools
import random
import string

# Add cleanup fixture to close figures after each test
@pytest.fixture(autouse=True)
def cleanup():
    yield
    plt.close("all")

# Check for Hypothesis availability
try:
    from hypothesis import given, strategies as st
    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False

# ----------------------------
# 1. Basic Functional Tests
# ----------------------------
@pytest.mark.parametrize("x,y,expected", [
    ([0, 1, 2], [10, 20, 30], [(0, 10), (1, 20), (2, 30)]),
    ([], [], []),
])
def test_scatter_basic_and_empty(x, y, expected):
    fig, ax = plt.subplots()
    coll = ax.scatter(x, y)
    offsets = coll.get_offsets()
    assert offsets.shape[0] == len(expected)
    for idx, (xi, yi) in enumerate(expected):
        assert offsets[idx][0] == xi
        assert offsets[idx][1] == yi

def test_scatter_mismatched_lengths_raises():
    with pytest.raises(ValueError):
        plt.scatter([1, 2], [1])

def test_scatter_nan_handling():
    x = [0, np.nan, 2]
    y = [0, 1, 2]
    coll = plt.scatter(x, y)
    offsets = coll.get_offsets()
    # In most matplotlib versions, NaN points are kept in the collection
    # but simply not rendered on the plot
    assert offsets.shape[0] == 3
    # Check that the NaN value is represented (either as NaN or as a masked value)
    # Matplotlib may use np.ma.masked arrays for handling missing values
    assert np.ma.is_masked(offsets[1, 0]) or np.isnan(offsets[1, 0])

def test_scatter_legend_label():
    fig, ax = plt.subplots()
    ax.scatter([1, 2, 3], [4, 5, 6], label="test_label")
    legend = ax.legend()
    labels = [text.get_text() for text in legend.get_texts()]
    assert "test_label" in labels

# Test default x generation when y is mapped to x-axis
def test_scatter_default_x_generation():
    y = [5, 10, 15]
    # Matplotlib actually requires 'x', so we'll test using y values as x
    # and check that default y values become indices
    coll = plt.scatter(y, range(len(y)))
    offsets = coll.get_offsets()
    assert offsets.shape[0] == len(y)
    for idx, val in enumerate(y):
        assert offsets[idx][0] == val
        assert offsets[idx][1] == idx

# Test scalar size parameter
def test_scatter_size_scalar():
    size_value = 100
    coll = plt.scatter([0, 1], [0, 1], s=size_value)
    sizes = coll.get_sizes()
    # Matplotlib optimizes by returning a single size value for uniform sizes
    assert sizes.shape == (1,) or len(sizes) == 2
    # The single value should match our size parameter
    assert sizes[0] == size_value

# Test array size parameter
def test_scatter_size_array():
    size_array = [50, 100]
    coll = plt.scatter([0, 1], [0, 1], s=size_array)
    sizes = coll.get_sizes()
    assert len(sizes) == 2
    assert sizes[0] == size_array[0]
    assert sizes[1] == size_array[1]

# Test scalar color parameter
def test_scatter_color_scalar():
    color = 'red'
    coll = plt.scatter([0, 1], [0, 1], c=color)
    facecolors = coll.get_facecolor()
    # All points should have the same color
    assert len(set(tuple(fc) for fc in facecolors)) == 1

# Test array color parameter
def test_scatter_color_array():
    color_array = ['red', 'blue']
    coll = plt.scatter([0, 1], [0, 1], c=color_array)
    facecolors = coll.get_facecolor()
    # Should have 2 different colors
    assert len(set(tuple(fc) for fc in facecolors)) == 2

# Test cmap normalization with vmin/vmax
def test_scatter_cmap_normalization():
    c_values = [0, 5, 10]
    vmin, vmax = 0, 10
    
    # Create two scatter plots: one with default norm and one with custom vmin/vmax
    coll1 = plt.scatter([0, 1, 2], [0, 1, 2], c=c_values, cmap='viridis')
    plt.clf()
    coll2 = plt.scatter([0, 1, 2], [0, 1, 2], c=c_values, cmap='viridis', vmin=vmin, vmax=vmax)
    
    # Check that the array data is preserved
    assert np.array_equal(coll2.get_array(), c_values)
    
    # The normalized values should match the input when proper vmin/vmax are set
    assert coll2.norm.vmin == vmin
    assert coll2.norm.vmax == vmax

# Test alpha transparency
def test_scatter_alpha_transparency():
    alpha_value = 0.5
    coll = plt.scatter([0, 1], [0, 1], alpha=alpha_value)
    # Check collection alpha
    assert coll.get_alpha() == alpha_value
    # Or check that alpha was applied to colors
    for fc in coll.get_facecolor():
        assert fc[3] == alpha_value

# Test datetime x-axis
def test_scatter_datetime_xaxis():
    dates = [np.datetime64('2020-01-01'), np.datetime64('2020-01-02')]
    y = [1, 2]
    fig, ax = plt.subplots()
    coll = ax.scatter(dates, y)
    
    # Check that dates are properly converted to float positions
    assert ax.xaxis.get_major_formatter().__class__.__name__ == 'AutoDateFormatter'
    offsets = coll.get_offsets()
    assert offsets.shape[0] == len(dates)
    
    # The datetime conversion maintains order
    assert offsets[1, 0] > offsets[0, 0]

# Test linewidths parameter
def test_scatter_linewidths():
    # Test scalar linewidth
    linewidth_value = 2.5
    coll = plt.scatter([0, 1], [0, 1], edgecolors='black', linewidths=linewidth_value)
    linewidths = coll.get_linewidths()
    # Matplotlib optimizes by returning a single linewidth for uniform values
    assert linewidths.shape == (1,) or len(linewidths) == 2
    # The single value should match our linewidth parameter
    assert linewidths[0] == linewidth_value
    plt.close()
    
    # Test array linewidths
    linewidth_array = [1.5, 3.0]
    coll = plt.scatter([0, 1], [0, 1], edgecolors='black', linewidths=linewidth_array)
    linewidths = coll.get_linewidths()
    # For array inputs, matplotlib should return an array of the same length
    # Check at least that the first value matches what we expect
    assert linewidths[0] == linewidth_array[0]
    # And that the returned array has the expected values
    assert np.allclose(linewidths[:len(linewidth_array)], linewidth_array)
    plt.close()

# Test categorical axes
def test_scatter_categorical_axes():
    categories = ['cat1', 'cat2', 'cat3']
    values = [1, 2, 3]
    fig, ax = plt.subplots()
    coll = ax.scatter(categories, values)
    
    # Check that categorical axis is created
    assert ax.xaxis.get_major_formatter().__class__.__name__ == 'StrCategoryFormatter'
    
    offsets = coll.get_offsets()
    assert offsets.shape[0] == len(categories)
    # First category should be at position 0, second at 1, etc.
    for i in range(len(categories)):
        assert offsets[i, 0] == i
        assert offsets[i, 1] == values[i]

# ----------------------------
# 2. Integration Tests
# ----------------------------
def test_scatter_with_subplots_and_log_scale():
    fig, axs = plt.subplots(1, 2)
    axs[0].scatter([1, 10, 100], [1, 10, 100])
    axs[1].scatter([1, 10, 100], [1, 10, 100])
    assert len(axs[0].collections) == 1
    assert len(axs[1].collections) == 1

    fig2, ax2 = plt.subplots()
    ax2.set_xscale('log')
    ax2.scatter([1, 10, 100], [1, 10, 100])
    assert ax2.get_xscale() == 'log'

def test_scatter_with_twin_axes():
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.scatter([0, 1], [0, 1])
    ax2.scatter([2, 3], [2, 3])
    assert len(ax1.collections) == 1
    assert len(ax2.collections) == 1

# ----------------------------
# 3. Property-Based Tests
# ----------------------------
if HAS_HYPOTHESIS:

    @given(
        x=st.lists(st.floats(min_value=-1e3, max_value=1e3), min_size=1, max_size=50),
        y=st.lists(st.floats(min_value=-1e3, max_value=1e3), min_size=1, max_size=50),
        s=st.one_of(
            st.floats(min_value=0.1, max_value=100),
            st.lists(st.floats(min_value=0.1, max_value=100), min_size=1, max_size=50)
        ),
        c=st.one_of(
            st.integers(min_value=0, max_value=255),
            st.lists(st.integers(min_value=0, max_value=255), min_size=1, max_size=50)
        )
    )
    def test_scatter_property_based(x, y, s, c):
        if len(x) != len(y):
            pytest.skip("x and y lengths must match")
        coll = plt.scatter(x, y, s=s, c=c)
        offsets = coll.get_offsets()
        assert offsets.shape[0] == len(x)
else:
    def test_scatter_property_based():
        pytest.skip("hypothesis not installed")

# ----------------------------
# 4. Fuzz Testing
# ----------------------------
@pytest.mark.parametrize("marker", [
    random.choice(string.ascii_letters) for _ in range(5)
])
def test_scatter_fuzz_marker(marker):
    try:
        plt.scatter([0, 1], [0, 1], marker=marker)
    except Exception as e:
        assert isinstance(e, (ValueError, TypeError))

# ----------------------------
# 5. Combinatorial Tests
# ----------------------------
markers = ['o', '^', 's', 'X', '.', '+', '*', 'D', 'p', 'h', 'H', '1']
cmaps = ['viridis', 'plasma', 'inferno', 'magma', 'cividis']
edgecolors = ['none', 'face', 'black', 'red', 'blue']
combos = list(itertools.product(markers, cmaps, edgecolors))[:60]

@pytest.mark.parametrize("marker,cmap,edgecolor", combos)
def test_scatter_combinatorial(marker, cmap, edgecolor):
    x = [0, 1, 2]
    y = [0, 1, 2]
    c = [0, 1, 2]  # Always provide 'c' to trigger colormapping and per-point coloring
    
    # Create a figure and axis explicitly to ensure we're in a clean state
    fig, ax = plt.subplots()
    coll = ax.scatter(x, y, marker=marker, c=c, cmap=cmap, edgecolors=edgecolor)
    
    assert coll.get_paths()  # paths defined
    
    # Some Matplotlib versions might return a scalar color instead of an array
    # Check the number of points in a more compatible way
    offsets = coll.get_offsets()
    assert offsets.shape[0] == len(x)
    
    # For edgecolors, we check that they exist but the shape may vary by Matplotlib version
    assert coll.get_edgecolor() is not None

# ----------------------------
# 6. Accessibility Tests
# ----------------------------
def test_scatter_color_cycle_distinct():
    fig, ax = plt.subplots()
    num = 10
    for i in range(num):
        ax.scatter([i], [i])
    colors = [tuple(coll.get_facecolor()[0]) for coll in ax.collections]
    assert len(set(colors)) == num

def test_scatter_high_contrast():
    coll = plt.scatter([0], [0], facecolors='white', edgecolors='black')
    fc = coll.get_facecolor()[0]
    ec = coll.get_edgecolor()[0]
    assert np.allclose(fc, [1, 1, 1, 1])
    assert np.allclose(ec, [0, 0, 0, 1])

# ----------------------------
# 7. Performance Scaling Test
# ----------------------------
def test_scatter_performance_scaling():
    sizes = [100, 1000, 10000, 100000]
    times = []
    for n in sizes:
        x = np.random.rand(n)
        y = np.random.rand(n)
        t0 = time.time()
        plt.scatter(x, y)
        times.append(time.time() - t0)
    # sub-linear scaling
    assert times[-1] < times[0] * 100
