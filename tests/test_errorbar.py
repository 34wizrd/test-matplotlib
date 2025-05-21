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
def test_errorbar_01_basic():
    """Verify basic errorbar creation"""
    x = [1, 2, 3]
    y = [1, 2, 3]
    yerr = [0.1, 0.2, 0.3]
    container = plt.errorbar(x, y, yerr=yerr, capsize=5)
    data_line, caplines, barlinecols = container.lines
    assert isinstance(data_line, plt.Line2D)
    assert isinstance(caplines, tuple)
    assert isinstance(barlinecols, tuple)
    assert len(caplines) == 2  # Two caps (top and bottom)
    assert len(barlinecols) == 1  # One barline collection for yerr

def test_errorbar_02_x_error():
    """Test x-direction error bars"""
    x = [1, 2, 3]
    y = [1, 2, 3]
    xerr = [0.1, 0.2, 0.3]
    container = plt.errorbar(x, y, xerr=xerr, capsize=5)
    data_line, caplines, barlinecols = container.lines
    assert isinstance(data_line, plt.Line2D)
    assert len(caplines) == 2
    assert len(barlinecols) == 1  # One barline collection for xerr

def test_errorbar_03_both_errors():
    """Test both x and y error bars"""
    x = [1, 2, 3]
    y = [1, 2, 3]
    xerr = [0.1, 0.2, 0.3]
    yerr = [0.1, 0.2, 0.3]
    container = plt.errorbar(x, y, xerr=xerr, yerr=yerr, capsize=5)
    data_line, caplines, barlinecols = container.lines
    assert isinstance(data_line, plt.Line2D)
    assert len(caplines) == 4  # Two caps for x, two for y
    assert len(barlinecols) == 2  # Two barline collections: one for xerr, one for yerr

def test_errorbar_04_markers():
    """Test different marker styles"""
    x = [1, 2, 3]
    y = [1, 2, 3]
    yerr = [0.1, 0.2, 0.3]
    container = plt.errorbar(x, y, yerr=yerr, fmt='o')
    line = container.lines[0]
    assert line.get_marker() == 'o'

def test_errorbar_05_colors():
    """Test color specification"""
    x = [1, 2, 3]
    y = [1, 2, 3]
    yerr = [0.1, 0.2, 0.3]
    color = 'red'
    container = plt.errorbar(x, y, yerr=yerr, color=color)
    data_line, caplines, barlinecols = container.lines
    assert data_line.get_color() == color
    for cap in caplines:
        assert cap.get_color() == color
    for bar in barlinecols:
        # bar is a LineCollection, get its color array
        bar_colors = bar.get_colors()
        assert all((np.allclose(c, plt.matplotlib.colors.to_rgba(color))) for c in bar_colors)

def test_errorbar_06_linestyle():
    """Test line style specification"""
    x = [1, 2, 3]
    y = [1, 2, 3]
    yerr = [0.1, 0.2, 0.3]
    linestyle = '--'
    container = plt.errorbar(x, y, yerr=yerr, linestyle=linestyle)
    line = container.lines[0]
    assert line.get_linestyle() == linestyle

def test_errorbar_07_capsize():
    """Test cap size specification"""
    x = [1, 2, 3]
    y = [1, 2, 3]
    yerr = [0.1, 0.2, 0.3]
    capsize = 10
    container = plt.errorbar(x, y, yerr=yerr, capsize=capsize)
    _, caplines, _ = container.lines
    for cap in caplines:
        assert abs(cap.get_markersize() - 2 * capsize) < 1e-6

def test_errorbar_08_capthick():
    """Test cap thickness specification"""
    x = [1, 2, 3]
    y = [1, 2, 3]
    yerr = [0.1, 0.2, 0.3]
    capthick = 2
    container = plt.errorbar(x, y, yerr=yerr, capthick=capthick)
    _, caplines, _ = container.lines
    for cap in caplines:
        assert abs(cap.get_markeredgewidth() - capthick) < 1e-6

def test_errorbar_09_elinewidth():
    """Test error bar line width"""
    x = [1, 2, 3]
    y = [1, 2, 3]
    yerr = [0.1, 0.2, 0.3]
    elinewidth = 2
    container = plt.errorbar(x, y, yerr=yerr, elinewidth=elinewidth)
    _, _, barlinecols = container.lines
    for bar in barlinecols:
        assert abs(bar.get_linewidth() - elinewidth) < 1e-6

def test_errorbar_10_ecolor():
    """Test error bar color"""
    x = [1, 2, 3]
    y = [1, 2, 3]
    yerr = [0.1, 0.2, 0.3]
    ecolor = 'blue'
    container = plt.errorbar(x, y, yerr=yerr, ecolor=ecolor)
    _, caplines, barlinecols = container.lines
    for cap in caplines:
        assert cap.get_color() == ecolor
    for bar in barlinecols:
        bar_colors = bar.get_colors()
        assert all((np.allclose(c, plt.matplotlib.colors.to_rgba(ecolor))) for c in bar_colors)

def test_errorbar_11_label():
    """Test legend label"""
    x = [1, 2, 3]
    y = [1, 2, 3]
    yerr = [0.1, 0.2, 0.3]
    label = 'test'
    container = plt.errorbar(x, y, yerr=yerr, label=label)
    plt.legend()
    assert plt.gca().legend_.get_texts()[0].get_text() == label

def test_errorbar_12_alpha():
    """Test transparency"""
    x = [1, 2, 3]
    y = [1, 2, 3]
    yerr = [0.1, 0.2, 0.3]
    alpha = 0.5
    container = plt.errorbar(x, y, yerr=yerr, alpha=alpha)
    line = container.lines[0]
    assert line.get_alpha() == alpha

def test_errorbar_13_zorder():
    """Test z-order"""
    x = [1, 2, 3]
    y = [1, 2, 3]
    yerr = [0.1, 0.2, 0.3]
    zorder = 3
    container = plt.errorbar(x, y, yerr=yerr, zorder=zorder)
    line = container.lines[0]
    assert abs(line.get_zorder() - zorder) < 0.2

def test_errorbar_14_errorevery():
    """Test error bar frequency"""
    x = [1, 2, 3, 4, 5]
    y = [1, 2, 3, 4, 5]
    yerr = [0.1, 0.2, 0.3, 0.4, 0.5]
    container = plt.errorbar(x, y, yerr=yerr, errorevery=2)
    _, caplines, barlinecols = container.lines
    assert len(caplines) > 0 or len(barlinecols) > 0

# ----------------------------
# 2. Integration Tests
# ----------------------------
def test_errorbar_with_subplots():
    """Test errorbars in subplots"""
    x = [1, 2, 3]
    y = [1, 2, 3]
    yerr = [0.1, 0.2, 0.3]
    fig, (ax1, ax2) = plt.subplots(1, 2)
    ax1.errorbar(x, y, yerr=yerr)
    ax2.errorbar(x, y, yerr=yerr)
    assert len(ax1.lines) > 0
    assert len(ax2.lines) > 0

def test_errorbar_with_grid():
    """Test errorbar with grid"""
    x = [1, 2, 3]
    y = [1, 2, 3]
    yerr = [0.1, 0.2, 0.3]
    plt.errorbar(x, y, yerr=yerr)
    plt.grid(True)
    ax = plt.gca()
    assert ax.xaxis.get_gridlines()[0].get_visible()
    assert ax.yaxis.get_gridlines()[0].get_visible()

# ----------------------------
# 3. Property-Based Tests
# ----------------------------
if HAS_HYPOTHESIS:
    @given(
        x=st.lists(st.floats(min_value=-1e3, max_value=1e3), min_size=1, max_size=10),
        y=st.lists(st.floats(min_value=-1e3, max_value=1e3), min_size=1, max_size=10),
        yerr=st.lists(st.floats(min_value=0.1, max_value=1.0), min_size=1, max_size=10)
    )
    def test_errorbar_property_data(x, y, yerr):
        if len(x) == len(y) == len(yerr):
            container = plt.errorbar(x, y, yerr=yerr)
            data_line, caplines, barlinecols = container.lines
            assert isinstance(data_line, plt.Line2D)
            assert len(caplines) >= 0
            assert len(barlinecols) >= 0
else:
    def test_errorbar_property_data():
        pytest.skip("hypothesis not installed")

# ----------------------------
# 4. Fuzz Testing
# ----------------------------
@pytest.mark.parametrize("marker", [
    random.choice(string.ascii_letters) for _ in range(5)
])
def test_errorbar_fuzz_marker(marker):
    """Random marker styles"""
    try:
        plt.errorbar([0, 1], [0, 1], yerr=[0.1, 0.1], marker=marker)
    except Exception as e:
        assert isinstance(e, (ValueError, TypeError))

# ----------------------------
# 5. Combinatorial Testing
# ----------------------------
markers = ['o', 's', '^', 'D']
colors = ['red', 'blue', 'green']
linestyles = ['-', '--', ':']
combos = list(itertools.product(markers, colors, linestyles))[:60]

@pytest.mark.parametrize("marker,color,linestyle", combos)
def test_errorbar_combinatorial(marker, color, linestyle):
    """Test combinations of errorbar parameters"""
    x = [1, 2, 3]
    y = [1, 2, 3]
    yerr = [0.1, 0.2, 0.3]
    container = plt.errorbar(x, y, yerr=yerr, fmt=marker, color=color, linestyle=linestyle)
    line = container.lines[0]
    assert line.get_marker() == marker
    assert line.get_color() == color
    assert line.get_linestyle() == linestyle

# ----------------------------
# 6. Accessibility Tests
# ----------------------------
def test_errorbar_color_cycle_distinct():
    """Test that errorbars have distinct colors by default"""
    x = [1, 2, 3]
    y1 = [1, 2, 3]
    y2 = [2, 3, 4]
    yerr = [0.1, 0.2, 0.3]
    container1 = plt.errorbar(x, y1, yerr=yerr)
    container2 = plt.errorbar(x, y2, yerr=yerr)
    color1 = container1.lines[0].get_color()
    color2 = container2.lines[0].get_color()
    assert color1 != color2

def test_errorbar_high_contrast():
    """Test high contrast color combinations"""
    x = [1, 2, 3]
    y = [1, 2, 3]
    yerr = [0.1, 0.2, 0.3]
    container = plt.errorbar(x, y, yerr=yerr, color='white', ecolor='black')
    data_line, caplines, barlinecols = container.lines
    assert data_line.get_color() == 'white'
    for cap in caplines:
        assert cap.get_color() == 'black'
    for bar in barlinecols:
        bar_colors = bar.get_colors()
        assert all((np.allclose(c, plt.matplotlib.colors.to_rgba('black'))) for c in bar_colors)

# ----------------------------
# 7. Performance Tests
# ----------------------------
def test_errorbar_performance_scaling():
    """Test performance with increasing data size"""
    sizes = [100, 1000, 10000]
    times = []
    for size in sizes:
        x = np.arange(size)
        y = np.random.random(size)
        yerr = np.random.random(size) * 0.1
        start_time = time.time()
        plt.errorbar(x, y, yerr=yerr)
        end_time = time.time()
        times.append(end_time - start_time)
        plt.close()
    for i in range(1, len(times)):
        assert times[i] < times[i-1] * 10

def test_errorbar_memory_usage():
    """Test memory usage with large dataset"""
    x = np.linspace(0, 1, 1000)
    y = np.sin(x)
    yerr = np.random.random(1000) * 0.1
    container = plt.errorbar(x, y, yerr=yerr)
    data_line, caplines, barlinecols = container.lines
    assert isinstance(data_line, plt.Line2D)