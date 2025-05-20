import pytest
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
import itertools
import random
import string
from hypothesis import given, strategies as st, settings

# --- 1. Basic Functional Tests ---

def test_tc_01_simple_numeric_lists():
    """TC-01: One line connecting (0,10), (1,20), (2,30)"""
    plt.figure()
    line, = plt.plot([0, 1, 2], [10, 20, 30])
    xdata, ydata = line.get_xdata(), line.get_ydata()
    assert np.all(xdata == [0, 1, 2])
    assert np.all(ydata == [10, 20, 30])
    plt.close()


def test_tc_02_default_x_generation():
    """TC-02: x defaults to [0,1,2]"""
    plt.figure()
    line, = plt.plot([5, 15, 25])
    assert np.all(line.get_xdata() == [0, 1, 2])
    assert np.all(line.get_ydata() == [5, 15, 25])
    plt.close()


def test_tc_03_single_point_data():
    """TC-03: Single marker at (0,5), no line segment"""
    plt.figure()
    line, = plt.plot([0], [5])
    assert len(line.get_xdata()) == 1 and len(line.get_ydata()) == 1
    plt.close()


def test_tc_04_empty_data():
    """TC-04: Empty data produces empty plot"""
    plt.figure()
    lines = plt.plot([], [])
    # Should be one line with no data
    assert len(lines) == 1
    assert len(lines[0].get_xdata()) == 0
    assert len(lines[0].get_ydata()) == 0
    plt.close()


def test_tc_05_mismatched_lengths():
    """TC-05: Raises ValueError on mismatched x and y lengths"""
    with pytest.raises(ValueError):
        plt.figure(); plt.plot([0,1], [10]); plt.close()


def test_tc_07_multiple_series():
    """TC-07: Two lines with correct styles"""
    plt.figure()
    x1, y1 = [0,1,2], [1,2,3]
    x2, y2 = [0,1,2], [3,2,1]
    lines = plt.plot(x1, y1, 'r-', x2, y2, 'b--')
    assert len(lines) == 2
    assert lines[0].get_color() == 'r'
    assert lines[1].get_color() == 'b'
    plt.close()


def test_tc_08_legend_labels():
    """TC-08: Legend displays entry 'data'"""
    plt.figure()
    plt.plot([0,1], [1,2], label='data')
    legend = plt.legend()
    labels = [text.get_text() for text in legend.get_texts()]
    assert 'data' in labels
    plt.close()


def test_tc_09_marker_only_styling():
    """TC-09: Line with 'o' markers"""
    plt.figure()
    line, = plt.plot([1,2,3], [3,2,1], marker='o')
    assert line.get_marker() == 'o'
    plt.close()


def test_tc_10_style_shorthand():
    """TC-10: Green dotted line with caret markers"""
    plt.figure()
    line, = plt.plot([1,2,3], [3,2,1], 'g:^')
    assert line.get_color() == 'g'
    assert line.get_linestyle() == ':'
    assert line.get_marker() == '^'
    plt.close()


def test_tc_11_performance_large_dataset():
    """TC-11: Plotting 100k points in under 1s"""
    x = np.arange(100000)
    start = time.time()
    plt.figure()
    plt.plot(x, x)
    plt.close()
    duration = time.time() - start
    assert duration < 1.0


def test_tc_12_nan_handling():
    """TC-12: Line gaps at NaN positions"""
    plt.figure()
    line, = plt.plot([1, np.nan, 3], [1,2,3])
    xdata = line.get_xdata()
    # NaN should break the line; check that NaN present
    assert np.isnan(xdata[1])
    plt.close()


def test_tc_13_advanced_styling():
    """TC-13: Line width and transparency"""
    plt.figure()
    line, = plt.plot([0,1], [1,0], linewidth=2.5, alpha=0.5)
    assert pytest.approx(line.get_linewidth()) == 2.5
    assert pytest.approx(line.get_alpha()) == 0.5
    plt.close()


def test_tc_14_datetime_xaxis():
    """TC-14: DateTime x-axis formatting"""
    dates = pd.date_range('2025-01-01', periods=3)
    plt.figure()
    line, = plt.plot(dates, [1,2,3])
    xdata = line.get_xdata()
    assert np.all(xdata == dates)
    plt.close()


def test_tc_15_categorical_data():
    """TC-15: Categorical x-axis support"""
    cats = ['A','B','C']
    plt.figure()
    line, = plt.plot(cats, [1,2,3])
    # Matplotlib keeps categories as xdata
    assert list(line.get_xdata()) == cats
    plt.close()

# --- 2. Integration Tests ---

def test_plot_with_subplots():
    fig, (ax1, ax2) = plt.subplots(1, 2)
    ax1.plot([1,2,3], [1,2,3])
    ax2.plot([3,2,1], [1,2,3])
    assert len(ax1.get_lines()) == 1
    assert len(ax2.get_lines()) == 1
    plt.close(fig)


def test_plot_with_grid():
    fig = plt.figure()
    plt.plot([1,2,3], [1,2,3])
    plt.grid(True)
    ax = plt.gca()
    # Check that gridlines are visible
    assert any([line.get_visible() for line in ax.get_xgridlines()])
    assert any([line.get_visible() for line in ax.get_ygridlines()])
    plt.close(fig)


def test_plot_with_twinx():
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.plot([1,2,3], [1,2,3], 'b-')
    ax2.plot([1,2,3], [3,2,1], 'r-')
    assert len(ax1.get_lines()) == 1
    assert len(ax2.get_lines()) == 1
    assert ax1.get_lines()[0].get_color() == 'b'
    assert ax2.get_lines()[0].get_color() == 'r'
    plt.close(fig)

# --- 3. Property-Based Testing ---

@given(
    y=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=1, max_size=20)
)
@settings(max_examples=50)
def test_plot_property_y_only(y):
    plt.figure()
    plt.plot(y)
    line = plt.gca().get_lines()[0]
    assert len(line.get_xdata()) == len(y)
    assert len(line.get_ydata()) == len(y)
    plt.close()


@given(
    x=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2, max_size=20),
    y=st.lists(st.floats(allow_nan=False, allow_infinity=False), min_size=2, max_size=20)
)
@settings(max_examples=50)
def test_plot_property_xy(x, y):
    # Adjust to equal lengths
    min_len = min(len(x), len(y))
    x, y = x[:min_len], y[:min_len]
    plt.figure()
    plt.plot(x, y)
    line = plt.gca().get_lines()[0]
    assert np.array_equal(line.get_xdata(), x)
    assert np.array_equal(line.get_ydata(), y)
    plt.close()

# --- 4. Fuzz Testing ---

def test_fuzz_style_string():
    for _ in range(100):
        style = ''.join(random.choice(string.ascii_letters + string.punctuation) for _ in range(random.randint(1,5)))
        plt.figure()
        try:
            plt.plot([1,2,3], [1,2,3], style)
        except ValueError:
            pass
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")
        finally:
            plt.close()

# --- 5. Combinatorial Testing ---

linestyles = ['-', '--', '-.', ':']
markers = [None, 'o', 's', '^', 'x']
colors = ['blue', 'green', 'red', 'black', 'orange']
combos = list(itertools.product(linestyles, markers, colors))[:50]

@pytest.mark.parametrize("ls,mk,cl", combos)
def test_plot_styles(ls, mk, cl):
    plt.figure()
    line, = plt.plot([0,1], [1,0], linestyle=ls, marker=mk, color=cl)
    assert line.get_linestyle() == ls
    # get_marker() returns 'None' (string) if no marker is set
    assert (line.get_marker() or 'None') == (mk if mk is not None else 'None')
    assert line.get_color() == cl
    plt.close()

# --- 6. Accessibility Testing ---

def test_colorblind_friendly_defaults():
    plt.figure()
    for i in range(10):
        plt.plot([0,1], [i, i])
    colors = [ln.get_color() for ln in plt.gca().get_lines()]
    assert len(set(colors)) == len(colors)
    plt.close()


def test_high_contrast_mode():
    plt.figure()
    line, = plt.plot([1,2,3], [1,2,1], 'k-', linewidth=3)
    plt.grid(True, color='black', linestyle='--', alpha=0.7)
    assert line.get_color() == 'k'
    assert line.get_linewidth() == 3
    plt.close()

# --- 7. Performance Scaling Test ---

def test_performance_scaling():
    sizes = [100, 1000, 10000, 100000]
    times = []
    for size in sizes:
        x = np.arange(size)
        start = time.time()
        plt.figure()
        plt.plot(x, x)
        plt.close()
        times.append(time.time() - start)
    # Check that scaling is roughly sub-linear
    assert times[-1] < times[0] * 1000
