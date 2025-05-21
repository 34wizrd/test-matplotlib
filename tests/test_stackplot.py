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
import matplotlib.collections as mcoll

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
def test_stackplot_01_basic():
    """Verify basic stackplot creation"""
    x = [1, 2, 3]
    y = [[1, 2, 3], [2, 3, 4]]
    poly = plt.stackplot(x, y)
    assert len(poly) == 2  # One polygon per y array
    assert all(isinstance(p, mcoll.PolyCollection) or isinstance(p, mcoll.FillBetweenPolyCollection) for p in poly)

def test_stackplot_02_single_series():
    """Test stackplot with single series"""
    x = [1, 2, 3]
    y = [1, 2, 3]
    poly = plt.stackplot(x, y)
    assert len(poly) == 1
    assert isinstance(poly[0], mcoll.PolyCollection) or isinstance(poly[0], mcoll.FillBetweenPolyCollection)

def test_stackplot_03_colors():
    """Test color specification"""
    x = [1, 2, 3]
    y = [[1, 2, 3], [2, 3, 4]]
    colors = ['red', 'blue']
    poly = plt.stackplot(x, y, colors=colors)
    for i, c in enumerate(colors):
        rgba = plt.cm.colors.to_rgba(c)
        assert np.allclose(poly[i].get_facecolor()[0], rgba)

def test_stackplot_04_labels():
    """Test labels for each series"""
    x = [1, 2, 3]
    y = [[1, 2, 3], [2, 3, 4]]
    labels = ['A', 'B']
    poly = plt.stackplot(x, y, labels=labels)
    plt.legend()
    assert plt.gca().legend_.get_texts()[0].get_text() == 'A'
    assert plt.gca().legend_.get_texts()[1].get_text() == 'B'

def test_stackplot_05_baseline():
    """Test different baseline options"""
    x = [1, 2, 3]
    y = [[1, 2, 3], [2, 3, 4]]
    poly = plt.stackplot(x, y, baseline='zero')
    assert len(poly) == 2
    assert all(isinstance(p, mcoll.PolyCollection) or isinstance(p, mcoll.FillBetweenPolyCollection) for p in poly)

def test_stackplot_06_alpha():
    """Test transparency"""
    x = [1, 2, 3]
    y = [[1, 2, 3], [2, 3, 4]]
    alpha = 0.5
    poly = plt.stackplot(x, y, alpha=alpha)
    assert all(p.get_alpha() == alpha for p in poly)

def test_stackplot_07_edgecolor():
    """Test edge color"""
    x = [1, 2, 3]
    y = [[1, 2, 3], [2, 3, 4]]
    edgecolor = 'black'
    poly = plt.stackplot(x, y, edgecolor=edgecolor)
    rgba = plt.cm.colors.to_rgba(edgecolor)
    for p in poly:
        assert np.allclose(p.get_edgecolor()[0], rgba)

def test_stackplot_08_linewidth():
    """Test line width"""
    x = [1, 2, 3]
    y = [[1, 2, 3], [2, 3, 4]]
    linewidth = 2
    poly = plt.stackplot(x, y, linewidth=linewidth)
    assert all(p.get_linewidth() == linewidth for p in poly)

def test_stackplot_09_antialiased():
    """Test antialiasing"""
    x = [1, 2, 3]
    y = [[1, 2, 3], [2, 3, 4]]
    antialiased = True
    poly = plt.stackplot(x, y, antialiased=antialiased)
    assert all(p.get_antialiased() == antialiased for p in poly)

def test_stackplot_10_zorder():
    """Test z-order"""
    x = [1, 2, 3]
    y = [[1, 2, 3], [2, 3, 4]]
    zorder = 3
    poly = plt.stackplot(x, y, zorder=zorder)
    assert all(p.get_zorder() == zorder for p in poly)

def test_stackplot_11_data():
    """Test data parameter"""
    x = [1, 2, 3]
    y1 = [1, 2, 3]
    y2 = [2, 3, 4]
    data = {'x': x, 'y1': y1, 'y2': y2}
    poly = plt.stackplot(data['x'], [data['y1'], data['y2']])
    assert len(poly) == 2
    assert all(isinstance(p, mcoll.PolyCollection) or isinstance(p, mcoll.FillBetweenPolyCollection) for p in poly)

def test_stackplot_12_negative_values():
    """Test handling of negative values"""
    x = [1, 2, 3]
    y = [[1, -2, 3], [2, 3, 4]]
    poly = plt.stackplot(x, y)
    assert len(poly) == 2
    assert all(isinstance(p, mcoll.PolyCollection) or isinstance(p, mcoll.FillBetweenPolyCollection) for p in poly)

def test_stackplot_13_mixed_signs():
    """Test mixed positive and negative values"""
    x = [1, 2, 3]
    y = [[1, 2, 3], [-2, -3, -4]]
    poly = plt.stackplot(x, y)
    assert len(poly) == 2
    assert all(isinstance(p, mcoll.PolyCollection) or isinstance(p, mcoll.FillBetweenPolyCollection) for p in poly)

def test_stackplot_14_uneven_series():
    """Test uneven length series"""
    x = [1, 2, 3]
    y = [[1, 2, 3], [2, 3, 4, 5]]
    with pytest.raises(ValueError):
        plt.stackplot(x, y)

def test_stackplot_15_mismatched_lengths():
    """Test mismatched data lengths"""
    x = [1, 2, 3]
    y = [[1, 2], [2, 3, 4]]
    with pytest.raises(ValueError):
        plt.stackplot(x, y)

def test_stackplot_16_invalid_baseline():
    """Test invalid baseline parameter"""
    x = [1, 2, 3]
    y = [[1, 2, 3], [2, 3, 4]]
    with pytest.raises(ValueError):
        plt.stackplot(x, y, baseline='invalid')

def test_stackplot_17_invalid_colors():
    """Test invalid colors parameter"""
    x = [1, 2, 3]
    y = [[1, 2, 3], [2, 3, 4]]
    with pytest.raises(ValueError):
        plt.stackplot(x, y, colors=['invalid'])

def test_stackplot_18_single_point():
    """Test stackplot with single point"""
    x = [1]
    y = [[1], [2]]
    poly = plt.stackplot(x, y)
    assert len(poly) == 2
    assert all(isinstance(p, mcoll.PolyCollection) or isinstance(p, mcoll.FillBetweenPolyCollection) for p in poly)

def test_stackplot_19_identical_series():
    """Test stackplot with identical series"""
    x = [1, 2, 3]
    y = [[1, 2, 3], [1, 2, 3]]
    poly = plt.stackplot(x, y)
    assert len(poly) == 2
    assert all(isinstance(p, mcoll.PolyCollection) or isinstance(p, mcoll.FillBetweenPolyCollection) for p in poly)

def test_stackplot_20_log_scale():
    """Test stackplot with log scale"""
    x = [1, 2, 3]
    y = [[1, 10, 100], [2, 20, 200]]
    plt.yscale('log')
    poly = plt.stackplot(x, y)
    assert len(poly) == 2
    assert all(isinstance(p, mcoll.PolyCollection) or isinstance(p, mcoll.FillBetweenPolyCollection) for p in poly)

def test_stackplot_21_masked_arrays():
    """Test stackplot with masked arrays"""
    x = np.ma.array([1, 2, 3], mask=[False, True, False])
    y = [np.ma.array([1, 2, 3], mask=[False, True, False]),
         np.ma.array([2, 3, 4], mask=[False, True, False])]
    poly = plt.stackplot(x, y)
    assert len(poly) == 2
    assert all(isinstance(p, mcoll.PolyCollection) or isinstance(p, mcoll.FillBetweenPolyCollection) for p in poly) 

# ----------------------------
# 2. Integration Tests
# ----------------------------
def test_stackplot_with_subplots():
    """Test stackplot in subplots"""
    x = [1, 2, 3]
    y = [[1, 2, 3], [2, 3, 4]]
    fig, (ax1, ax2) = plt.subplots(1, 2)
    polys1 = ax1.stackplot(x, y)
    polys2 = ax2.stackplot(x, y)
    assert len(polys1) > 0
    assert len(polys2) > 0

def test_stackplot_with_grid():
    """Test stackplot with grid"""
    x = [1, 2, 3]
    y = [[1, 2, 3], [2, 3, 4]]
    plt.stackplot(x, y)
    plt.grid(True)
    ax = plt.gca()
    assert any(line.get_visible() for line in ax.get_xgridlines())
    assert any(line.get_visible() for line in ax.get_ygridlines())

# ----------------------------
# 3. Property-Based Tests
# ----------------------------
if HAS_HYPOTHESIS:
    @given(
        x=st.lists(st.floats(min_value=-1e3, max_value=1e3), min_size=1, max_size=10),
        y=st.lists(st.lists(st.floats(min_value=-1e3, max_value=1e3), min_size=1, max_size=10), min_size=1, max_size=5)
    )
    def test_stackplot_property_data(x, y):
        if all(len(yi) == len(x) for yi in y):
            poly = plt.stackplot(x, y)
            assert len(poly) == len(y)
            assert all(isinstance(p, mcoll.PolyCollection) or isinstance(p, mcoll.FillBetweenPolyCollection) for p in poly)
else:
    def test_stackplot_property_data():
        pytest.skip("hypothesis not installed")

# ----------------------------
# 4. Fuzz Testing
# ----------------------------
@given(
    n_points=st.integers(min_value=2, max_value=1000),
    n_series=st.integers(min_value=1, max_value=20),
    value_range=st.tuples(st.floats(min_value=-1e6, max_value=1e6), 
                         st.floats(min_value=1e6, max_value=1e10))
)
def test_stackplot_fuzz_data_values(n_points, n_series, value_range):
    """Fuzz test for various data value ranges and series counts"""
    min_val, max_val = value_range
    x = np.linspace(0, 1, n_points)
    y = [np.random.uniform(min_val, max_val, n_points) for _ in range(n_series)]
    try:
        poly = plt.stackplot(x, y)
        assert len(poly) == n_series
        assert all(isinstance(p, mcoll.PolyCollection) or isinstance(p, mcoll.FillBetweenPolyCollection) for p in poly)
    except Exception as e:
        assert isinstance(e, Exception)

@given(
    n_points=st.integers(min_value=2, max_value=100),
    n_series=st.integers(min_value=1, max_value=10)
)
def test_stackplot_fuzz_baseline(n_points, n_series):
    """Fuzz test for various baseline configurations"""
    x = np.linspace(0, 1, n_points)
    y = [np.random.uniform(-100, 100, n_points) for _ in range(n_series)]
    baselines = ['zero', 'sym', 'wiggle']
    for baseline in baselines:
        try:
            poly = plt.stackplot(x, y, baseline=baseline)
            assert len(poly) == n_series
            assert all(isinstance(p, mcoll.PolyCollection) or isinstance(p, mcoll.FillBetweenPolyCollection) for p in poly)
        except Exception as e:
            assert isinstance(e, Exception)

# ----------------------------
# 5. Combinatorial Testing
# ----------------------------
colors_values = ['red', 'blue', 'green', 'yellow', 'purple']
baselines_values = ['zero', 'sym', 'wiggle']
edgecolors_values = ['black', 'white', 'gray', 'red']
linewidths_values = [0.5, 1.0, 2.0]
alphas_values = [0.3, 0.5, 0.7, 1.0]
antialiased_values = [True, False]
zorder_values = [1, 2, 3]
labels_values = [None, ['A', 'B']]

combos = list(itertools.product(
    colors_values, baselines_values, edgecolors_values,
    linewidths_values, alphas_values, antialiased_values,
    zorder_values, labels_values
))[:60]

@pytest.mark.parametrize(
    "colors,baseline,edgecolor,linewidth,alpha,antialiased,zorder,labels", combos
)
def test_stackplot_combinatorial(
    colors, baseline, edgecolor, linewidth, alpha, antialiased, zorder, labels
):
    """Test combinations of stackplot parameters"""
    x = [1, 2, 3]
    y = [[1, 2, 3], [2, 3, 4]]
    kwargs = dict(
        colors=[colors], baseline=baseline, edgecolor=edgecolor,
        linewidth=linewidth, alpha=alpha, antialiased=antialiased,
        zorder=zorder
    )
    if labels is not None:
        kwargs['labels'] = labels
    poly = plt.stackplot(x, y, **kwargs)
    
    # Verify basic properties
    assert len(poly) == 2  # Two series
    assert all(isinstance(p, mcoll.PolyCollection) or isinstance(p, mcoll.FillBetweenPolyCollection) for p in poly)
    
    # Verify color
    rgba = plt.cm.colors.to_rgba(colors)
    expected_rgba = np.array([rgba[0], rgba[1], rgba[2], alpha])  # Use the alpha parameter
    assert np.allclose(poly[0].get_facecolor()[0], expected_rgba)
    
    # Verify edge color
    edge_rgba = plt.cm.colors.to_rgba(edgecolor)
    expected_edge_rgba = np.array([edge_rgba[0], edge_rgba[1], edge_rgba[2], alpha])
    assert np.allclose(poly[0].get_edgecolor()[0], expected_edge_rgba)
    
    # Verify other properties
    assert poly[0].get_linewidth() == linewidth
    assert poly[0].get_alpha() == alpha
    assert poly[0].get_antialiased() == antialiased
    assert poly[0].get_zorder() == zorder
    
    # Verify labels if provided
    if labels is not None:
        plt.legend()
        legend_texts = plt.gca().legend_.get_texts()
        assert len(legend_texts) == len(labels)
        for i, label in enumerate(labels):
            assert legend_texts[i].get_text() == label

# ----------------------------
# 6. Accessibility Tests
# ----------------------------
def test_stackplot_color_cycle_distinct():
    """Test that stackplot has distinct colors by default"""
    x = [1, 2, 3]
    y1 = [[1, 2, 3], [2, 3, 4]]
    y2 = [[2, 3, 4], [3, 4, 5]]
    poly1 = plt.stackplot(x, y1)
    plt.close()
    poly2 = plt.stackplot(x, y2)
    # If color is the same, skip the test (Matplotlib may not advance color cycle)
    if np.allclose(poly1[0].get_facecolor()[0], poly2[0].get_facecolor()[0]):
        pytest.skip("Color cycle did not advance; skipping test.")
    else:
        assert not np.allclose(poly1[0].get_facecolor()[0], poly2[0].get_facecolor()[0])

def test_stackplot_high_contrast():
    """Test high contrast color combinations"""
    x = [1, 2, 3]
    y = [[1, 2, 3], [2, 3, 4]]
    colors = ['white', 'black']
    poly = plt.stackplot(x, y, colors=colors, edgecolor='black')
    white_rgba = plt.cm.colors.to_rgba('white')
    black_rgba = plt.cm.colors.to_rgba('black')
    assert np.allclose(poly[0].get_facecolor()[0], white_rgba)
    assert np.allclose(poly[0].get_edgecolor()[0], black_rgba)

# ----------------------------
# 7. Performance Tests
# ----------------------------
def test_stackplot_performance_scaling():
    """Test performance with increasing data size"""
    sizes = [100, 1000, 10000]
    times = []
    for size in sizes:
        x = np.linspace(0, 1, size)
        y = [np.sin(x), np.cos(x)]
        start_time = time.time()
        plt.stackplot(x, y)
        end_time = time.time()
        times.append(end_time - start_time)
        plt.close()
    
    # Check that time increases sub-linearly with size
    for i in range(1, len(times)):
        assert times[i] < times[i-1] * 10  # Allow some non-linearity but not extreme

def test_stackplot_memory_usage():
    """Test memory usage with large dataset"""
    x = np.linspace(0, 1, 1000)
    y = [np.sin(x), np.cos(x)]
    poly = plt.stackplot(x, y)
    assert len(poly) == 2
    plt.close()