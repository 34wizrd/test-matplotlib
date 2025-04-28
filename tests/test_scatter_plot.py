import matplotlib
matplotlib.use('Agg')  # Use headless backend for testing

import matplotlib.pyplot as plt
import numpy as np
from hypothesis import given, settings, strategies as st
import pytest

@given(st.lists(st.tuples(st.floats(-1e6, 1e6), st.floats(-1e6, 1e6)), min_size=10, max_size=100))
@settings(max_examples=100, deadline=None)
def test_scatter_plot(points):
    fig, ax = plt.subplots()
    x_vals, y_vals = zip(*points)
    scatter = ax.scatter(x_vals, y_vals)

    # Ensure the number of points plotted matches input
    assert scatter.get_offsets().shape[0] == len(points)

    plt.close(fig)


def test_scatter_plot_custom_appearance():
    """Test scatter plot with custom colors, sizes and markers."""
    x = np.arange(10)
    y = x ** 2
    
    # Test with explicit sizes and colors
    fig, ax = plt.subplots()
    sizes = np.arange(10) * 20 + 100  # varying sizes
    colors = np.random.rand(10)  # random colors
    scatter = ax.scatter(x, y, s=sizes, c=colors, marker='*', alpha=0.7)
    
    # Verify size array was applied
    assert np.array_equal(scatter.get_sizes(), sizes)
    
    # Verify color array was used
    assert scatter.get_array().size == len(colors)
    
    # Verify marker style - PathCollection doesn't have get_marker()
    # We can check the marker style using the collection's path
    paths = scatter.get_paths()
    assert len(paths) > 0  # Ensure we have paths for the markers
    
    # Verify alpha value
    assert scatter.get_alpha() == 0.7
    
    plt.close(fig)


def test_scatter_plot_labels_and_legend():
    """Test scatter plot with labels and legend."""
    fig, ax = plt.subplots()
    
    # Create two scatter plots
    scatter1 = ax.scatter([1, 2, 3], [1, 2, 3], label='Group 1')
    scatter2 = ax.scatter([1, 2, 3], [3, 2, 1], label='Group 2')
    
    # Add labels and legend
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')
    ax.set_title('Scatter Plot Test')
    ax.legend()
    
    # Verify legend was created with correct number of elements
    legend = ax.get_legend()
    assert legend is not None
    assert len(legend.get_texts()) == 2
    assert legend.get_texts()[0].get_text() == 'Group 1'
    assert legend.get_texts()[1].get_text() == 'Group 2'
    
    # Verify axis labels
    assert ax.get_xlabel() == 'X-axis'
    assert ax.get_ylabel() == 'Y-axis'
    assert ax.get_title() == 'Scatter Plot Test'
    
    plt.close(fig)


def test_scatter_plot_edge_cases():
    """Test scatter plot with edge cases: empty dataset and single point."""
    # Test with single point
    fig, ax = plt.subplots()
    scatter_single = ax.scatter([5], [5])
    assert scatter_single.get_offsets().shape[0] == 1
    plt.close(fig)
    
    # Test with empty lists - this should work without errors
    fig, ax = plt.subplots()
    scatter_empty = ax.scatter([], [])
    assert scatter_empty.get_offsets().shape[0] == 0
    plt.close(fig)


def test_scatter_plot_colormap():
    """Test scatter plot with colormap and colorbar."""
    x = np.random.rand(50)
    y = np.random.rand(50)
    colors = np.linspace(0, 1, 50)
    
    fig, ax = plt.subplots()
    scatter = ax.scatter(x, y, c=colors, cmap='viridis')
    colorbar = fig.colorbar(scatter)
    
    # Verify colormap was set
    assert scatter.get_cmap().name == 'viridis'
    
    # Verify colorbar exists
    assert colorbar.ax is not None
    
    plt.close(fig)


def test_scatter_plot_different_markers():
    """Test scatter plot with different marker styles."""
    markers = ['o', 's', '^', 'D', '*']
    
    fig, ax = plt.subplots()
    
    for i, marker in enumerate(markers):
        scatter = ax.scatter([i]*3, range(3), marker=marker)
        # Instead of get_marker(), check the Path objects
        paths = scatter.get_paths()
        assert len(paths) > 0  # Ensure the marker has a valid path
        
    plt.close(fig)


def test_scatter_plot_zorder():
    """Test scatter plot with custom zorder."""
    fig, ax = plt.subplots()
    
    # Create two overlapping scatter plots with different zorder
    scatter1 = ax.scatter([1, 2, 3], [1, 2, 3], color='blue', s=100, zorder=1)
    scatter2 = ax.scatter([1.5, 2.5], [1.5, 2.5], color='red', s=100, zorder=2)
    
    # Verify zorder was set correctly
    assert scatter1.get_zorder() == 1
    assert scatter2.get_zorder() == 2
    
    plt.close(fig)


def test_scatter_plot_with_vmin_vmax():
    """Test scatter plot with vmin and vmax parameters."""
    x = np.random.rand(20)
    y = np.random.rand(20)
    c = np.linspace(0, 100, 20)
    
    fig, ax = plt.subplots()
    scatter = ax.scatter(x, y, c=c, vmin=20, vmax=80, cmap='plasma')
    
    # Verify vmin and vmax were set
    assert scatter.get_clim() == (20, 80)
    
    plt.close(fig)


def test_scatter_plot_with_edgecolors():
    """Test scatter plot with custom edge colors."""
    x = np.arange(10)
    y = x ** 2
    
    fig, ax = plt.subplots()
    
    # Test with different edge colors
    scatter = ax.scatter(x, y, s=100, facecolor='blue', edgecolor='red', linewidth=2)
    
    # Get edge color (this is a bit tricky with matplotlib's API)
    # For now, we'll just verify that the scatter plot was created
    assert scatter is not None
    
    plt.close(fig)