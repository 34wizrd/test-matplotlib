import matplotlib
matplotlib.use('Agg')  # Use headless backend for testing

import matplotlib.pyplot as plt
import pytest
import numpy as np
from hypothesis import given, settings, strategies as st
from hypothesis import assume

@given(st.lists(st.floats(min_value=0, max_value=100), min_size=10, max_size=100))
@settings(max_examples=100, deadline=None)
def test_histogram(data):
    # Ensure the data has a wide enough spread for 10 bins
    assume(max(data) - min(data) > 1e-3)

    fig, ax = plt.subplots()
    n, bins, patches = ax.hist(data, bins=10)

    assert len(patches) == 10

    plt.close(fig)

# Additional tests to cover different aspects of histograms

def test_histogram_bin_configurations():
    """Test histogram with different bin configurations."""
    data = np.random.randn(1000)
    
    # Test 1: Default bins (automatically determined)
    fig, ax = plt.subplots()
    n1, bins1, patches1 = ax.hist(data)
    assert len(patches1) > 0
    plt.close(fig)
    
    # Test 2: Integer number of bins
    fig, ax = plt.subplots()
    n2, bins2, patches2 = ax.hist(data, bins=5)
    assert len(patches2) == 5
    plt.close(fig)
    
    # Test 3: Array of bin edges
    bin_edges = [-3, -2, -1, 0, 1, 2, 3]
    fig, ax = plt.subplots()
    n3, bins3, patches3 = ax.hist(data, bins=bin_edges)
    assert len(patches3) == len(bin_edges) - 1
    assert np.array_equal(bins3, bin_edges)
    plt.close(fig)
    
    # Test 4: String bin options
    fig, ax = plt.subplots()
    n4, bins4, patches4 = ax.hist(data, bins='auto')
    assert len(patches4) > 0
    plt.close(fig)

def test_histogram_types():
    """Test different histogram types."""
    data = np.random.randn(1000)
    
    # Test 1: Default (bar)
    fig, ax = plt.subplots()
    n1, bins1, patches1 = ax.hist(data)
    assert len(patches1) > 0
    plt.close(fig)
    
    # Test 2: Step histogram
    fig, ax = plt.subplots()
    n2, bins2, patches2 = ax.hist(data, histtype='step')
    assert len(patches2) > 0
    plt.close(fig)
    
    # Test 3: Barstacked histogram (requires multiple datasets)
    fig, ax = plt.subplots()
    data1 = np.random.randn(500)
    data2 = np.random.randn(500) + 1  # Offset for visibility
    n3, bins3, patches3 = ax.hist([data1, data2], histtype='barstacked')
    assert len(patches3) == 2  # One patch list per dataset
    assert len(patches3[0]) > 0
    plt.close(fig)
    
    # Test 4: Stepfilled histogram
    fig, ax = plt.subplots()
    n4, bins4, patches4 = ax.hist(data, histtype='stepfilled')
    assert len(patches4) > 0
    plt.close(fig)

def test_histogram_normalization():
    """Test different histogram normalization methods."""
    data = np.random.randn(1000)
    
    # Test 1: Default (count)
    fig, ax = plt.subplots()
    n1, bins1, patches1 = ax.hist(data, bins=10)
    # Sum of counts should be total number of data points
    assert np.sum(n1) == len(data)
    plt.close(fig)
    
    # Test 2: Probability density
    fig, ax = plt.subplots()
    n2, bins2, patches2 = ax.hist(data, bins=10, density=True)
    # Integral of probability density should be approximately 1
    bin_widths = np.diff(bins2)
    assert np.isclose(np.sum(n2 * bin_widths), 1.0, atol=1e-10)
    plt.close(fig)

def test_histogram_orientation():
    """Test different histogram orientations."""
    data = np.random.randn(100)
    
    # Test 1: Default (vertical)
    fig, ax = plt.subplots()
    n1, bins1, patches1 = ax.hist(data)
    plt.close(fig)
    
    # Test 2: Horizontal
    fig, ax = plt.subplots()
    n2, bins2, patches2 = ax.hist(data, orientation='horizontal')
    plt.close(fig)

def test_histogram_cumulative():
    """Test cumulative histograms."""
    data = np.random.randn(1000)
    
    # Test 1: Non-cumulative (default)
    fig, ax = plt.subplots()
    n1, bins1, patches1 = ax.hist(data, bins=10)
    plt.close(fig)
    
    # Test 2: Cumulative
    fig, ax = plt.subplots()
    n2, bins2, patches2 = ax.hist(data, bins=10, cumulative=True)
    # Last bin in cumulative histogram should contain all data points
    assert np.isclose(n2[-1], len(data))
    plt.close(fig)

def test_histogram_multiple_datasets():
    """Test histograms with multiple datasets."""
    data1 = np.random.normal(0, 1, 1000)
    data2 = np.random.normal(3, 1, 1000)
    
    # Test 1: Multiple datasets (default stacked)
    fig, ax = plt.subplots()
    n1, bins1, patches1 = ax.hist([data1, data2], bins=10)
    # We should have 2 lists of patches for 2 datasets
    assert len(patches1) == 2
    assert len(patches1[0]) == 10
    assert len(patches1[1]) == 10
    plt.close(fig)
    
    # Test 2: Multiple datasets with overlay
    fig, ax = plt.subplots()
    n2, bins2, patches2 = ax.hist([data1, data2], bins=10, histtype='step')
    assert len(patches2) == 2
    assert len(patches2[0]) > 0
    plt.close(fig)

def test_histogram_edge_cases():
    """Test histogram with edge cases."""
    
    # Test 1: Empty data
    fig, ax = plt.subplots()
    n1, bins1, patches1 = ax.hist([])
    # For empty data, matplotlib still creates bins (default 10) but with zero counts
    assert len(n1) > 0
    assert np.sum(n1) == 0  # Sum of counts should be zero for empty data
    plt.close(fig)
    
    # Test 2: Single value
    fig, ax = plt.subplots()
    n2, bins2, patches2 = ax.hist([5])
    # Should create at least one bin
    assert len(patches2) > 0
    assert np.sum(n2) == 1  # Sum of counts should be 1 for single value
    plt.close(fig)
    
    # Test 3: All identical values
    fig, ax = plt.subplots()
    n3, bins3, patches3 = ax.hist([7, 7, 7, 7, 7], bins=10)
    # All values should be in one bin
    non_zero_bins = np.count_nonzero(n3)
    assert non_zero_bins == 1
    assert np.sum(n3) == 5  # Sum of counts should be 5 for five identical values
    plt.close(fig)

def test_histogram_return_values():
    """Test histogram return values."""
    data = np.random.randn(1000)
    
    fig, ax = plt.subplots()
    n, bins, patches = ax.hist(data, bins=10)
    
    # Test 1: n should have the count of elements in each bin
    assert len(n) == 10
    assert np.sum(n) == len(data)
    
    # Test 2: bins should have 11 edges for 10 bins
    assert len(bins) == 11
    
    # Test 3: patches should have 10 elements for 10 bins
    assert len(patches) == 10
    
    plt.close(fig)

def test_histogram_aesthetics():
    """Test histogram aesthetic properties."""
    data = np.random.randn(1000)
    
    # Test 1: Color specification
    fig, ax = plt.subplots()
    n1, bins1, patches1 = ax.hist(data, color='red')
    # All patches should have the specified color
    assert patches1[0].get_facecolor()[0:3] == (1, 0, 0)  # RGB for red
    plt.close(fig)
    
    # Test 2: Alpha transparency
    fig, ax = plt.subplots()
    n2, bins2, patches2 = ax.hist(data, alpha=0.5)
    # All patches should have the specified alpha
    assert patches2[0].get_facecolor()[3] == 0.5  # Alpha value
    plt.close(fig)
    
    # Test 3: Edge color
    fig, ax = plt.subplots()
    n3, bins3, patches3 = ax.hist(data, edgecolor='black')
    # Edge color should be black
    assert patches3[0].get_edgecolor()[0:3] == (0, 0, 0)  # RGB for black
    plt.close(fig)


# =========================================================== test session starts ============================================================
# platform win32 -- Python 3.13.2, pytest-8.3.5, pluggy-1.5.0 -- C:\Github\Git_34wizrd\matplotlib-testing\env\Scripts\python.exe
# cachedir: .pytest_cache
# hypothesis profile 'default' -> database=DirectoryBasedExampleDatabase(WindowsPath('C:/Github/Git_34wizrd/matplotlib-testing/.hypothesis/examples'))
# Matplotlib: 3.10.1
# Freetype: 2.6.1
# rootdir: C:\Github\Git_34wizrd\matplotlib-testing
# plugins: hypothesis-6.130.8, cov-6.1.1, mpl-0.17.0
# collected 10 items

# tests/test_histogram.py::test_histogram PASSED                                                                                        [ 10%]
# tests/test_histogram.py::test_histogram_bin_configurations PASSED                                                                     [ 20%]
# tests/test_histogram.py::test_histogram_types PASSED                                                                                  [ 30%]
# tests/test_histogram.py::test_histogram_normalization PASSED                                                                          [ 40%]
# tests/test_histogram.py::test_histogram_orientation PASSED                                                                            [ 50%]
# tests/test_histogram.py::test_histogram_cumulative PASSED                                                                             [ 60%]
# tests/test_histogram.py::test_histogram_multiple_datasets PASSED                                                                      [ 70%]
# tests/test_histogram.py::test_histogram_edge_cases PASSED                                                                             [ 80%]
# tests/test_histogram.py::test_histogram_return_values PASSED                                                                          [ 90%]
# tests/test_histogram.py::test_histogram_aesthetics PASSED                                                                             [100%]

# ============================================================ 10 passed in 2.66s ============================================================ 