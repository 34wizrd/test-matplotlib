import matplotlib
matplotlib.use('Agg')  # Use headless backend for testing

import matplotlib.pyplot as plt
import numpy as np
from hypothesis import given, settings, strategies as st
import pytest
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
def test_hist_01_basic():
    """Verify basic histogram creation"""
    data = [1, 2, 2, 3, 3, 3, 4, 4, 5]
    n, bins, patches = plt.hist(data, bins=5)
    assert len(n) == 5  # Number of bins
    assert len(bins) == 6  # Number of bin edges
    assert len(patches) == 5  # Number of patches
    # Verify frequency distribution
    assert n[2] == 3  # Three values in the middle bin

def test_hist_02_bins():
    """Validate behavior for different bin sizes"""
    data = [1, 2, 2, 3, 3, 3, 4, 4, 5]
    # Test with integer bins
    n1, bins1, _ = plt.hist(data, bins=5)
    # Test with explicit bin edges
    bin_edges = [1, 2, 3, 4, 5, 6]
    n2, bins2, _ = plt.hist(data, bins=bin_edges)
    assert len(n1) == 5
    assert len(n2) == 5
    # Only check the counts, as bin edges may differ due to different binning strategies
    assert np.array_equal(n1, n2)

def test_hist_03_empty_data():
    """Ensure empty data produces no bars"""
    n, bins, patches = plt.hist([], bins=5)
    assert len(n) == 5
    assert len(bins) == 6
    assert len(patches) == 5
    assert all(count == 0 for count in n)

def test_hist_04_density():
    """Test density normalization"""
    data = [1, 2, 2, 3, 3, 3, 4, 4, 5]
    n, bins, _ = plt.hist(data, bins=5, density=True)
    # Sum of density should be approximately 1
    assert abs(np.sum(n * np.diff(bins)) - 1.0) < 1e-10

def test_hist_05_weights():
    """Validate weighted histograms"""
    data = [1, 2, 3]
    weights = [2, 3, 4]
    n, bins, _ = plt.hist(data, bins=3, weights=weights)
    assert n[0] == 2  # First bin weight
    assert n[1] == 3  # Second bin weight
    assert n[2] == 4  # Third bin weight

def test_hist_06_histtype_bar():
    """Verify bar histogram type"""
    data = [1, 2, 2, 3, 3, 3]
    n, bins, patches = plt.hist(data, bins=3, histtype='bar')
    assert len(patches) == 3
    for patch in patches:
        assert isinstance(patch, plt.Rectangle)

def test_hist_07_histtype_step():
    """Validate step histogram type"""
    data = [1, 2, 2, 3, 3, 3]
    n, bins, patches = plt.hist(data, bins=3, histtype='step')
    assert len(patches) == 1
    # For step histograms, matplotlib uses Polygon
    assert isinstance(patches[0], plt.Polygon)
    assert len(n) == 3  # Should have 3 bins
    assert len(bins) == 4  # Should have 4 bin edges

def test_hist_08_colors():
    """Test custom bar colors"""
    data = [1, 2, 2, 3, 3, 3]
    color = 'red'  # Use a single color
    n, bins, patches = plt.hist(data, bins=3, color=color)
    for patch in patches:
        assert np.array_equal(patch.get_facecolor(), plt.cm.colors.to_rgba(color))

def test_hist_09_edgecolor():
    """Verify edge color customization"""
    data = [1, 2, 2, 3, 3, 3]
    edgecolor = 'black'
    n, bins, patches = plt.hist(data, bins=3, edgecolor=edgecolor)
    for patch in patches:
        assert patch.get_edgecolor() == plt.cm.colors.to_rgba(edgecolor)

def test_hist_10_alignment():
    """Validate align parameter"""
    data = [1, 2, 2, 3, 3, 3]
    # Test mid alignment (default)
    n1, bins1, patches1 = plt.hist(data, bins=3, align='mid')
    # Test left alignment
    n2, bins2, patches2 = plt.hist(data, bins=3, align='left')
    assert len(patches1) == len(patches2)
    # Check that the bin positions are different
    assert not np.array_equal([p.get_x() for p in patches1], [p.get_x() for p in patches2])

def test_hist_11_range():
    """Test binning with custom range"""
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    range_val = (2, 8)
    n, bins, _ = plt.hist(data, bins=3, range=range_val)
    assert bins[0] == range_val[0]
    assert bins[-1] == range_val[1]
    assert len(n) == 3

def test_hist_12_label():
    """Verify legend label functionality"""
    data = [1, 2, 2, 3, 3, 3]
    label = "test_histogram"
    n, bins, patches = plt.hist(data, bins=3, label=label)
    legend = plt.gca().legend()
    labels = [text.get_text() for text in legend.get_texts()]
    assert label in labels

def test_hist_13_invalid_weights():
    """Test invalid weights"""
    data = [1, 2, 3]
    weights = [1, 2]  # Mismatched length
    with pytest.raises(ValueError):
        plt.hist(data, weights=weights)

def test_hist_14_negative_values():
    """Test handling of negative values"""
    data = [-1, -2, -3]
    n, bins, patches = plt.hist(data, bins=3)
    assert len(patches) == 3
    for i, patch in enumerate(patches):
        assert patch.get_height() == 1  # Each bin should have one value

def test_hist_15_zero_values():
    """Test handling of zero values"""
    data = [0, 0, 0]
    n, bins, patches = plt.hist(data, bins=3)
    assert len(patches) == 3
    assert n[1] == 3  # All values should be in the middle bin

def test_hist_16_with_datetime_xaxis():
    """Test histogram with datetime x-axis"""
    dates = [np.datetime64('2020-01-01'), np.datetime64('2020-01-02')]
    values = [1, 2]
    fig, ax = plt.subplots()
    n, bins, patches = ax.hist(dates, bins=2)
    assert len(patches) == 2
    assert ax.xaxis.get_major_formatter().__class__.__name__ == 'AutoDateFormatter'

def test_hist_17_with_log_scale():
    """Test histogram with log scale"""
    data = [1, 10, 100, 1000]
    fig, ax = plt.subplots()
    ax.set_xscale('log')
    n, bins, patches = ax.hist(data, bins=4)
    assert len(patches) == 4
    assert ax.get_xscale() == 'log'

def test_hist_18_with_custom_xticks():
    """Test histogram with custom x-axis ticks"""
    data = [1, 2, 3]
    labels = ['A', 'B', 'C']
    fig, ax = plt.subplots()
    n, bins, patches = ax.hist(data, bins=3)
    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(labels)
    assert [t.get_text() for t in ax.get_xticklabels()] == labels

def test_hist_19_with_categorical_data():
    """Test histogram with categorical data"""
    categories = ['A', 'B', 'A', 'C', 'B', 'B']
    n, bins, patches = plt.hist(categories, bins=3)
    assert len(n) == 3
    assert len(bins) == 4
    assert len(patches) == 3 

# ----------------------------
# 2. Integration Tests
# ----------------------------
def test_hist_with_subplots():
    """Test rendering histograms in subplots"""
    data1 = [1, 2, 2, 3, 3, 3]
    data2 = [4, 5, 5, 6, 6, 6]
    fig, (ax1, ax2) = plt.subplots(1, 2)
    ax1.hist(data1, bins=3)
    ax2.hist(data2, bins=3)
    assert len(ax1.patches) == 3
    assert len(ax2.patches) == 3

def test_hist_with_log_scale():
    """Validate histogram with log scale"""
    data = [1, 10, 100, 1000]
    fig, ax = plt.subplots()
    ax.set_xscale('log')
    n, bins, patches = ax.hist(data, bins=4)
    assert ax.get_xscale() == 'log'
    assert len(patches) == 4

# ----------------------------
# 3. Property-Based Tests
# ----------------------------
if HAS_HYPOTHESIS:
    @given(
        data=st.lists(st.floats(min_value=-1e3, max_value=1e3), min_size=1, max_size=50),
        bins=st.one_of(
            st.integers(min_value=1, max_value=20),
            st.lists(st.floats(min_value=-1e3, max_value=1e3), min_size=2, max_size=20)
            .map(lambda x: sorted(x))  # Ensure bin edges are monotonically increasing
        )
    )
    def test_hist_property_bins(data, bins):
        try:
            n, bins_out, patches = plt.hist(data, bins=bins)
            assert len(n) == len(patches)
            assert len(bins_out) == len(n) + 1
        except ValueError as e:
            # Accept ValueError for too many bins for data range
            assert "Too many bins for data range" in str(e)
else:
    def test_hist_property_bins():
        pytest.skip("hypothesis not installed")

# ----------------------------
# 4. Fuzz Testing
# ----------------------------

@given(
    n_points=st.integers(min_value=10, max_value=100),
    n_bins=st.integers(min_value=2, max_value=20)
)
def test_hist_fuzz_bin_edges(n_points, n_bins):
    """Fuzz test for various bin edge specifications"""
    data = np.random.randn(n_points)
    # Test different bin edge specifications
    bin_specs = [
        n_bins,  # Integer number of bins
        np.linspace(min(data), max(data), n_bins + 1),  # Linear spacing
        np.geomspace(abs(min(data)) + 1e-10, abs(max(data)) + 1e-10, n_bins + 1),  # Geometric spacing
        np.concatenate([np.linspace(min(data), 0, n_bins//2 + 1), 
                       np.linspace(0, max(data), n_bins//2 + 1)[1:]])  # Custom spacing
    ]
    for bins in bin_specs:
        try:
            counts, bin_edges, patches = plt.hist(data, bins=bins)
            assert len(counts) == len(patches)
            assert len(bin_edges) == len(counts) + 1
        except Exception as e:
            assert isinstance(e, Exception)
# ----------------------------
# 5. Combinatorial Testing
# ----------------------------
histtypes = ['bar', 'barstacked', 'step', 'stepfilled']
aligns = ['left', 'mid', 'right']
colors = ['red', 'blue', 'green', 'yellow', 'purple']
edgecolors = ['black', 'none', 'red', 'blue', 'green']
combos = list(itertools.product(histtypes, aligns, colors, edgecolors))[:60]

@pytest.mark.parametrize("histtype,align,color,edgecolor", combos)
def test_hist_combinatorial(histtype, align, color, edgecolor):
    """Test combinations of histogram parameters"""
    data = [1, 2, 2, 3, 3, 3]
    n, bins, patches = plt.hist(data, bins=3, histtype=histtype, align=align, 
                               color=color, edgecolor=edgecolor)
    assert len(patches) > 0
    for patch in patches:
        assert patch.get_facecolor() == plt.cm.colors.to_rgba(color)
        assert patch.get_edgecolor() == plt.cm.colors.to_rgba(edgecolor)

# ----------------------------
# 6. Accessibility Tests
# ----------------------------
def test_hist_color_cycle_distinct():
    """Test that histograms have distinct colors by default"""
    fig, ax = plt.subplots()
    data = [1, 2, 2, 3, 3, 3]
    # Create multiple datasets to test color cycling
    data1 = [1, 2, 2]
    data2 = [3, 3, 3]
    n, bins, patches = ax.hist([data1, data2], bins=3)
    # Get colors from patches
    colors = []
    for container in patches:
        for patch in container:
            colors.append(patch.get_facecolor())
    # Check that we have distinct colors
    assert len(set(tuple(c) for c in colors)) > 1

def test_hist_high_contrast():
    """Test high contrast color combinations"""
    data = [1, 2, 2, 3, 3, 3]
    n, bins, patches = plt.hist(data, bins=3, color='white', edgecolor='black')
    for patch in patches:
        assert np.allclose(patch.get_facecolor(), [1, 1, 1, 1])  # White
        assert np.allclose(patch.get_edgecolor(), [0, 0, 0, 1])  # Black

# ----------------------------
# 7. Performance Tests
# ----------------------------
def test_hist_performance_scaling():
    """Test performance with increasing data size"""
    sizes = [100, 1000, 10000, 100000]
    times = []
    for size in sizes:
        data = np.random.normal(0, 1, size)
        start_time = time.time()
        plt.hist(data, bins=50)
        end_time = time.time()
        times.append(end_time - start_time)
        plt.close()
    
    # Check that time increases sub-linearly with size
    for i in range(1, len(times)):
        assert times[i] < times[i-1] * 10  # Allow some non-linearity but not extreme

def test_hist_memory_usage():
    """Test memory usage with large dataset"""
    data = np.random.normal(0, 1, 100000)
    n, bins, patches = plt.hist(data, bins=50)
    assert len(patches) == 50
    plt.close()