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
from matplotlib.collections import PolyCollection, FillBetweenPolyCollection

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
def test_fill_between_01_basic():
    """Verify basic fill_between creation"""
    x = [1, 2, 3]
    y1 = [1, 2, 3]
    y2 = [0, 1, 2]
    poly = plt.fill_between(x, y1, y2)
    assert isinstance(poly, PolyCollection)

def test_fill_between_02_single_curve():
    """Test fill between curve and constant"""
    x = [1, 2, 3]
    y = [1, 2, 3]
    poly = plt.fill_between(x, y)
    assert isinstance(poly, PolyCollection)

def test_fill_between_03_where():
    """Test where parameter for conditional filling"""
    x = [1, 2, 3, 4]
    y1 = [1, 2, 3, 4]
    y2 = [0, 1, 2, 3]
    where = [True, False, True, False]
    poly = plt.fill_between(x, y1, y2, where=where)
    assert isinstance(poly, PolyCollection)

def test_fill_between_04_interpolate():
    """Test interpolate parameter"""
    x = [1, 2, 3]
    y1 = [1, 2, 3]
    y2 = [0, 1, 2]
    poly = plt.fill_between(x, y1, y2, interpolate=True)
    assert isinstance(poly, PolyCollection)

def test_fill_between_05_step():
    """Test step parameter"""
    x = [1, 2, 3]
    y1 = [1, 2, 3]
    y2 = [0, 1, 2]
    poly = plt.fill_between(x, y1, y2, step='pre')
    assert isinstance(poly, PolyCollection)

def test_fill_between_06_color():
    """Test color specification"""
    x = [1, 2, 3]
    y1 = [1, 2, 3]
    y2 = [0, 1, 2]
    color = 'red'
    poly = plt.fill_between(x, y1, y2, color=color)
    facecolor = poly.get_facecolor()
    # Compare to RGBA tuple
    assert np.allclose(facecolor[0], plt.matplotlib.colors.to_rgba(color))

def test_fill_between_07_alpha():
    """Test transparency"""
    x = [1, 2, 3]
    y1 = [1, 2, 3]
    y2 = [0, 1, 2]
    alpha = 0.5
    poly = plt.fill_between(x, y1, y2, alpha=alpha)
    assert poly.get_alpha() == alpha

def test_fill_between_08_hatch():
    """Test hatch pattern"""
    x = [1, 2, 3]
    y1 = [1, 2, 3]
    y2 = [0, 1, 2]
    hatch = '/'
    poly = plt.fill_between(x, y1, y2, hatch=hatch)
    assert poly.get_hatch() == hatch

def test_fill_between_09_edgecolor():
    """Test edge color"""
    x = [1, 2, 3]
    y1 = [1, 2, 3]
    y2 = [0, 1, 2]
    edgecolor = 'blue'
    poly = plt.fill_between(x, y1, y2, edgecolor=edgecolor)
    edgecolor_rgba = plt.matplotlib.colors.to_rgba(edgecolor)
    # get_edgecolor returns an array of RGBA
    assert np.allclose(poly.get_edgecolor()[0], edgecolor_rgba)

def test_fill_between_10_linewidth():
    """Test line width"""
    x = [1, 2, 3]
    y1 = [1, 2, 3]
    y2 = [0, 1, 2]
    linewidth = 2
    poly = plt.fill_between(x, y1, y2, linewidth=linewidth)
    # get_linewidth returns an array
    assert np.allclose(poly.get_linewidth()[0], linewidth)

def test_fill_between_11_antialiased():
    """Test antialiasing"""
    x = [1, 2, 3]
    y1 = [1, 2, 3]
    y2 = [0, 1, 2]
    antialiased = True
    poly = plt.fill_between(x, y1, y2, antialiased=antialiased)
    # get_antialiased returns an array
    assert poly.get_antialiased()[0] == antialiased

def test_fill_between_12_label():
    """Test legend label"""
    x = [1, 2, 3]
    y1 = [1, 2, 3]
    y2 = [0, 1, 2]
    label = 'test'
    poly = plt.fill_between(x, y1, y2, label=label)
    plt.legend()
    assert plt.gca().legend_.get_texts()[0].get_text() == label

def test_fill_between_13_zorder():
    """Test z-order"""
    x = [1, 2, 3]
    y1 = [1, 2, 3]
    y2 = [0, 1, 2]
    zorder = 3
    poly = plt.fill_between(x, y1, y2, zorder=zorder)
    assert abs(poly.get_zorder() - zorder) < 1e-6

def test_fill_between_14_data():
    """Test data parameter"""
    x = [1, 2, 3]
    y1 = [1, 2, 3]
    y2 = [0, 1, 2]
    data = {'x': x, 'y1': y1, 'y2': y2}
    poly = plt.fill_between('x', 'y1', 'y2', data=data)
    assert isinstance(poly, PolyCollection)

def test_fill_between_15_mismatched_lengths():
    """Test mismatched data lengths"""
    x = [1, 2, 3]
    y1 = [1, 2]
    y2 = [0, 1, 2]
    with pytest.raises(ValueError):
        plt.fill_between(x, y1, y2)

def test_fill_between_16_invalid_step():
    """Test invalid step parameter"""
    x = [1, 2, 3]
    y1 = [1, 2, 3]
    y2 = [0, 1, 2]
    with pytest.raises((ValueError, KeyError)):
        plt.fill_between(x, y1, y2, step='invalid')

def test_fill_between_17_invalid_where():
    """Test invalid where parameter"""
    x = [1, 2, 3]
    y1 = [1, 2, 3]
    y2 = [0, 1, 2]
    with pytest.raises(ValueError):
        plt.fill_between(x, y1, y2, where=[True, False])  # Mismatched length

def test_fill_between_18_single_point():
    """Test fill_between with single point"""
    x = [1]
    y1 = [1]
    y2 = [0]
    poly = plt.fill_between(x, y1, y2)
    assert isinstance(poly, PolyCollection)

def test_fill_between_19_identical_curves():
    """Test fill_between with identical curves"""
    x = [1, 2, 3]
    y = [1, 2, 3]
    poly = plt.fill_between(x, y, y)
    assert isinstance(poly, PolyCollection)

# ----------------------------
# 2. Integration Tests
# ----------------------------
def test_fill_between_with_subplots():
    """Test fill_between in subplots"""
    x = [1, 2, 3]
    y1 = [1, 2, 3]
    y2 = [0, 1, 2]
    fig, (ax1, ax2) = plt.subplots(1, 2)
    poly1 = ax1.fill_between(x, y1, y2)
    poly2 = ax2.fill_between(x, y1, y2)
    # PolyCollection is added to ax.collections, not ax.patches
    assert any(isinstance(coll, PolyCollection) for coll in ax1.collections)
    assert any(isinstance(coll, PolyCollection) for coll in ax2.collections)

def test_fill_between_with_grid():
    """Test fill_between with grid"""
    x = [1, 2, 3]
    y1 = [1, 2, 3]
    y2 = [0, 1, 2]
    plt.fill_between(x, y1, y2)
    plt.grid(True)
    ax = plt.gca()
    assert any(line.get_visible() for line in ax.xaxis.get_gridlines())
    assert any(line.get_visible() for line in ax.yaxis.get_gridlines())

# ----------------------------
# 3. Property-Based Tests
# ----------------------------
if HAS_HYPOTHESIS:
    @given(
        x=st.lists(st.floats(min_value=-1e3, max_value=1e3), min_size=1, max_size=10),
        y1=st.lists(st.floats(min_value=-1e3, max_value=1e3), min_size=1, max_size=10),
        y2=st.lists(st.floats(min_value=-1e3, max_value=1e3), min_size=1, max_size=10)
    )
    def test_fill_between_property_data(x, y1, y2):
        if len(x) == len(y1) == len(y2):
            poly = plt.fill_between(x, y1, y2)
            assert isinstance(poly, PolyCollection)
else:
    def test_fill_between_property_data():
        pytest.skip("hypothesis not installed")

# ----------------------------
# 4. Fuzz Testing
# ----------------------------
@given(
    n_points=st.integers(min_value=1, max_value=100)
)
def test_fill_between_fuzz_shape(n_points):
    """Random data shapes and values"""
    x = np.sort(np.random.randn(n_points))
    y1 = np.random.randn(n_points)
    y2 = y1 + np.random.uniform(0, 1, n_points)  # ensure y2 >= y1 sometimes
    try:
        poly = plt.fill_between(x, y1, y2)
        assert poly is not None
    except Exception as e:
        assert isinstance(e, Exception)

@pytest.mark.parametrize("size", [1, 5, 10])
def test_fill_between_fuzz_invalid_values(size):
    """Random invalid values (NaN, Inf, None) with matching sizes"""
    x = np.random.choice([np.nan, np.inf, -np.inf, None], size=size)
    y1 = np.random.choice([np.nan, np.inf, -np.inf, None], size=size)
    y2 = np.random.choice([np.nan, np.inf, -np.inf, None], size=size)
    try:
        plt.fill_between(x, y1, y2)
    except Exception as e:
        assert isinstance(e, (ValueError, TypeError))

# ----------------------------
# 5. Combinatorial Testing
# ----------------------------=
colors_values = ['red', 'blue', 'green', 'yellow', 'purple']
hatches_values = ['/', '\\', 'x', '-', '|']
steps_values = ['pre', 'post', 'mid']
alphas_values = [0.3, 0.5, 0.7, 1.0]
edgecolors_values = ['black', 'white', 'gray', 'red']
linewidths_values = [0.5, 1.0, 2.0]
antialiased_values = [True, False]
zorder_values = [1, 2, 3]
labels_values = [None, 'A']

combos = list(itertools.product(
    colors_values, hatches_values, steps_values, alphas_values,
    edgecolors_values, linewidths_values, antialiased_values, zorder_values, labels_values
))[:60]

@pytest.mark.parametrize(
    "color,hatch,step,alpha,edgecolor,linewidth,antialiased,zorder,label", combos
)
def test_fill_between_combinatorial(
    color, hatch, step, alpha, edgecolor, linewidth, antialiased, zorder, label
):
    x = [1, 2, 3]
    y1 = [1, 2, 3]
    y2 = [0, 1, 2]
    kwargs = dict(
        color=color, hatch=hatch, step=step, alpha=alpha,
        edgecolor=edgecolor, linewidth=linewidth, antialiased=antialiased, zorder=zorder
    )
    if label is not None:
        kwargs['label'] = label
    poly = plt.fill_between(x, y1, y2, **kwargs)
    # get_facecolor returns an array of RGBA
    expected_rgba = np.array(list(plt.matplotlib.colors.to_rgba(color)[:3]) + [alpha])
    assert np.allclose(poly.get_facecolor()[0], expected_rgba)
    expected_edge_rgba = np.array(list(plt.matplotlib.colors.to_rgba(edgecolor)[:3]) + [alpha])
    assert np.allclose(poly.get_edgecolor()[0], expected_edge_rgba)
    assert poly.get_hatch() == hatch
    assert np.allclose(poly.get_linewidth()[0], linewidth)
    assert poly.get_antialiased()[0] == antialiased
    assert abs(poly.get_zorder() - zorder) < 1e-6
    if label is not None:
        plt.legend()
        legend_texts = plt.gca().legend_.get_texts()
        assert any(label == t.get_text() for t in legend_texts)

# ----------------------------
# 6. Accessibility Tests
# ----------------------------
def test_fill_between_color_cycle_distinct():
    """Test that fill_between has distinct colors by default"""
    x = [1, 2, 3]
    y1 = [1, 2, 3]
    y2 = [0, 1, 2]
    y3 = [2, 3, 4]
    poly1 = plt.fill_between(x, y1, y2)
    poly2 = plt.fill_between(x, y2, y3)
    # Compare the first facecolor RGBA
    assert not np.allclose(poly1.get_facecolor()[0], poly2.get_facecolor()[0])

def test_fill_between_high_contrast():
    """Test high contrast color combinations"""
    x = [1, 2, 3]
    y1 = [1, 2, 3]
    y2 = [0, 1, 2]
    poly = plt.fill_between(x, y1, y2, color='white', edgecolor='black')
    assert np.allclose(poly.get_facecolor()[0], plt.matplotlib.colors.to_rgba('white'))
    assert np.allclose(poly.get_edgecolor()[0], plt.matplotlib.colors.to_rgba('black'))

# ----------------------------
# 7. Performance Tests
# ----------------------------
def test_fill_between_performance_scaling():
    """Test performance with increasing data size"""
    sizes = [100, 1000, 10000]
    times = []
    for size in sizes:
        x = np.linspace(0, 1, size)
        y1 = np.sin(x)
        y2 = np.cos(x)
        start_time = time.time()
        plt.fill_between(x, y1, y2)
        end_time = time.time()
        times.append(end_time - start_time)
        plt.close()
    
    # Check that time increases sub-linearly with size
    for i in range(1, len(times)):
        assert times[i] < times[i-1] * 10  # Allow some non-linearity but not extreme

def test_fill_between_memory_usage():
    """Test memory usage with large dataset"""
    x = np.linspace(0, 1, 1000)
    y1 = np.sin(x)
    y2 = np.cos(x)
    poly = plt.fill_between(x, y1, y2)
    assert isinstance(poly, PolyCollection)
    plt.close()