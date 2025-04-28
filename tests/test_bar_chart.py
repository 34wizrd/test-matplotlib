import matplotlib
matplotlib.use('Agg')  # Use headless backend for testing

import matplotlib.pyplot as plt
import numpy as np
import pytest
from hypothesis import given, settings, strategies as st

@given(st.lists(st.floats(min_value=0, max_value=100), min_size=10, max_size=100))
@settings(max_examples=100, deadline=None)
def test_bar_chart(values):
    x_vals = list(range(len(values)))
    fig, ax = plt.subplots()
    ax.bar(x_vals, values)

    # Assert that one bar was drawn for each input
    assert len(ax.patches) == len(values)

    plt.close(fig)


# Special cases tests

def test_empty_bar_chart():
    """Test that bar chart handles empty data gracefully"""
    fig, ax = plt.subplots()
    # This should not raise an error, just create an empty plot
    ax.bar([], [])
    plt.close(fig)


def test_negative_values():
    """Test bar chart with negative values"""
    values = [-5, -2, 0, 3, 7]
    x_vals = range(len(values))
    fig, ax = plt.subplots()
    bars = ax.bar(x_vals, values)
    
    # Verify bars with negative values are drawn below x-axis
    for i, value in enumerate(values):
        if value < 0:
            assert bars[i].get_height() < 0
        else:
            assert bars[i].get_height() >= 0
            
    plt.close(fig)


def test_nan_inf_values():
    """Test bar chart with NaN and Inf values"""
    values = [1, 2, np.nan, 4, np.inf, -np.inf, 7]
    x_vals = range(len(values))
    fig, ax = plt.subplots()
    
    # This should not crash but will log warnings
    # NaN and Inf values are typically skipped in plotting
    bars = ax.bar(x_vals, values)
    
    # Check that bars exist for all values, including NaN and Inf
    assert len(bars) == len(values)
    
    # For validating the test, just check that non-NaN, non-Inf values have proper heights
    for i, val in enumerate(values):
        if not np.isnan(val) and not np.isinf(val):
            assert bars[i].get_height() == val
    
    plt.close(fig)


def test_extreme_values():
    """Test bar chart with very small and very large values"""
    small_val = 1e-10
    large_val = 1e10
    values = [small_val, 1, 10, large_val]
    x_vals = range(len(values))
    
    fig, ax = plt.subplots()
    ax.bar(x_vals, values)
    
    # Test should complete without errors
    plt.close(fig)


def test_stacked_bars():
    """Test stacked bar chart"""
    data1 = [1, 2, 3, 4, 5]
    data2 = [2, 3, 1, 2, 1]
    x_vals = range(len(data1))
    
    fig, ax = plt.subplots()
    ax.bar(x_vals, data1, label='Series 1')
    ax.bar(x_vals, data2, bottom=data1, label='Series 2')
    
    # We should have twice as many bars as x values (2 series)
    assert len(ax.patches) == 2 * len(x_vals)
    
    plt.close(fig)


def test_horizontal_bars():
    """Test horizontal bar chart orientation"""
    values = [1, 5, 3, 7, 2]
    y_vals = range(len(values))
    
    fig, ax = plt.subplots()
    bars = ax.barh(y_vals, values)
    
    # Check that bars are horizontal (width corresponds to value)
    for i, bar in enumerate(bars):
        assert bar.get_width() == values[i]
        
    plt.close(fig)


def test_bar_styling():
    """Test bar styling options"""
    values = [3, 7, 2, 5, 8]
    x_vals = range(len(values))
    colors = ['red', 'green', 'blue', 'yellow', 'purple']
    widths = [0.5, 0.7, 0.6, 0.8, 0.4]
    
    fig, ax = plt.subplots()
    bars = ax.bar(x_vals, values, color=colors, width=widths, edgecolor='black', linewidth=2)
    
    # Check that styling was applied
    for i, bar in enumerate(bars):
        assert bar.get_facecolor()[:-1] == plt.matplotlib.colors.to_rgb(colors[i])
        assert bar.get_width() == widths[i]
        
    plt.close(fig)


def test_bar_labels():
    """Test bar chart with labels"""
    values = [10, 20, 15, 25, 30]
    x_vals = range(len(values))
    labels = ['A', 'B', 'C', 'D', 'E']
    
    fig, ax = plt.subplots()
    ax.bar(x_vals, values)
    ax.set_xticks(x_vals)
    ax.set_xticklabels(labels)
    
    # Verify x tick labels match our provided labels
    assert [text.get_text() for text in ax.get_xticklabels()] == labels
    
    plt.close(fig)

# TEST CASES
# Empty data: Currently your test requires at least 10 values (min_size=10)
# Negative values: You're only testing values from 0 to 100
# NaN or Inf values: These can cause issues in matplotlib
# Very large values or very small values: Potential overflow/underflow issues
# Stacked bar charts: Testing multiple series on the same plot
# Different bar orientations: Horizontal bars vs. vertical bars
# Bar customization: Colors, widths, etc.
# Bar labels and annotations