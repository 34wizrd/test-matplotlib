import matplotlib
matplotlib.use('Agg')  # Use headless backend for testing

import matplotlib.pyplot as plt
import numpy as np
import math
from hypothesis import given, settings, strategies as st
import pytest

@given(st.lists(st.floats(min_value=-1e6, max_value=1e6), min_size=10, max_size=100))
@settings(max_examples=100, deadline=None)
def test_line_plot(y_vals):
    x_vals = list(range(len(y_vals)))
    fig, ax = plt.subplots()
    ax.plot(x_vals, y_vals)

    # Check that a line was added
    assert len(ax.lines) == 1

    # Check that the line has the expected number of points
    data = ax.lines[0].get_xydata()
    assert len(data) == len(y_vals)

    plt.close(fig)

def test_line_plot_styling():
    """Test line plot with various styling options."""
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    
    fig, ax = plt.subplots()
    line = ax.plot(x, y, 'r--', linewidth=2.5)[0]
    
    # Check styling was applied correctly
    assert line.get_color() == 'r'
    assert line.get_linestyle() == '--'
    assert line.get_linewidth() == 2.5
    
    plt.close(fig)

def test_multiple_lines():
    """Test plotting multiple lines on the same axes."""
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    y3 = np.sin(x) * np.cos(x)
    
    fig, ax = plt.subplots()
    ax.plot(x, y1, 'r-')
    ax.plot(x, y2, 'g--')
    ax.plot(x, y3, 'b:')
    
    # Check that three lines were added
    assert len(ax.lines) == 3
    
    # Check that each line has the expected color and style
    assert ax.lines[0].get_color() == 'r'
    assert ax.lines[0].get_linestyle() == '-'
    
    assert ax.lines[1].get_color() == 'g'
    assert ax.lines[1].get_linestyle() == '--'
    
    assert ax.lines[2].get_color() == 'b'
    assert ax.lines[2].get_linestyle() == ':'
    
    plt.close(fig)

def test_line_with_markers():
    """Test line plot with various marker styles."""
    x = np.arange(0, 10)
    y = x ** 2
    
    fig, ax = plt.subplots()
    line = ax.plot(x, y, 'bo-', markersize=8, markerfacecolor='white')[0]
    
    # Check marker properties
    assert line.get_marker() == 'o'
    assert line.get_markersize() == 8
    
    # Check that there are the right number of points
    assert len(line.get_xdata()) == len(x)
    assert len(line.get_ydata()) == len(y)
    
    plt.close(fig)

def test_line_plot_labels():
    """Test line plot with labels, title, and axes labels."""
    x = np.linspace(0, 10, 20)
    y = x ** 2
    
    fig, ax = plt.subplots()
    ax.plot(x, y, label='y = x²')
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_title('Quadratic Function')
    ax.legend()
    
    # Check labels
    assert ax.get_xlabel() == 'X axis'
    assert ax.get_ylabel() == 'Y axis'
    assert ax.get_title() == 'Quadratic Function'
    
    # Check legend
    assert len(ax.get_legend().get_texts()) == 1
    assert ax.get_legend().get_texts()[0].get_text() == 'y = x²'
    
    plt.close(fig)

def test_line_plot_with_nan_values():
    """Test line plot with NaN values."""
    x = np.arange(10)
    y = np.array([1, 2, np.nan, 4, 5, 6, np.nan, 8, 9, 10])
    
    fig, ax = plt.subplots()
    line = ax.plot(x, y)[0]
    
    # Matplotlib automatically handles NaN values by breaking the line
    # Check that the line was created
    assert len(ax.lines) == 1
    
    # Get the data that was actually plotted (will have breaks for NaN values)
    xdata = line.get_xdata()
    ydata = line.get_ydata()
    
    # Check that some data was plotted
    assert len(xdata) > 0
    assert len(ydata) > 0
    
    plt.close(fig)

def test_line_plot_with_inf_values():
    """Test line plot with Inf values."""
    x = np.arange(10)
    y = np.array([1, 2, np.inf, 4, 5, 6, -np.inf, 8, 9, 10])
    
    fig, ax = plt.subplots()
    
    # This should not cause an error, matplotlib will clip the values
    line = ax.plot(x, y)[0]
    assert len(ax.lines) == 1
    
    plt.close(fig)

@pytest.mark.parametrize('scale', ['linear', 'log', 'symlog', 'logit'])
def test_line_plot_scales(scale):
    """Test line plot with different axis scales."""
    # For log scales we need positive values
    x = np.linspace(0.1, 10, 100)
    if scale == 'logit':
        y = np.linspace(0.1, 0.9, 100)  # For logit, values must be between 0 and 1
    else:
        y = x ** 2
    
    fig, ax = plt.subplots()
    
    # Set scale without expecting warnings
    ax.set_yscale(scale)
    line = ax.plot(x, y)[0]
    
    # Check that the scale was set
    assert ax.get_yscale() == scale
    assert len(ax.lines) == 1
    
    plt.close(fig)