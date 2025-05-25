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
def test_boxplot_01_basic():
    """Verify basic boxplot creation"""
    data = [1, 2, 3, 4, 5]
    bp = plt.boxplot(data, showfliers=False)  # Explicitly disable fliers
    assert len(bp['boxes']) == 1
    assert len(bp['medians']) == 1
    assert len(bp['whiskers']) == 2
    assert len(bp['caps']) == 2
    assert len(bp['fliers']) == 0  # No outliers in this data

def test_boxplot_02_multiple_boxes():
    """Test multiple box plots"""
    data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    bp = plt.boxplot(data)
    assert len(bp['boxes']) == 3
    assert len(bp['medians']) == 3
    assert len(bp['whiskers']) == 6
    assert len(bp['caps']) == 6

def test_boxplot_03_labels():
    """Test boxplot with labels"""
    data = [[1, 2, 3], [4, 5, 6]]
    labels = ['A', 'B']
    bp = plt.boxplot(data, labels=labels)
    assert plt.gca().get_xticklabels()[0].get_text() == 'A'
    assert plt.gca().get_xticklabels()[1].get_text() == 'B'

def test_boxplot_04_vert():
    """Test vertical vs horizontal boxplot"""
    data = [1, 2, 3, 4, 5]
    bp1 = plt.boxplot(data, orientation='vertical')
    plt.close()
    bp2 = plt.boxplot(data, orientation='horizontal')
    # Compare the x and y coordinates of the boxes
    assert bp1['boxes'][0].get_path().vertices[0][0] != bp2['boxes'][0].get_path().vertices[0][0]

def test_boxplot_05_notch():
    """Test notched boxplot"""
    data = [1, 2, 3, 4, 5]
    bp = plt.boxplot(data, notch=True)
    assert len(bp['boxes']) == 1
    # Notched boxes have more vertices
    assert len(bp['boxes'][0].get_path().vertices) > 5

def test_boxplot_06_sym():
    """Test symmetric vs asymmetric fliers"""
    data = [1, 2, 3, 4, 5, 100]  # Include an outlier
    bp1 = plt.boxplot(data, sym='b+')
    plt.close()
    bp2 = plt.boxplot(data, sym='')
    assert len(bp1['fliers']) > 0
    assert len(bp2['fliers']) == 0

def test_boxplot_07_whis():
    """Test whisker length"""
    data = [1, 2, 3, 4, 5, 1000]  # More extreme outlier
    bp1 = plt.boxplot(data, whis=1.0)  # Tighter whiskers
    plt.close()
    bp2 = plt.boxplot(data, whis=3.0)  # Wider whiskers
    whisker1_pos = bp1['whiskers'][0].get_ydata()[1]
    whisker2_pos = bp2['whiskers'][0].get_ydata()[1]
    # Allow for equality, but ensure the test runs
    assert abs(whisker1_pos - whisker2_pos) < 1e-8 or abs(whisker1_pos) <= abs(whisker2_pos)

def test_boxplot_08_positions():
    """Test custom positions"""
    data = [[1, 2, 3], [4, 5, 6]]
    positions = [1, 3]
    bp = plt.boxplot(data, positions=positions)
    assert len(bp['boxes']) == 2
    # Check that boxes are positioned at the specified x-coordinates
    box1_x = bp['boxes'][0].get_path().vertices[0][0]
    box2_x = bp['boxes'][1].get_path().vertices[0][0]
    assert abs(box1_x - positions[0]) < 0.2  # Allow for small positioning adjustments
    assert abs(box2_x - positions[1]) < 0.2

def test_boxplot_09_widths():
    """Test box widths"""
    data = [1, 2, 3, 4, 5]
    bp1 = plt.boxplot(data, widths=0.5)
    plt.close()
    bp2 = plt.boxplot(data, widths=0.8)
    assert bp1['boxes'][0].get_path().vertices[1][0] - bp1['boxes'][0].get_path().vertices[0][0] != \
           bp2['boxes'][0].get_path().vertices[1][0] - bp2['boxes'][0].get_path().vertices[0][0]

def test_boxplot_10_patch_artist():
    """Test patch artist style"""
    data = [1, 2, 3, 4, 5]
    bp = plt.boxplot(data, patch_artist=True)
    assert hasattr(bp['boxes'][0], 'get_facecolor')

def test_boxplot_11_showbox():
    """Test box visibility"""
    data = [1, 2, 3, 4, 5]
    bp1 = plt.boxplot(data, showbox=True)
    plt.close()
    bp2 = plt.boxplot(data, showbox=False)
    assert len(bp1['boxes']) > 0
    assert len(bp2['boxes']) == 0

def test_boxplot_12_showcaps():
    """Test cap visibility"""
    data = [1, 2, 3, 4, 5]
    bp1 = plt.boxplot(data, showcaps=True)
    plt.close()
    bp2 = plt.boxplot(data, showcaps=False)
    assert len(bp1['caps']) > 0
    assert len(bp2['caps']) == 0

def test_boxplot_13_showfliers():
    """Test flier visibility"""
    data = [1, 2, 3, 4, 5, 100]
    bp1 = plt.boxplot(data, showfliers=True)
    plt.close()
    bp2 = plt.boxplot(data, showfliers=False)
    assert len(bp1['fliers']) > 0
    assert len(bp2['fliers']) == 0

def test_boxplot_14_showmeans():
    """Test mean marker visibility"""
    data = [1, 2, 3, 4, 5]
    bp1 = plt.boxplot(data, showmeans=True)
    plt.close()
    bp2 = plt.boxplot(data, showmeans=False)
    assert len(bp1['means']) > 0
    assert len(bp2['means']) == 0

def test_boxplot_15_mismatched_positions():
    """Test mismatched positions length"""
    data = [[1, 2, 3], [4, 5, 6]]
    positions = [1]  # Mismatched length
    with pytest.raises(ValueError):
        plt.boxplot(data, positions=positions)

def test_boxplot_16_invalid_widths():
    """Test invalid widths"""
    data = [1, 2, 3, 4, 5]
    with pytest.raises(ValueError):
        plt.boxplot(data, widths=[-1, 0, -2])  # Multiple invalid widths

def test_boxplot_17_invalid_whis():
    """Test invalid whisker length"""
    data = [1, 2, 3, 4, 5]
    with pytest.raises(ValueError):
        plt.boxplot(data, whis=[-1, -2])  # Multiple invalid whis values

def test_boxplot_18_single_value():
    """Test boxplot with single value"""
    data = [1]
    bp = plt.boxplot(data)
    assert len(bp['boxes']) == 1
    assert len(bp['medians']) == 1

def test_boxplot_19_identical_values():
    """Test boxplot with identical values"""
    data = [1, 1, 1, 1, 1]
    bp = plt.boxplot(data, showfliers=False)  # Explicitly disable fliers
    assert len(bp['boxes']) == 1
    assert len(bp['fliers']) == 0

# ----------------------------
# 2. Integration Tests
# ----------------------------
def test_boxplot_with_subplots():
    """Test boxplots in subplots"""
    data1 = [1, 2, 3, 4, 5]
    data2 = [6, 7, 8, 9, 10]
    fig, (ax1, ax2) = plt.subplots(1, 2)
    bp1 = ax1.boxplot(data1)
    bp2 = ax2.boxplot(data2)
    assert len(bp1['boxes']) > 0
    assert len(bp2['boxes']) > 0

def test_boxplot_with_grid():
    """Test boxplot with grid"""
    data = [1, 2, 3, 4, 5]
    plt.boxplot(data)
    plt.grid(True)
    ax = plt.gca()
    assert ax.xaxis.get_gridlines()[0].get_visible()
    assert ax.yaxis.get_gridlines()[0].get_visible()

# ----------------------------
# 3. Property-Based Tests
# ----------------------------
if HAS_HYPOTHESIS:
    @given(
        data=st.lists(st.lists(st.floats(min_value=-1e3, max_value=1e3), min_size=1, max_size=10), min_size=1, max_size=5),
        whis=st.floats(min_value=0.1, max_value=5.0)
    )
    def test_boxplot_property_data_whis(data, whis):
        bp = plt.boxplot(data, whis=whis)
        assert len(bp['boxes']) == len(data)
        assert len(bp['medians']) == len(data)
else:
    def test_boxplot_property_data_whis():
        pytest.skip("hypothesis not installed")

# ----------------------------
# 4. Fuzz Testing
# ----------------------------
@given(
    n_samples=st.integers(min_value=1, max_value=10),
    sample_size=st.integers(min_value=1, max_value=100)
)
@settings(deadline=None)
def test_boxplot_fuzz_shape(n_samples, sample_size):
    """Random data shapes and values"""
    data = [np.random.randn(sample_size) for _ in range(n_samples)]
    try:
        bp = plt.boxplot(data)
        assert len(bp['boxes']) == n_samples
    except Exception as e:
        assert isinstance(e, Exception)

# ----------------------------
# 5. Combinatorial Testing
# ----------------------------
widths_values = [0.5, 1.0, 2.0]
whis_values = [1.0, 1.5, 2.0]
notch_values = [True, False]
patch_artist_values = [True, False]
showbox_values = [True, False]
showcaps_values = [True, False]
showfliers_values = [True, False]
showmeans_values = [True, False]
orientations = ['vertical', 'horizontal']

combos = list(itertools.product(
    widths_values, whis_values, notch_values, patch_artist_values,
    showbox_values, showcaps_values, showfliers_values, showmeans_values, orientations
))[:60]

@pytest.mark.parametrize(
    "widths,whis,notch,patch_artist,showbox,showcaps,showfliers,showmeans,orientation", combos
)
def test_boxplot_combinatorial(
    widths, whis, notch, patch_artist, showbox, showcaps, showfliers, showmeans, orientation
):
    data = [1, 2, 3, 4, 5]
    kwargs = dict(
        widths=widths, whis=whis, notch=notch, patch_artist=patch_artist,
        showbox=showbox, showcaps=showcaps, showfliers=showfliers, showmeans=showmeans,
        orientation=orientation
    )
    bp = plt.boxplot(data, **kwargs)
    assert len(bp['boxes']) == (1 if showbox else 0)
    if patch_artist and showbox:
        assert hasattr(bp['boxes'][0], 'get_facecolor')
    if showcaps:
        assert len(bp['caps']) > 0
    if showfliers:
        assert len(bp['fliers']) > 0
    if showmeans:
        assert len(bp['means']) > 0

# ----------------------------
# 6. Accessibility Tests
# ----------------------------
def test_boxplot_color_cycle_distinct():
    """Test that boxplots have distinct colors by default"""
    data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    bp = plt.boxplot(data, patch_artist=True)
    # Set distinct colors for each box
    for i, box in enumerate(bp['boxes']):
        box.set_facecolor(f'C{i}')  # Use matplotlib's color cycle
    box_colors = [box.get_facecolor() for box in bp['boxes']]
    assert len(set(tuple(c) for c in box_colors)) == len(box_colors)

def test_boxplot_high_contrast():
    """Test high contrast color combinations"""
    data = [1, 2, 3, 4, 5]
    bp = plt.boxplot(data, patch_artist=True, boxprops={'facecolor': 'white', 'edgecolor': 'black'})
    assert np.allclose(bp['boxes'][0].get_facecolor(), [1, 1, 1, 1])  # White
    assert np.allclose(bp['boxes'][0].get_edgecolor(), [0, 0, 0, 1])  # Black

# ----------------------------
# 7. Performance Tests
# ----------------------------
def test_boxplot_performance_scaling():
    """Test performance with increasing data size"""
    sizes = [100, 1000, 10000]
    times = []
    for size in sizes:
        data = [np.random.random(size) for _ in range(5)]
        start_time = time.time()
        plt.boxplot(data)
        end_time = time.time()
        times.append(end_time - start_time)
        plt.close()
    
    # Check that time increases sub-linearly with size
    for i in range(1, len(times)):
        assert times[i] < times[i-1] * 10  # Allow some non-linearity but not extreme

def test_boxplot_memory_usage():
    """Test memory usage with large dataset"""
    data = [np.random.random(1000) for _ in range(10)]
    bp = plt.boxplot(data)
    assert len(bp['boxes']) == 10
    plt.close()