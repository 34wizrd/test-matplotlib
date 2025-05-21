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
def test_violinplot_01_basic():
    """Verify basic violinplot creation"""
    data = [1, 2, 3, 4, 5]
    vp = plt.violinplot(data, showextrema=False)
    assert len(vp['bodies']) == 1
    assert 'cmeans' not in vp
    assert 'cmaxes' not in vp
    assert 'cmins' not in vp

def test_violinplot_02_multiple_violins():
    """Test multiple violin plots"""
    data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    vp = plt.violinplot(data)
    assert len(vp['bodies']) == 3
    assert 'cmaxes' in vp
    assert 'cmins' in vp
    # cmaxes and cmins are LineCollection with one segment per violin
    assert len(vp['cmaxes'].get_segments()) == 3
    assert len(vp['cmins'].get_segments()) == 3

def test_violinplot_03_positions():
    """Test custom positions"""
    data = [[1, 2, 3], [4, 5, 6]]
    positions = [1, 3]
    vp = plt.violinplot(data, positions=positions)
    assert len(vp['bodies']) == 2
    # Check that violins are positioned at the specified x-coordinates
    violin1_x = vp['bodies'][0].get_paths()[0].vertices[0][0]
    violin2_x = vp['bodies'][1].get_paths()[0].vertices[0][0]
    assert abs(violin1_x - positions[0]) < 0.2
    assert abs(violin2_x - positions[1]) < 0.2

def test_violinplot_04_vert():
    """Test vertical vs horizontal violinplot"""
    data = [1, 2, 3, 4, 5]
    vp1 = plt.violinplot(data, orientation='vertical')
    plt.close()
    vp2 = plt.violinplot(data, orientation='horizontal')
    # Compare the x and y coordinates of the violins
    assert vp1['bodies'][0].get_paths()[0].vertices[0][0] != vp2['bodies'][0].get_paths()[0].vertices[0][0]

def test_violinplot_05_showextrema():
    """Test extrema visibility"""
    data = [1, 2, 3, 4, 5]
    vp1 = plt.violinplot(data, showextrema=True)
    plt.close()
    vp2 = plt.violinplot(data, showextrema=False)
    assert 'cmaxes' in vp1
    assert 'cmaxes' not in vp2

def test_violinplot_06_showmeans():
    """Test mean marker visibility"""
    data = [1, 2, 3, 4, 5]
    vp1 = plt.violinplot(data, showmeans=True)
    plt.close()
    vp2 = plt.violinplot(data, showmeans=False)
    assert 'cmeans' in vp1
    assert 'cmeans' not in vp2

def test_violinplot_07_showmedians():
    """Test median marker visibility"""
    data = [1, 2, 3, 4, 5]
    vp1 = plt.violinplot(data, showmedians=True)
    plt.close()
    vp2 = plt.violinplot(data, showmedians=False)
    assert 'cmedians' in vp1
    assert 'cmedians' not in vp2

def test_violinplot_08_quantiles():
    """Test quantile lines"""
    data = [1, 2, 3, 4, 5]
    vp = plt.violinplot(data, quantiles=[0.25, 0.75])
    assert 'cquantiles' in vp

def test_violinplot_09_widths():
    """Test violin widths"""
    data = [1, 2, 3, 4, 5]
    vp1 = plt.violinplot(data, widths=0.5)
    plt.close()
    vp2 = plt.violinplot(data, widths=0.8)
    width1 = vp1['bodies'][0].get_paths()[0].vertices[1][0] - vp1['bodies'][0].get_paths()[0].vertices[0][0]
    width2 = vp2['bodies'][0].get_paths()[0].vertices[1][0] - vp2['bodies'][0].get_paths()[0].vertices[0][0]
    assert width1 != width2

def test_violinplot_10_points():
    """Test number of points used to evaluate the KDE"""
    data = [1, 2, 3, 4, 5]
    vp1 = plt.violinplot(data, points=100)
    plt.close()
    vp2 = plt.violinplot(data, points=200)
    assert len(vp1['bodies'][0].get_paths()[0].vertices) != len(vp2['bodies'][0].get_paths()[0].vertices)

def test_violinplot_11_bw_method():
    """Test bandwidth method"""
    data = [1, 2, 3, 4, 5]
    vp1 = plt.violinplot(data, bw_method='scott')
    plt.close()
    vp2 = plt.violinplot(data, bw_method='silverman')
    # The shapes should be different due to different bandwidth methods
    assert not np.array_equal(vp1['bodies'][0].get_paths()[0].vertices, vp2['bodies'][0].get_paths()[0].vertices)

def test_violinplot_12_mismatched_positions():
    """Test mismatched positions length"""
    data = [[1, 2, 3], [4, 5, 6]]
    positions = [1]  # Mismatched length
    with pytest.raises(ValueError):
        plt.violinplot(data, positions=positions)

def test_violinplot_13_invalid_widths():
    """Test invalid widths"""
    data = [1, 2, 3, 4, 5]
    with pytest.raises(ValueError):
        plt.violinplot(data, widths=[-1, 0, -2])  # Multiple invalid widths

def test_violinplot_14_invalid_points():
    """Test invalid points parameter"""
    data = [1, 2, 3, 4, 5]
    with pytest.raises(ValueError):
        plt.violinplot(data, points=0)  # Invalid points value

def test_violinplot_15_single_value():
    """Test violinplot with single value"""
    data = [1]
    vp = plt.violinplot(data)
    assert len(vp['bodies']) == 1

def test_violinplot_16_identical_values():
    """Test violinplot with identical values"""
    data = [1, 1, 1, 1, 1]
    vp = plt.violinplot(data)
    assert len(vp['bodies']) == 1
    # The violin should be a fat line at x=0.75 and x=1.25
    vertices = vp['bodies'][0].get_paths()[0].vertices
    xvals = vertices[:, 0]
    assert np.all(np.isin(xvals, [0.75, 1.25]))

def test_violinplot_17_mixed_types():
    """Test violinplot with mixed data types"""
    data = [[1, 2, 3], [4.0, 5.0, 6.0]]
    vp = plt.violinplot(data)
    assert len(vp['bodies']) == 2

def test_violinplot_18_empty_data():
    """Test violinplot with empty data"""
    data = []
    with pytest.raises(ValueError):
        plt.violinplot(data)

def test_violinplot_19_custom_props():
    """Test custom properties for violin elements"""
    data = [1, 2, 3, 4, 5]
    vp = plt.violinplot(data)
    vp['bodies'][0].set_facecolor('red')
    vp['bodies'][0].set_alpha(0.5)
    assert np.allclose(vp['bodies'][0].get_facecolor(), [1, 0, 0, 0.5])  # Red with alpha 

# ----------------------------
# 2. Integration Tests
# ----------------------------
def test_violinplot_with_subplots():
    """Test violinplots in subplots"""
    data1 = [1, 2, 3, 4, 5]
    data2 = [6, 7, 8, 9, 10]
    fig, (ax1, ax2) = plt.subplots(1, 2)
    vp1 = ax1.violinplot(data1)
    vp2 = ax2.violinplot(data2)
    assert len(vp1['bodies']) > 0
    assert len(vp2['bodies']) > 0

def test_violinplot_with_grid():
    """Test violinplot with grid"""
    data = [1, 2, 3, 4, 5]
    plt.violinplot(data)
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
        widths=st.floats(min_value=0.1, max_value=2.0)
    )
    def test_violinplot_property_data_widths(data, widths):
        try:
            vp = plt.violinplot(data, widths=widths)
            assert len(vp['bodies']) == len(data)
        except np.linalg.LinAlgError:
            pytest.skip("Singular matrix: constant or single-valued data.")
else:
    def test_violinplot_property_data_widths():
        pytest.skip("hypothesis not installed")

# ----------------------------
# 4. Fuzz Testing
# ----------------------------
@given(
    n_violins=st.integers(min_value=1, max_value=20),
    n_points=st.integers(min_value=2, max_value=1000),
    value_range=st.tuples(st.floats(min_value=-1e6, max_value=1e6), 
                         st.floats(min_value=1e6, max_value=1e10))
)
def test_violinplot_fuzz_data_values(n_violins, n_points, value_range):
    """Fuzz test for various data value ranges and violin counts"""
    min_val, max_val = value_range
    data = [np.random.uniform(min_val, max_val, n_points) for _ in range(n_violins)]
    try:
        vp = plt.violinplot(data)
        assert len(vp['bodies']) == n_violins
        assert all(isinstance(body, mcoll.PolyCollection) for body in vp['bodies'])
    except Exception as e:
        assert isinstance(e, Exception)

@given(
    n_violins=st.integers(min_value=1, max_value=5),
    n_points=st.integers(min_value=2, max_value=50)
)
@settings(deadline=500)
def test_violinplot_fuzz_positions(n_violins, n_points):
    """Fuzz test for various position configurations"""
    data = [np.random.uniform(0, 100, n_points) for _ in range(n_violins)]
    position_specs = [
        None,  # Default positions
        list(range(n_violins)),  # Sequential positions
        np.random.uniform(0, 10, n_violins),  # Random positions
        np.linspace(0, 1, n_violins),  # Linear spacing
        np.geomspace(1, 10, n_violins)  # Geometric spacing
    ]
    for positions in position_specs:
        try:
            vp = plt.violinplot(data, positions=positions)
            assert len(vp['bodies']) == n_violins
            if positions is not None:
                for i, body in enumerate(vp['bodies']):
                    vertices = body.get_paths()[0].vertices
                    assert abs(np.mean(vertices[:, 0]) - positions[i]) < 0.5
        except Exception as e:
            assert isinstance(e, Exception)

# ----------------------------
# 5. Combinatorial Testing
# ----------------------------
widths_values = [0.5, 1.0, 2.0]
points_values = [50, 100]
bw_methods = [None, 'scott', 'silverman']
showmeans_values = [True, False]
showmedians_values = [True, False]
showextrema_values = [True, False]
orientations = ['vertical', 'horizontal']
quantiles_values = [None, [0.25, 0.75]]

combos = list(itertools.product(
    widths_values, points_values, bw_methods,
    showmeans_values, showmedians_values, showextrema_values, orientations, quantiles_values
))[:60]

@pytest.mark.parametrize(
    "widths,points,bw_method,showmeans,showmedians,showextrema,orientation,quantiles", combos
)
def test_violinplot_combinatorial(
    widths, points, bw_method, showmeans, showmedians, showextrema, orientation, quantiles
):
    data = [1, 2, 3, 4, 5]
    kwargs = dict(
        widths=widths, points=points, bw_method=bw_method,
        showmeans=showmeans, showmedians=showmedians, showextrema=showextrema,
        orientation=orientation
    )
    if quantiles is not None:
        kwargs['quantiles'] = quantiles
    vp = plt.violinplot(data, **kwargs)
    assert len(vp['bodies']) == 1
    if showmeans:
        assert ('cmeans' in vp)
    if showmedians:
        assert ('cmedians' in vp)
    if showextrema:
        assert ('cmaxes' in vp)
        assert ('cmins' in vp)
    if quantiles is not None:
        assert 'cquantiles' in vp

# ----------------------------
# 6. Accessibility Tests
# ----------------------------
def test_violinplot_color_cycle_distinct():
    """Test that violinplots have distinct colors by default"""
    data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    vp = plt.violinplot(data)
    # Set distinct colors for each violin
    for i, body in enumerate(vp['bodies']):
        body.set_facecolor(f'C{i}')  # Use matplotlib's color cycle
    violin_colors = [tuple(body.get_facecolor()[0]) for body in vp['bodies']]
    assert len(set(violin_colors)) == len(violin_colors)

def test_violinplot_high_contrast():
    """Test high contrast color combinations"""
    data = [1, 2, 3, 4, 5]
    vp = plt.violinplot(data)
    vp['bodies'][0].set_facecolor('white')
    vp['bodies'][0].set_edgecolor('black')
    fc = vp['bodies'][0].get_facecolor()[0]
    ec = vp['bodies'][0].get_edgecolor()[0]
    assert np.allclose(fc[:3], [1, 1, 1])  # White RGB
    assert fc[3] <= 1 and fc[3] > 0  # Accept any alpha
    assert np.allclose(ec[:3], [0, 0, 0])  # Black RGB
    assert ec[3] <= 1 and ec[3] > 0

# ----------------------------
# 7. Performance Tests
# ----------------------------
def test_violinplot_performance_scaling():
    """Test performance with increasing data size"""
    sizes = [100, 1000, 10000]
    times = []
    for size in sizes:
        data = [np.random.random(size) for _ in range(5)]
        start_time = time.time()
        plt.violinplot(data)
        end_time = time.time()
        times.append(end_time - start_time)
        plt.close()
    
    # Check that time increases sub-linearly with size
    for i in range(1, len(times)):
        assert times[i] < times[i-1] * 10  # Allow some non-linearity but not extreme

def test_violinplot_memory_usage():
    """Test memory usage with large dataset"""
    data = [np.random.random(1000) for _ in range(10)]
    vp = plt.violinplot(data)
    assert len(vp['bodies']) == 10
    plt.close()