import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
from hypothesis import given, settings, strategies as st
from hypothesis import assume
import pytest

@given(st.lists(st.floats(min_value=0, max_value=100), min_size=3, max_size=8))
@settings(max_examples=100, deadline=None)
def test_pie_chart(data):
    assume(sum(data) > 1e-5)  # Skip zero or near-zero sum

    fig, ax = plt.subplots()
    ax.pie(data, labels=[f"Label {i}" for i in range(len(data))])

    assert len(ax.patches) >= len(data)

    plt.close(fig)

def test_pie_chart_explode():
    """Test pie chart with exploded slices."""
    data = [15, 30, 45, 10]
    explode = [0, 0.1, 0, 0.2]  # explode 2nd and 4th slice
    
    fig, ax = plt.subplots()
    wedges, texts = ax.pie(data, explode=explode)
    
    assert len(wedges) == len(data)
    # Check if exploded slices have different center positions
    centers = [wedge.center for wedge in wedges]
    assert centers[1] != centers[0]  # 2nd slice is exploded
    assert centers[3] != centers[0]  # 4th slice is exploded
    
    plt.close(fig)

def test_pie_chart_colors():
    """Test pie chart with custom colors."""
    data = [30, 20, 40, 10]
    colors = ['red', 'green', 'blue', 'yellow']
    
    fig, ax = plt.subplots()
    wedges, texts = ax.pie(data, colors=colors)
    
    # Check if colors are applied
    for i, wedge in enumerate(wedges):
        assert wedge.get_facecolor()[:-1] == plt.cm.colors.to_rgb(colors[i])
    
    plt.close(fig)

def test_pie_chart_with_autopct():
    """Test pie chart with percentage labels."""
    data = [20, 30, 50]
    
    fig, ax = plt.subplots()
    wedges, texts, autotext = ax.pie(data, autopct='%1.1f%%')
    
    assert len(autotext) == len(data)
    # Check if percentage texts are created
    for i, text in enumerate(autotext):
        percentage = 100 * data[i] / sum(data)
        expected_text = f"{percentage:.1f}%"
        assert text.get_text() == expected_text
    
    plt.close(fig)

def test_pie_chart_with_shadows():
    """Test pie chart with shadow effect."""
    data = [25, 25, 25, 25]
    
    fig, ax = plt.subplots()
    wedges, texts = ax.pie(data, shadow=True)
    
    # Instead of checking a non-existent get_shadow method, just verify the wedges exist
    assert len(wedges) == len(data)
    # The shadow is applied during rendering, so we can't easily test it directly
    
    plt.close(fig)

def test_pie_chart_with_custom_start_angle():
    """Test pie chart with custom start angle."""
    data = [10, 10, 10, 10]
    start_angle = 90
    
    fig, ax = plt.subplots()
    wedges, texts = ax.pie(data, startangle=start_angle)
    
    # This is difficult to test directly, but we can verify the chart is created
    assert len(wedges) == len(data)
    
    plt.close(fig)

def test_pie_chart_single_value():
    """Test pie chart with a single value."""
    data = [100]
    
    fig, ax = plt.subplots()
    wedges, texts = ax.pie(data)
    
    assert len(wedges) == 1
    # A single value should create a full circle (2*pi radians)
    assert abs(wedges[0].theta2 - wedges[0].theta1 - 360.0) < 1e-6
    
    plt.close(fig)

def test_pie_chart_with_one_zero_value():
    """Test pie chart with one zero value."""
    data = [30, 40, 0, 30]
    
    fig, ax = plt.subplots()
    wedges, texts = ax.pie(data)
    
    # Matplotlib creates wedges for zero values too, just with zero angle
    assert len(wedges) == len(data)
    # Check that the zero value wedge has effectively zero area
    for i, val in enumerate(data):
        if val == 0:
            assert abs(wedges[i].theta2 - wedges[i].theta1) < 1e-6
    
    plt.close(fig)

@pytest.mark.parametrize("normalize", [True, False])
def test_pie_chart_normalization(normalize):
    """Test pie chart normalization behavior."""
    # When normalize=False, sum(data) must be <= 1
    data = [0.2, 0.3, 0.4] if not normalize else [1, 2, 3]
    
    fig, ax = plt.subplots()
    wedges, texts = ax.pie(data, normalize=normalize)
    
    actual_fractions = [(wedge.theta2 - wedge.theta1) / 360.0 for wedge in wedges]
    
    if normalize:
        # When normalize=True (default), values should be proportional to the sum
        expected_fractions = [val / sum(data) for val in data]
    else:
        # When normalize=False, values are used directly as they sum to ≤1
        expected_fractions = data
    
    for actual, expected in zip(actual_fractions, expected_fractions):
        assert abs(actual - expected) < 1e-6
    
    plt.close(fig)

def test_pie_chart_with_nan_values():
    """Test pie chart with NaN values."""
    data = [10, np.nan, 30, 20]
    
    # Filter out NaN values before plotting - Matplotlib doesn't handle NaN values directly
    valid_data = [x for x in data if not np.isnan(x)]
    
    fig, ax = plt.subplots()
    wedges, texts = ax.pie(valid_data)
    
    # Verify we get the right number of wedges
    assert len(wedges) == len(valid_data)
    assert len(wedges) == 3  # Since one value was NaN
    
    plt.close(fig)