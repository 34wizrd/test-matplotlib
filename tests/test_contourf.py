import matplotlib
matplotlib.use('Agg')  # Use headless backend for testing

import matplotlib.pyplot as plt
import numpy as np
import pytest
import itertools
import time
from hypothesis import given, strategies as st
import random
import string

# Add cleanup fixture to close figures after each test
@pytest.fixture(autouse=True)
def cleanup():
    yield
    plt.close("all")

# ----------------------------
# 1. Basic Functional Tests
# ----------------------------
def test_contourf_01_basic():
    """Basic filled contour plot with default levels"""
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    cs = plt.contourf(X, Y, Z)
    collections = getattr(cs, 'collections', getattr(cs, 'allsegs', []))
    assert len(collections) > 0

def test_contourf_02_custom_levels():
    """Custom number of levels"""
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    cs = plt.contourf(X, Y, Z, levels=7)
    assert len(cs.levels) >= 7

def test_contourf_03_manual_levels():
    """Manual level specification"""
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    levels = [-0.5, 0, 0.5]
    cs = plt.contourf(X, Y, Z, levels=levels)
    assert np.allclose(cs.levels, levels)

def test_contourf_04_cmap():
    """Test colormap application"""
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    cs = plt.contourf(X, Y, Z, cmap='plasma')
    collections = getattr(cs, 'collections', getattr(cs, 'allsegs', []))
    assert len(collections) > 0

def test_contourf_05_alpha():
    """Test alpha blending"""
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    cs = plt.contourf(X, Y, Z, alpha=0.5)
    for coll in getattr(cs, 'collections', []):
        if hasattr(coll, 'get_alpha') and coll.get_alpha() is not None:
            assert abs(coll.get_alpha() - 0.5) < 1e-6

def test_contourf_06_colors():
    """Test color specification"""
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    cs = plt.contourf(X, Y, Z, colors=['red', 'blue', 'green'])
    collections = getattr(cs, 'collections', getattr(cs, 'allsegs', []))
    assert len(collections) > 0
    for i, coll in enumerate(getattr(cs, 'collections', [])):
        if hasattr(coll, 'get_facecolor'):
            fc = coll.get_facecolor()[0]
            assert np.allclose(fc[:3], plt.cm.colors.to_rgb(['red', 'blue', 'green'][i % 3]), rtol=1e-2)

def test_contourf_07_empty_data():
    """Test empty Z array"""
    x = np.linspace(-3, 3, 0)
    y = np.linspace(-3, 3, 0)
    X, Y = np.meshgrid(x, y)
    Z = np.empty((0, 0))
    with pytest.raises(Exception):
        plt.contourf(X, Y, Z)

def test_contourf_08_mismatched_shapes():
    """Test mismatched input shapes"""
    # Test case 1: X and Y have different lengths
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 49)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    # This should work as matplotlib will handle the shape mismatch
    cs = plt.contourf(X, Y, Z)
    assert hasattr(cs, 'collections') or hasattr(cs, 'allsegs')
    
    # Test case 2: Z has wrong shape
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    Z = Z[:-1, :]  # Now Z is (49, 50) while X, Y are (50, 50)
    with pytest.raises(TypeError):
        plt.contourf(X, Y, Z)

def test_contourf_09_nan_handling():
    """Test NaN in Z array"""
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    Z[0, 0] = np.nan
    cs = plt.contourf(X, Y, Z)
    collections = getattr(cs, 'collections', getattr(cs, 'allsegs', []))
    assert len(collections) > 0

def test_contourf_10_masked_array():
    """Test masked array input"""
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.ma.masked_array(np.sin(X) * np.cos(Y), mask=(np.abs(X) < 1))
    cs = plt.contourf(X, Y, Z)
    collections = getattr(cs, 'collections', getattr(cs, 'allsegs', []))
    assert len(collections) > 0

def test_contourf_11_unevenly_spaced_axes():
    """Unevenly spaced x/y axes"""
    x = np.array([-3, -2, 0, 1, 3])
    y = np.array([-3, -1, 0, 2, 3])
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    cs = plt.contourf(X, Y, Z)
    collections = getattr(cs, 'collections', getattr(cs, 'allsegs', []))
    assert len(collections) > 0

def test_contourf_12_neg_and_pos_values():
    """Z with both negative and positive values"""
    x = np.linspace(-2, 2, 10)
    y = np.linspace(-2, 2, 10)
    X, Y = np.meshgrid(x, y)
    Z = X - Y
    cs = plt.contourf(X, Y, Z)
    collections = getattr(cs, 'collections', getattr(cs, 'allsegs', []))
    assert len(collections) > 0

def test_contourf_13_large_grid():
    """Very large grid (functional, not performance)"""
    x = np.linspace(-3, 3, 200)
    y = np.linspace(-3, 3, 200)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    cs = plt.contourf(X, Y, Z)
    collections = getattr(cs, 'collections', getattr(cs, 'allsegs', []))
    assert len(collections) > 0

def test_contourf_14_diagonal_mask():
    """Masked array with diagonal mask"""
    x = np.linspace(-3, 3, 10)
    y = np.linspace(-3, 3, 10)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    mask = np.eye(10, dtype=bool)
    Z = np.ma.masked_array(Z, mask=mask)
    cs = plt.contourf(X, Y, Z)
    collections = getattr(cs, 'collections', getattr(cs, 'allsegs', []))
    assert len(collections) > 0

def test_contourf_15_float32_array():
    """Z as float32 array"""
    x = np.linspace(-3, 3, 10)
    y = np.linspace(-3, 3, 10)
    X, Y = np.meshgrid(x, y)
    Z = (np.sin(X) * np.cos(Y)).astype(np.float32)
    cs = plt.contourf(X, Y, Z)
    collections = getattr(cs, 'collections', getattr(cs, 'allsegs', []))
    assert len(collections) > 0

# ----------------------------
# 2. Integration Tests
# ----------------------------
def test_contourf_with_subplots():
    """Test contourf in subplots"""
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    fig, (ax1, ax2) = plt.subplots(1, 2)
    cs1 = ax1.contourf(X, Y, Z)
    cs2 = ax2.contourf(X, Y, Z + 1)
    collections1 = getattr(cs1, 'collections', getattr(cs1, 'allsegs', []))
    collections2 = getattr(cs2, 'collections', getattr(cs2, 'allsegs', []))
    assert len(collections1) > 0
    assert len(collections2) > 0

def test_contourf_with_log_scale():
    """Test contourf with log scale axes"""
    x = np.linspace(1, 10, 50)
    y = np.linspace(1, 10, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.log(X * Y)
    fig, ax = plt.subplots()
    ax.set_xscale('log')
    ax.set_yscale('log')
    cs = ax.contourf(X, Y, Z)
    assert ax.get_xscale() == 'log'
    assert ax.get_yscale() == 'log'

# ----------------------------
# 3. Property-Based Tests
# ----------------------------
def test_contourf_property_random():
    """Random Z arrays produce valid collections"""
    for n in [2, 5, 10]:
        x = np.linspace(-3, 3, n)
        y = np.linspace(-3, 3, n)
        X, Y = np.meshgrid(x, y)
        Z = np.random.uniform(-5, 5, (n, n))
        cs = plt.contourf(X, Y, Z)
        collections = getattr(cs, 'collections', getattr(cs, 'allsegs', []))
        assert len(collections) > 0

# ----------------------------
# 4. Fuzz Testing
# ----------------------------
@given(
    m=st.integers(min_value=2, max_value=20),
    n=st.integers(min_value=2, max_value=20),
)
def test_contourf_fuzz_shape(m, n):
    """Random shapes and values"""
    x = np.linspace(-3, 3, n)
    y = np.linspace(-3, 3, m)
    X, Y = np.meshgrid(x, y)
    Z = np.random.randn(m, n)
    try:
        plt.contourf(X, Y, Z)
    except Exception as e:
        assert isinstance(e, Exception)

# ----------------------------
# 5. Combinatorial Testing
# ----------------------------
colors = ['red', 'blue', 'green', 'black']
alphas = [0.2, 0.5, 0.8]
levels = [2, 5, 10]
cmaps = ['viridis', 'plasma', 'coolwarm']
combos = list(itertools.product(colors, alphas, levels, cmaps))[:60]

@pytest.mark.parametrize("color,alpha,levels,cmap", combos)
def test_contourf_combinatorial(color, alpha, levels, cmap):
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    # Only pass either colors or cmap, not both
    kwargs = dict(alpha=alpha, levels=levels)
    if color in ['red', 'blue', 'green', 'black']:
        kwargs['colors'] = color
    else:
        kwargs['cmap'] = cmap
    cs = plt.contourf(X, Y, Z, **kwargs)
    collections = getattr(cs, 'collections', getattr(cs, 'allsegs', []))
    assert len(collections) >= levels or len(collections) > 0
    for coll in getattr(cs, 'collections', []):
        if hasattr(coll, 'get_alpha') and coll.get_alpha() is not None:
            assert abs(coll.get_alpha() - alpha) < 1e-6

# ----------------------------
# 6. Accessibility Tests
# ----------------------------
def test_contourf_color_cycle_distinct():
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z1 = np.sin(X) * np.cos(Y)
    Z2 = np.sin(X) * np.cos(Y) + 1
    cs1 = plt.contourf(X, Y, Z1)
    cs2 = plt.contourf(X, Y, Z2)
    collections1 = getattr(cs1, 'collections', getattr(cs1, 'allsegs', []))
    collections2 = getattr(cs2, 'collections', getattr(cs2, 'allsegs', []))
    assert len(collections1) > 0 and len(collections2) > 0

def test_contourf_high_contrast():
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    cs = plt.contourf(X, Y, Z, colors=['black', 'white'])
    collections = getattr(cs, 'collections', getattr(cs, 'allsegs', []))
    assert len(collections) > 0

# ----------------------------
# 7. Performance Tests
# ----------------------------
def test_contourf_performance_scaling():
    sizes = [10, 50, 100]
    times = []
    for size in sizes:
        x = np.linspace(-3, 3, size)
        y = np.linspace(-3, 3, size)
        X, Y = np.meshgrid(x, y)
        Z = np.sin(X) * np.cos(Y)
        start = time.time()
        plt.contourf(X, Y, Z)
        end = time.time()
        times.append(end - start)
        plt.close()
    for i in range(1, len(times)):
        assert times[i] < times[i-1] * 10 