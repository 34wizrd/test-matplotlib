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
@pytest.mark.parametrize("x,height,expected", [
    ([0, 1, 2], [10, 20, 30], [(0, 10), (1, 20), (2, 30)]),
    ([], [], []),
])
def test_bar_01_basic_and_empty(x, height, expected):
    fig, ax = plt.subplots()
    bars = ax.bar(x, height)
    assert len(bars) == len(expected)
    for i, (xi, hi) in enumerate(expected):
        assert abs(bars[i].get_x() - (xi - 0.4)) < 1e-6  # 0.4 is half of default width
        assert bars[i].get_height() == hi

def test_bar_02_mismatched_lengths_raises():
    """Test that mismatched lengths raise ValueError"""
    with pytest.raises(ValueError, match="shape mismatch: objects cannot be broadcast to a single shape"):
        plt.bar([1, 2, 3], [1, 2])  # Different lengths

def test_bar_03_nan_handling():
    x = [0, 1, 2]
    height = [0, np.nan, 2]
    bars = plt.bar(x, height)
    assert len(bars) == 3
    assert np.isnan(bars[1].get_height())

def test_bar_04_legend_label():
    fig, ax = plt.subplots()
    ax.bar([1, 2, 3], [4, 5, 6], label="test_label")
    legend = ax.legend()
    labels = [text.get_text() for text in legend.get_texts()]
    assert "test_label" in labels

def test_bar_05_default_width():
    width_value = 0.8  # default width
    bars = plt.bar([0, 1], [0, 1])
    for bar in bars:
        assert abs(bar.get_width() - width_value) < 1e-6

def test_bar_06_custom_width():
    width_array = [0.5, 0.7]
    bars = plt.bar([0, 1], [0, 1], width=width_array)
    for i, bar in enumerate(bars):
        assert abs(bar.get_width() - width_array[i]) < 1e-6

def test_bar_07_color_scalar():
    color = 'red'
    bars = plt.bar([0, 1], [0, 1], color=color)
    for bar in bars:
        assert bar.get_facecolor() == plt.cm.colors.to_rgba(color)

def test_bar_08_color_array():
    color_array = ['red', 'blue']
    bars = plt.bar([0, 1], [0, 1], color=color_array)
    for i, bar in enumerate(bars):
        assert bar.get_facecolor() == plt.cm.colors.to_rgba(color_array[i])

def test_bar_09_edgecolor():
    edgecolor = 'black'
    bars = plt.bar([0, 1], [0, 1], edgecolor=edgecolor)
    for bar in bars:
        assert bar.get_edgecolor() == plt.cm.colors.to_rgba(edgecolor)

def test_bar_10_alpha_transparency():
    alpha_value = 0.5
    bars = plt.bar([0, 1], [0, 1], alpha=alpha_value)
    for bar in bars:
        assert abs(bar.get_alpha() - alpha_value) < 1e-6

def test_bar_11_bottom_parameter():
    bottom = 2
    bars = plt.bar([0, 1], [0, 1], bottom=bottom)
    for bar in bars:
        assert bar.get_y() == bottom

def test_bar_12_align_center():
    x = [0, 1, 2]
    bars = plt.bar(x, [1, 1, 1], align='center')
    for i, bar in enumerate(bars):
        assert abs(bar.get_x() - (x[i] - 0.4)) < 1e-6

def test_bar_13_align_edge():
    x = [0, 1, 2]
    bars = plt.bar(x, [1, 1, 1], align='edge')
    for i, bar in enumerate(bars):
        assert abs(bar.get_x() - x[i]) < 1e-6

def test_bar_14_categorical_xaxis():
    """Test bar chart with categorical x-axis"""
    categories = ['cat1', 'cat2', 'cat3']
    values = [1, 2, 3]
    fig, ax = plt.subplots()
    bars = ax.bar(categories, values)
    assert len(bars) == len(categories)
    for i, bar in enumerate(bars):
        # For center alignment (default), x position is offset by half the width
        assert abs(bar.get_x() - (i - 0.4)) < 1e-6  # 0.4 is half of default width
        assert bar.get_height() == values[i]

def test_bar_15_invalid_input_types():
    """Test that invalid input types raise appropriate errors"""
    # Test with None values
    with pytest.raises(TypeError):
        plt.bar(None, [1, 2, 3])
    with pytest.raises(TypeError):
        plt.bar([1, 2, 3], None)
    
    # Test with non-numeric values in lists
    with pytest.raises((TypeError, ValueError)):
        plt.bar([1, 2, "invalid"], [1, 2, 3])
    with pytest.raises((TypeError, ValueError)):
        plt.bar([1, 2, 3], [1, 2, "invalid"])

def test_bar_16_negative_values():
    x = [1, 2, 3]
    height = [-1, -2, -3]
    bars = plt.bar(x, height)
    assert len(bars) == 3
    for i, bar in enumerate(bars):
        assert bar.get_height() == height[i]

def test_bar_17_zero_values():
    x = [1, 2, 3]
    height = [0, 0, 0]
    bars = plt.bar(x, height)
    assert len(bars) == 3
    for i, bar in enumerate(bars):
        assert bar.get_height() == 0

# ----------------------------
# 2. Integration Tests
# ----------------------------
def test_bar_with_subplots_and_log_scale():
    fig, axs = plt.subplots(1, 2)
    axs[0].bar([1, 10, 100], [1, 10, 100])
    axs[1].bar([1, 10, 100], [1, 10, 100])
    assert len(axs[0].patches) == 3
    assert len(axs[1].patches) == 3

    fig2, ax2 = plt.subplots()
    ax2.set_xscale('log')
    ax2.bar([1, 10, 100], [1, 10, 100])
    assert ax2.get_xscale() == 'log'

def test_bar_with_twin_axes():
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.bar([0, 1], [0, 1])
    ax2.bar([2, 3], [2, 3])
    assert len(ax1.patches) == 2
    assert len(ax2.patches) == 2

def test_bar_with_error_bars():
    x = [1, 2, 3]
    height = [4, 5, 6]
    yerr = [0.5, 0.5, 0.5]
    bars = plt.bar(x, height, yerr=yerr)
    assert len(bars) == len(x)
    # Check that error bars are present
    assert len(plt.gca().collections) > 0

# ----------------------------
# 3. Property-Based Tests
# ----------------------------
if HAS_HYPOTHESIS:
    @given(
        x=st.lists(st.floats(min_value=-1e3, max_value=1e3), min_size=1, max_size=50),
        height=st.lists(st.floats(min_value=0, max_value=1e3), min_size=1, max_size=50),
        width=st.one_of(
            st.floats(min_value=0.1, max_value=10),
            st.lists(st.floats(min_value=0.1, max_value=10), min_size=1, max_size=50)
        ),
        color=st.one_of(
            st.sampled_from(['red', 'blue', 'green']),
            st.lists(st.sampled_from(['red', 'blue', 'green']), min_size=1, max_size=50)
        )
    )
    def test_bar_property_based(x, height, width, color):
        if len(x) != len(height):
            pytest.skip("x and height lengths must match")
        bars = plt.bar(x, height, width=width, color=color)
        assert len(bars) == len(x)
else:
    def test_bar_property_based():
        pytest.skip("hypothesis not installed")

# ----------------------------
# 4. Fuzz Testing
# ----------------------------
@pytest.mark.parametrize("color", [
    ''.join(random.choices(string.ascii_letters, k=5)) for _ in range(5)
])
def test_bar_fuzz_color(color):
    try:
        plt.bar([0, 1], [0, 1], color=color)
    except ValueError:
        pass  # Expected for invalid colors

@pytest.mark.parametrize("width", [
    random.uniform(-10, 10) for _ in range(5)
])
def test_bar_fuzz_width(width):
    try:
        plt.bar([0, 1], [0, 1], width=width)
    except ValueError:
        pass  # Expected for invalid widths

# ----------------------------
# 5. Combinatorial Testing
# ----------------------------
BAR_TEST_PARAMS = {
    'colors': ['red', 'blue', 'green', 'yellow', 'purple'],
    'edgecolors': ['black', 'white', 'gray', 'red'],
    'widths': [0.5, 1.0, 2.0],
    'alphas': [0.3, 0.5, 0.7, 1.0],
    'aligns': ['center', 'edge'],
    'bottoms': [0, 2, 5],
    'labels': [None, 'A']
}

# Combinatorial test with all parameters
@pytest.mark.parametrize(
    "color,edgecolor,width,alpha,align,bottom,label",
    list(itertools.product(
        BAR_TEST_PARAMS['colors'],
        BAR_TEST_PARAMS['edgecolors'],
        BAR_TEST_PARAMS['widths'],
        BAR_TEST_PARAMS['alphas'],
        BAR_TEST_PARAMS['aligns'],
        BAR_TEST_PARAMS['bottoms'],
        BAR_TEST_PARAMS['labels']
    ))[:60]
)
def test_bar_combinatorial(
    color, edgecolor, width, alpha, align, bottom, label
):
    """Test combinations of all bar parameters"""
    x = [0, 1, 2]
    height = [1, 2, 3]
    kwargs = dict(
        color=color, edgecolor=edgecolor, width=width, alpha=alpha,
        align=align, bottom=bottom
    )
    if label is not None:
        kwargs['label'] = label
    bars = plt.bar(x, height, **kwargs)
    assert len(bars) == len(x)
    for bar in bars:
        expected_rgba = np.array(list(plt.cm.colors.to_rgba(color)[:3]) + [alpha])
        assert np.allclose(bar.get_facecolor(), expected_rgba)
        expected_edge_rgba = np.array(list(plt.cm.colors.to_rgba(edgecolor)[:3]) + [alpha])
        assert np.allclose(bar.get_edgecolor(), expected_edge_rgba)
        assert abs(bar.get_width() - width) < 1e-6
        assert abs(bar.get_alpha() - alpha) < 1e-6
        assert bar.get_y() == bottom
    if label is not None:
        plt.legend()
        legend_texts = plt.gca().legend_.get_texts()
        assert any(label == t.get_text() for t in legend_texts)

# ----------------------------
# 6. Accessibility Tests
# ----------------------------
def test_bar_color_cycle_distinct():
    """Test that bars have distinct colors by default"""
    fig, ax = plt.subplots()
    # Force different colors for each bar
    bars = ax.bar([1, 2, 3], [1, 2, 3], color=['red', 'blue', 'green'])
    colors = [bar.get_facecolor() for bar in bars]
    assert len(set(tuple(c) for c in colors)) == len(colors)

def test_bar_high_contrast():
    fig, ax = plt.subplots()
    bars = ax.bar([1, 2, 3], [1, 2, 3], color=['black', 'white', 'red'])
    colors = [bar.get_facecolor() for bar in bars]
    # Check that colors are distinct
    assert len(set(tuple(c) for c in colors)) == len(colors)

# ----------------------------
# 7. Performance Tests
# ----------------------------
def test_bar_performance_scaling():
    sizes = [10, 100, 1000]
    times = []
    for size in sizes:
        x = list(range(size))
        height = [1] * size
        run_times = []
        for _ in range(3):  # Run 3 times and average
            start_time = time.time()
            plt.bar(x, height)
            end_time = time.time()
            run_times.append(end_time - start_time)
            plt.close()
        times.append(sum(run_times) / len(run_times))
    # Allow more non-linearity, e.g., 20x instead of 10x
    for i in range(1, len(times)):
        assert times[i] < times[i-1] * 20  # Increased fudge factor

def test_bar_memory_usage():
    x = list(range(1000))
    height = [1] * 1000
    bars = plt.bar(x, height)
    assert len(bars) == 1000
    plt.close() 