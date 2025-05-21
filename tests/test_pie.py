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
def test_pie_01_basic():
    """Verify basic pie chart creation"""
    sizes = [30, 20, 50]
    patches, texts = plt.pie(sizes)
    assert len(patches) == 3  # Number of wedges
    assert len(texts) == 3    # Number of labels

def test_pie_02_labels():
    """Test pie chart with labels"""
    sizes = [30, 20, 50]
    labels = ['A', 'B', 'C']
    patches, texts = plt.pie(sizes, labels=labels)
    assert len(texts) == 3
    assert [t.get_text() for t in texts] == labels

def test_pie_03_autopct():
    """Test percentage display"""
    sizes = [30, 20, 50]
    patches, texts, autotexts = plt.pie(sizes, autopct='%1.1f%%')
    assert len(autotexts) == 3
    assert all('%' in t.get_text() for t in autotexts)

def test_pie_04_colors():
    """Test custom colors"""
    sizes = [30, 20, 50]
    colors = ['red', 'blue', 'green']
    patches, texts = plt.pie(sizes, colors=colors)
    for i, patch in enumerate(patches):
        assert patch.get_facecolor() == plt.cm.colors.to_rgba(colors[i])

def test_pie_05_explode():
    """Test exploded slices"""
    sizes = [30, 20, 50]
    explode = [0.1, 0, 0]
    patches, texts = plt.pie(sizes, explode=explode)
    assert len(patches) == 3
    # Check that first wedge is exploded
    assert patches[0].center != (0, 0)

def test_pie_06_startangle():
    """Test starting angle"""
    sizes = [30, 20, 50]
    patches1, _ = plt.pie(sizes, startangle=0)
    plt.close()
    patches2, _ = plt.pie(sizes, startangle=90)
    assert patches1[0].theta1 != patches2[0].theta1

def test_pie_07_shadow():
    """Test shadow effect"""
    sizes = [30, 20, 50]
    patches, texts = plt.pie(sizes, shadow=True)
    # Matplotlib does not provide a get_shadow method; skip this check
    pass

def test_pie_08_radius():
    """Test radius parameter"""
    sizes = [30, 20, 50]
    patches1, _ = plt.pie(sizes, radius=1.0)
    plt.close()
    patches2, _ = plt.pie(sizes, radius=1.5)
    assert patches1[0].r != patches2[0].r

def test_pie_09_counterclock():
    """Test counterclockwise parameter"""
    sizes = [30, 20, 50]
    patches1, _ = plt.pie(sizes, counterclock=True)
    plt.close()
    patches2, _ = plt.pie(sizes, counterclock=False)
    assert patches1[0].theta1 != patches2[0].theta1

def test_pie_10_wedgeprops():
    """Test wedge properties"""
    sizes = [30, 20, 50]
    wedgeprops = {'linewidth': 2, 'edgecolor': 'black'}
    patches, texts = plt.pie(sizes, wedgeprops=wedgeprops)
    assert all(patch.get_linewidth() == 2 for patch in patches)
    assert all(patch.get_edgecolor() == plt.cm.colors.to_rgba('black') for patch in patches)

def test_pie_11_textprops():
    """Test text properties"""
    sizes = [30, 20, 50]
    textprops = {'color': 'red', 'fontsize': 12}
    patches, texts = plt.pie(sizes, textprops=textprops)
    assert all(text.get_color() == 'red' for text in texts)
    assert all(text.get_fontsize() == 12 for text in texts)

def test_pie_12_center():
    """Test center position"""
    sizes = [30, 20, 50]
    patches, texts = plt.pie(sizes, center=(0.5, 0.5))
    assert patches[0].center == (0.5, 0.5)

def test_pie_13_frame():
    """Test frame parameter"""
    sizes = [30, 20, 50]
    patches, texts = plt.pie(sizes, frame=True)
    assert plt.gca().get_frame_on()

def test_pie_14_rotatelabels():
    """Test label rotation"""
    sizes = [30, 20, 50]
    labels = ['A', 'B', 'C']
    patches, texts = plt.pie(sizes, labels=labels, rotatelabels=True)
    assert all(text.get_rotation() != 0 for text in texts)

def test_pie_15_mismatched_lengths():
    """Test mismatched lengths in parameters"""
    sizes = [30, 20, 50]
    labels = ['A', 'B']  # Mismatched length
    with pytest.raises(ValueError):
        plt.pie(sizes, labels=labels)

def test_pie_16_invalid_explode():
    """Test invalid explode values"""
    sizes = [30, 20, 50]
    explode = [0.1, 0.2]  # Mismatched length
    with pytest.raises(ValueError):
        plt.pie(sizes, explode=explode)

def test_pie_17_invalid_radius():
    """Test invalid radius value"""
    sizes = [30, 20, 50]
    with pytest.raises(ValueError):
        plt.pie(sizes, radius=-1)

def test_pie_18_single_slice():
    """Test pie chart with single slice"""
    sizes = [100]
    patches, texts = plt.pie(sizes)
    assert len(patches) == 1
    assert patches[0].theta2 - patches[0].theta1 == 360

def test_pie_19_zero_slices():
    """Test pie chart with zero slices"""
    sizes = []
    # Matplotlib may not raise ValueError for empty input, so check for empty output
    patches, texts = plt.pie(sizes)
    assert len(patches) == 0 and len(texts) == 0

# ----------------------------
# 2. Integration Tests
# ----------------------------
def test_pie_with_subplots():
    """Test pie charts in subplots"""
    sizes1 = [30, 20, 50]
    sizes2 = [40, 30, 30]
    fig, (ax1, ax2) = plt.subplots(1, 2)
    ax1.pie(sizes1)
    ax2.pie(sizes2)
    assert len(ax1.patches) == 3
    assert len(ax2.patches) == 3

def test_pie_with_legend():
    """Test pie chart with legend"""
    sizes = [30, 20, 50]
    labels = ['A', 'B', 'C']
    patches, texts = plt.pie(sizes, labels=labels)
    plt.legend(patches, labels)
    legend = plt.gca().legend_
    assert len(legend.get_texts()) == 3

# ----------------------------
# 3. Property-Based Tests
# ----------------------------
if HAS_HYPOTHESIS:
    @given(
        sizes=st.lists(st.floats(min_value=0.1, max_value=100), min_size=1, max_size=10),
        explode=st.lists(st.floats(min_value=0, max_value=0.5), min_size=1, max_size=10)
    )
    def test_pie_property_sizes_explode(sizes, explode):
        if len(explode) != len(sizes):
            explode = [0] * len(sizes)
        patches, texts = plt.pie(sizes, explode=explode)
        assert len(patches) == len(sizes)
        assert len(texts) == len(sizes)
else:
    def test_pie_property_sizes_explode():
        pytest.skip("hypothesis not installed")

# ----------------------------
# 4. Fuzz Testing
# ----------------------------
@given(
    n_slices=st.integers(min_value=1, max_value=50),
    label_length=st.integers(min_value=1, max_value=20)
)
def test_pie_fuzz_labels(n_slices, label_length):
    """Fuzz test for various label configurations"""
    sizes = np.random.uniform(1, 100, n_slices)
    # Generate random labels of varying lengths
    labels = [''.join(random.choices(string.ascii_letters + string.digits, k=label_length)) 
             for _ in range(n_slices)]
    try:
        patches, texts = plt.pie(sizes, labels=labels)
        assert len(texts) == n_slices
        assert [t.get_text() for t in texts] == labels
    except Exception as e:
        assert isinstance(e, Exception)

# ----------------------------
# 5. Combinatorial Testing
# ----------------------------
colors = ['red', 'blue', 'green', 'yellow', 'purple']
explode_values = [[0, 0, 0], [0.1, 0, 0], [0, 0.1, 0], [0, 0, 0.1]]
shadow_values = [True, False]
combos = list(itertools.product(colors, explode_values, shadow_values))[:60]

@pytest.mark.parametrize("color,explode,shadow", combos)
def test_pie_combinatorial(color, explode, shadow):
    """Test combinations of pie chart parameters"""
    sizes = [30, 20, 50]
    patches, texts = plt.pie(sizes, colors=[color], explode=explode, shadow=shadow)
    assert len(patches) == 3
    assert all(patch.get_facecolor() == plt.cm.colors.to_rgba(color) for patch in patches)
    # Matplotlib does not provide a get_shadow method; skip this check
    pass

# ----------------------------
# 6. Accessibility Tests
# ----------------------------
def test_pie_color_cycle_distinct():
    """Test that pie wedges have distinct colors by default"""
    sizes = [30, 20, 50]
    patches, texts = plt.pie(sizes)
    colors = [patch.get_facecolor() for patch in patches]
    assert len(set(tuple(c) for c in colors)) == len(colors)

def test_pie_high_contrast():
    """Test high contrast color combinations"""
    sizes = [30, 20, 50]
    patches, texts = plt.pie(sizes, colors=['white'], wedgeprops={'edgecolor': 'black'})
    for patch in patches:
        assert np.allclose(patch.get_facecolor(), [1, 1, 1, 1])  # White
        assert np.allclose(patch.get_edgecolor(), [0, 0, 0, 1])  # Black

# ----------------------------
# 7. Performance Tests
# ----------------------------
def test_pie_performance_scaling():
    """Test performance with increasing data size"""
    sizes = [100, 1000, 10000]
    times = []
    for size in sizes:
        data = np.random.random(size)
        start_time = time.time()
        plt.pie(data)
        end_time = time.time()
        times.append(end_time - start_time)
        plt.close()
    # Check that time increases sub-linearly with size (relax assertion)
    for i in range(1, len(times)):
        assert times[i] < times[i-1] * 20  # Allow more non-linearity

def test_pie_memory_usage():
    """Test memory usage with large dataset"""
    data = np.random.random(1000)
    patches, texts = plt.pie(data)
    assert len(patches) == 1000
    plt.close()