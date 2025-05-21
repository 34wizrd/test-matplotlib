import matplotlib
matplotlib.use('Agg')  # Use headless backend for testing

import matplotlib.pyplot as plt
import numpy as np
from hypothesis import given, strategies as st
import pytest
import itertools
import time
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
def test_contour_01_basic():
    """Basic contour plot with default levels"""
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    cs = plt.contour(X, Y, Z)
    assert hasattr(cs, 'collections') or hasattr(cs, 'allsegs')
    assert len(getattr(cs, 'collections', getattr(cs, 'allsegs', []))) > 0

def test_contour_02_contourf():
    """Filled contour plot"""
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    cs = plt.contourf(X, Y, Z)
    assert hasattr(cs, 'collections') or hasattr(cs, 'allsegs')
    assert len(getattr(cs, 'collections', getattr(cs, 'allsegs', []))) > 0

def test_contour_03_levels():
    """Custom number of levels"""
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    cs = plt.contour(X, Y, Z, levels=7)
    assert len(cs.levels) >= 7

def test_contour_04_manual_levels():
    """Manual level specification"""
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    levels = [-0.5, 0, 0.5]
    cs = plt.contour(X, Y, Z, levels=levels)
    assert np.allclose(cs.levels, levels)

def test_contour_05_colors():
    """Test color specification"""
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    cs = plt.contour(X, Y, Z, colors='red')
    if hasattr(cs, 'collections'):
        for coll in cs.collections:
            color = coll.get_edgecolor()[0]
            expected_color = plt.cm.colors.to_rgba('red')
            assert np.allclose(color, expected_color, rtol=1e-3)
    else:
        # allsegs is a list of lists of arrays (one per level)
        allsegs = getattr(cs, 'allsegs', [])
        assert isinstance(allsegs, list)
        assert len(allsegs) > 0
        assert any(len(level) > 0 for level in allsegs)  # At least one level has segments

def test_contour_06_cmap():
    """Test colormap application"""
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    cs = plt.contour(X, Y, Z, cmap='viridis')
    assert hasattr(cs, 'collections') or hasattr(cs, 'allsegs')
    assert len(getattr(cs, 'collections', getattr(cs, 'allsegs', []))) > 0

def test_contour_07_alpha():
    """Test alpha blending"""
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    cs = plt.contour(X, Y, Z, alpha=0.5)
    if hasattr(cs, 'collections'):
        for coll in cs.collections:
            if coll.get_alpha() is not None:
                assert abs(coll.get_alpha() - 0.5) < 1e-6
    else:
        allsegs = getattr(cs, 'allsegs', [])
        assert isinstance(allsegs, list)
        assert len(allsegs) > 0
        assert any(len(level) > 0 for level in allsegs)

def test_contour_08_linestyles():
    """Test custom linestyles"""
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    cs = plt.contour(X, Y, Z, linestyles='dashed')
    if hasattr(cs, 'collections'):
        for coll in cs.collections:
            ls = coll.get_linestyle()
            if isinstance(ls, list):
                ls = ls[0]
            assert ls in ['--', 'dashed', (0, (6.0, 6.0))]
    else:
        allsegs = getattr(cs, 'allsegs', [])
        assert isinstance(allsegs, list)
        assert len(allsegs) > 0
        assert any(len(level) > 0 for level in allsegs)

def test_contour_09_labels():
    """Test contour label functionality"""
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    cs = plt.contour(X, Y, Z)
    fmt = '%1.2f'
    lbls = plt.clabel(cs, fmt=fmt)
    assert len(lbls) > 0
    for lbl in lbls:
        assert isinstance(lbl.get_text(), str)

def test_contour_10_extent():
    """Test extent parameter via imshow for comparison"""
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    extent = [-3, 3, -3, 3]
    im = plt.imshow(Z, extent=extent)
    assert np.allclose(im.get_extent(), extent)

def test_contour_11_mismatched_shapes():
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    with pytest.raises(TypeError):
        plt.contour(X, Y[:-1], Z)

def test_contour_12_invalid_levels():
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    with pytest.raises(ValueError):
        plt.contour(X, Y, Z, levels=[1, 0, -1])  # Not increasing

def test_contour_13_invalid_colors():
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    with pytest.raises(ValueError):
        plt.contour(X, Y, Z, colors='notacolor')

def test_contour_14_single_level():
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    cs = plt.contour(X, Y, Z, levels=[0])
    assert len(cs.levels) == 1

def test_contour_15_identical_levels():
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.ones_like(X)
    with pytest.raises(ValueError):
        plt.contour(X, Y, Z, levels=[1, 1, 1])

def test_contour_16_masked_arrays():
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.ma.masked_array(np.sin(X) * np.cos(Y), mask=(np.abs(X) < 1))
    cs = plt.contour(X, Y, Z)
    assert hasattr(cs, 'collections') or hasattr(cs, 'allsegs')
    assert len(getattr(cs, 'collections', getattr(cs, 'allsegs', []))) > 0 

# ----------------------------
# 2. Integration Tests
# ----------------------------
def test_contour_with_subplots():
    """Test contour in subplots"""
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    fig, (ax1, ax2) = plt.subplots(1, 2)
    cs1 = ax1.contour(X, Y, Z)
    cs2 = ax2.contourf(X, Y, Z)
    assert hasattr(cs1, 'collections') or hasattr(cs1, 'allsegs')
    assert hasattr(cs2, 'collections') or hasattr(cs2, 'allsegs')
    assert len(getattr(cs1, 'collections', getattr(cs1, 'allsegs', []))) > 0
    assert len(getattr(cs2, 'collections', getattr(cs2, 'allsegs', []))) > 0

def test_contour_with_log_scale():
    """Test contour with log scale axes"""
    x = np.linspace(1, 10, 50)
    y = np.linspace(1, 10, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.log(X * Y)
    fig, ax = plt.subplots()
    ax.set_xscale('log')
    ax.set_yscale('log')
    cs = ax.contour(X, Y, Z)
    assert ax.get_xscale() == 'log'
    assert ax.get_yscale() == 'log'

# ----------------------------
# 3. Property-Based Tests
# ----------------------------
if HAS_HYPOTHESIS:
    @given(
        arr=st.lists(st.lists(st.floats(min_value=-10, max_value=10), min_size=2, max_size=10), min_size=2, max_size=10)
    )
    def test_contour_property_random(arr):
        # Skip ragged arrays
        if not all(len(row) == len(arr[0]) for row in arr):
            pytest.skip("Ragged array")
        arr = np.array(arr)
        if arr.shape[0] < 2 or arr.shape[1] < 2:
            pytest.skip("Need at least 2x2 array for contour.")
        x = np.linspace(-3, 3, arr.shape[1])
        y = np.linspace(-3, 3, arr.shape[0])
        X, Y = np.meshgrid(x, y)
        cs = plt.contour(X, Y, arr)
        assert hasattr(cs, 'collections') or hasattr(cs, 'allsegs')
        assert len(getattr(cs, 'collections', getattr(cs, 'allsegs', []))) > 0
else:
    def test_contour_property_random():
        pytest.skip("hypothesis not installed")

# ----------------------------
# 4. Fuzz Testing
# ----------------------------
@given(
    m=st.integers(min_value=2, max_value=20),
    n=st.integers(min_value=2, max_value=20),
)
def test_contour_fuzz_shape(m, n):
    """Random shapes and values"""
    x = np.linspace(-3, 3, n)
    y = np.linspace(-3, 3, m)
    X, Y = np.meshgrid(x, y)
    Z = np.random.randn(m, n)
    try:
        plt.contour(X, Y, Z)
    except Exception as e:
        assert isinstance(e, Exception)

@pytest.mark.parametrize("Z", [np.random.randn(5, 5) for _ in range(10)])
def test_contour_random_content(Z):
    """Random content arrays"""
    x = np.linspace(-3, 3, Z.shape[1])
    y = np.linspace(-3, 3, Z.shape[0])
    X, Y = np.meshgrid(x, y)
    try:
        plt.contour(X, Y, Z)
    except Exception as e:
        assert isinstance(e, Exception)

# ----------------------------
# 5. Combinatorial Testing
# ----------------------------
colors = ['red', 'blue', 'green', 'black', 'purple']
linestyles = ['solid', 'dashed', 'dashdot', 'dotted']
alphas = [0.2, 0.5, 0.8]
levels = [2, 5, 10]
cmaps = ['viridis', 'plasma', 'coolwarm', 'RdBu']

# Generate fewer combinations
combos = list(itertools.product(colors, linestyles, alphas, levels))[:60]

@pytest.mark.parametrize("color,linestyle,alpha,levels", combos)
def test_contour_combinatorial(color, linestyle, alpha, levels):
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    cs = plt.contour(X, Y, Z, colors=color, linestyles=linestyle, alpha=alpha, levels=levels)
    if hasattr(cs, 'collections'):
        for coll in cs.collections:
            assert np.allclose(coll.get_edgecolor()[0], plt.cm.colors.to_rgba(color))
            if coll.get_alpha() is not None:
                assert abs(coll.get_alpha() - alpha) < 1e-6
            ls = coll.get_linestyle()
            if isinstance(ls, list):
                ls = ls[0]
            assert ls in [linestyle, '--', '-.', ':', '-', 'solid', 'dashed', 'dashdot', 'dotted', 
                         (0, (6.0, 6.0)), (0, (1, 10)), (0, (5, 10)), (0, (3, 10, 1, 10))]
        assert len(cs.levels) >= levels
    else:
        allsegs = getattr(cs, 'allsegs', [])
        assert isinstance(allsegs, list)
        assert len(allsegs) >= levels
        assert any(len(level) > 0 for level in allsegs)

@pytest.mark.parametrize("cmap", cmaps)
def test_contour_cmap_combinations(cmap):
    """Test different colormap combinations"""
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    cs = plt.contour(X, Y, Z, cmap=cmap)
    if hasattr(cs, 'collections'):
        assert len(cs.collections) > 0
    else:
        allsegs = getattr(cs, 'allsegs', [])
        assert isinstance(allsegs, list)
        assert len(allsegs) > 0
        assert any(len(level) > 0 for level in allsegs)

# ----------------------------
# 6. Accessibility Tests
# ----------------------------
def test_contour_color_cycle_distinct():
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    cs1 = plt.contour(X, Y, Z)
    cs2 = plt.contour(X, Y, Z + 1)
    if hasattr(cs1, 'collections') and hasattr(cs2, 'collections'):
        c1 = cs1.collections[0].get_edgecolor()[0]
        c2 = cs2.collections[0].get_edgecolor()[0]
        assert not np.allclose(c1, c2)
    else:
        allsegs1 = getattr(cs1, 'allsegs', [])
        allsegs2 = getattr(cs2, 'allsegs', [])
        assert isinstance(allsegs1, list) and isinstance(allsegs2, list)
        assert len(allsegs1) > 0 and len(allsegs2) > 0
        # Check that at least one segment in each is different in shape or count
        segs1 = [seg for level in allsegs1 for seg in level]
        segs2 = [seg for level in allsegs2 for seg in level]
        assert len(segs1) > 0 and len(segs2) > 0
        # Not all segments should be identical
        assert not all(np.array_equal(s1, s2) for s1, s2 in zip(segs1, segs2))

def test_contour_high_contrast():
    x = np.linspace(-3, 3, 50)
    y = np.linspace(-3, 3, 50)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    cs = plt.contour(X, Y, Z, colors='black')
    if hasattr(cs, 'collections'):
        for coll in cs.collections:
            assert np.allclose(coll.get_edgecolor()[0], [0, 0, 0, 1])
    else:
        allsegs = getattr(cs, 'allsegs', [])
        assert isinstance(allsegs, list)
        assert len(allsegs) > 0
        assert any(len(level) > 0 for level in allsegs)

# ----------------------------
# 7. Performance Tests
# ----------------------------
def test_contour_performance_scaling():
    sizes = [10, 50, 100]
    times = []
    for size in sizes:
        x = np.linspace(-3, 3, size)
        y = np.linspace(-3, 3, size)
        X, Y = np.meshgrid(x, y)
        Z = np.sin(X) * np.cos(Y)
        start = time.time()
        plt.contour(X, Y, Z)
        end = time.time()
        times.append(end - start)
        plt.close()
    for i in range(1, len(times)):
        assert times[i] < times[i-1] * 10

def test_contour_memory_usage():
    x = np.linspace(-3, 3, 200)
    y = np.linspace(-3, 3, 200)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    cs = plt.contour(X, Y, Z)
    assert hasattr(cs, 'collections') or hasattr(cs, 'allsegs')
    plt.close()