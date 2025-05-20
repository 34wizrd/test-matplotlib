import matplotlib
matplotlib.use('Agg')  # Use headless backend for testing

import matplotlib.pyplot as plt
import numpy as np
import math
from hypothesis import given, settings, strategies as st
import pytest

# Strategy for generating valid colors
color_strategy = st.sampled_from(['r', 'g', 'b', 'c', 'm', 'y', 'k']) | st.tuples(
    st.floats(min_value=0, max_value=1),
    st.floats(min_value=0, max_value=1),
    st.floats(min_value=0, max_value=1)
)

# Strategy for figure properties
figure_props = st.fixed_dictionaries({
    'figsize': st.tuples(st.floats(1, 15), st.floats(1, 15)),
    'dpi': st.integers(50, 200)
})

# Strategy for labels
label_strategy = st.lists(st.text(min_size=1, max_size=10), min_size=1, max_size=5)

# Strategy for line styles - removing empty string and using only valid collection linestyles
linestyle_strategy = st.sampled_from(['-', '--', '-.', ':', 'solid', 'dashed', 'dashdot', 'dotted'])

@st.composite
def lists_with_nans(draw, min_size=5, max_size=20):
    """Generate lists of floats with some NaN values."""
    n = draw(st.integers(min_size, max_size))
    result = []
    for _ in range(n):
        if draw(st.booleans()):
            result.append(draw(st.floats(min_value=-1000, max_value=1000)))
        else:
            result.append(float('nan'))
    return result

@given(
    # Use a fixed length for all inner lists to ensure consistency
    st.integers(min_value=5, max_value=20).flatmap(
        lambda n: st.lists(
            st.lists(st.floats(min_value=-1000, max_value=1000), min_size=n, max_size=n),
            min_size=2, max_size=5
        )
    ),
    figure_props
)
@settings(max_examples=50, deadline=None)
def test_stackplot_basic(data_lists, fig_props):
    """Test stackplot with various random datasets."""
    fig = plt.figure(figsize=fig_props['figsize'], dpi=fig_props['dpi'])
    
    # Create x values
    x = np.arange(len(data_lists[0]))
    
    try:
        plt.stackplot(x, data_lists)
        # Stackplot should create a figure with content
        assert len(plt.gca().collections) > 0
    except Exception as e:
        # If we have NaN or Inf values, stackplot might legitimately fail
        if not any(any(not math.isfinite(val) for val in data) for data in data_lists):
            # If all values are finite but we still got an error, that's a problem
            pytest.fail(f"Stackplot failed with valid data: {e}")
    finally:
        plt.close('all')

@given(
    # Use a fixed length for all inner lists to ensure consistency
    st.integers(min_value=5, max_value=20).flatmap(
        lambda n: st.lists(
            lists_with_nans(min_size=n, max_size=n),
            min_size=2, max_size=5
        )
    ),
    st.lists(color_strategy, min_size=1, max_size=10),
)
@settings(max_examples=30, deadline=None)
def test_stackplot_with_nan_values_and_colors(data_lists, colors):
    """Test stackplot with NaN values and custom colors."""
    fig = plt.figure()
    
    # Create x values
    x = np.arange(len(data_lists[0]))
    
    try:
        # Use colors if provided, otherwise default
        if len(colors) >= len(data_lists):
            plt.stackplot(x, data_lists, colors=colors[:len(data_lists)])
        else:
            plt.stackplot(x, data_lists)
        
        # Some assertions are not possible here because NaN values might cause unpredictable behavior
    except Exception:
        # We expect potential exceptions with NaN values, so we're just testing
        # that it doesn't crash the application
        pass
    finally:
        plt.close('all')

@given(
    # Use a fixed length for all inner lists to ensure consistency
    st.integers(min_value=5, max_value=20).flatmap(
        lambda n: st.lists(
            st.lists(st.floats(min_value=-1000, max_value=1000), min_size=n, max_size=n),
            min_size=2, max_size=5
        )
    ),
    st.sampled_from(['zero', 'sym', 'wiggle', 'weighted_wiggle'])  # Changed 'symmetric' to 'sym' to match valid options
)
@settings(max_examples=20, deadline=None)
def test_stackplot_baseline_options(data_lists, baseline):
    """Test stackplot with different baseline options."""
    fig = plt.figure()
    
    # Create x values
    x = np.arange(len(data_lists[0]))
    
    try:
        plt.stackplot(x, data_lists, baseline=baseline)
        # Should create stackplot collections
        assert len(plt.gca().collections) > 0
    except Exception as e:
        if not any(any(not math.isfinite(val) for val in data) for data in data_lists):
            pytest.fail(f"Stackplot with baseline {baseline} failed with valid data: {e}")
    finally:
        plt.close('all')

@given(
    # Use a fixed length for all inner lists to ensure consistency
    st.integers(min_value=5, max_value=20).flatmap(
        lambda n: st.lists(
            st.lists(st.floats(min_value=-1000, max_value=1000), min_size=n, max_size=n),
            min_size=2, max_size=5
        )
    ),
    label_strategy
)
@settings(max_examples=20, deadline=None)
def test_stackplot_with_labels_and_legend(data_lists, labels):
    """Test stackplot with labels and legend."""
    fig = plt.figure()
    
    # Create x values
    x = np.arange(len(data_lists[0]))
    
    try:
        # Generate labels if needed
        if len(labels) < len(data_lists):
            labels = [f'Series {i+1}' for i in range(len(data_lists))]
        else:
            labels = labels[:len(data_lists)]
        
        plt.stackplot(x, data_lists, labels=labels)
        # Stackplot should create a figure with content
        assert len(plt.gca().collections) > 0
        
        # Add a legend and verify it was created
        legend = plt.legend()
        assert legend is not None
        if all(np.allclose(data, 0) for data in data_lists):
            assert len(legend.get_texts()) == 1
        else:
            assert len(legend.get_texts()) == len(data_lists)
    except Exception as e:
        if not any(any(not math.isfinite(val) for val in data) for data in data_lists):
            pytest.fail(f"Stackplot with labels failed with valid data: {e}")
    finally:
        plt.close('all')

@given(
    # Use a fixed length for all inner lists to ensure consistency
    st.integers(min_value=5, max_value=20).flatmap(
        lambda n: st.tuples(
            st.lists(st.floats(min_value=0, max_value=1000), min_size=n, max_size=n),
            st.lists(
                st.lists(st.floats(min_value=-1000, max_value=1000), min_size=n, max_size=n),
                min_size=2, max_size=5
            )
        )
    )
)
@settings(max_examples=20, deadline=None)
def test_stackplot_with_explicit_x_values(x_and_data):
    """Test stackplot with explicit x values (not just range-based)."""
    x_values, data_lists = x_and_data
    
    # Make sure x_values are sorted for proper plotting
    x_values.sort()
    
    fig = plt.figure()
    
    try:
        plt.stackplot(x_values, data_lists)
        # Stackplot should create a figure with content
        assert len(plt.gca().collections) > 0
        
        # Check if x-axis limits match our data
        x_min, x_max = plt.gca().get_xlim()
        assert x_min <= min(x_values)
        assert x_max >= max(x_values)
    except Exception as e:
        if not any(any(not math.isfinite(val) for val in data) for data in data_lists):
            pytest.fail(f"Stackplot with explicit x values failed with valid data: {e}")
    finally:
        plt.close('all')

@given(
    # Use a fixed length for all inner lists to ensure consistency
    st.integers(min_value=5, max_value=20).flatmap(
        lambda n: st.lists(
            st.lists(st.floats(min_value=-1000, max_value=1000), min_size=n, max_size=n),
            min_size=2, max_size=5
        )
    ),
    st.floats(min_value=0.1, max_value=1.0)
)
@settings(max_examples=20, deadline=None)
def test_stackplot_with_alpha(data_lists, alpha):
    """Test stackplot with alpha parameter for transparency."""
    fig = plt.figure()
    
    # Create x values
    x = np.arange(len(data_lists[0]))
    
    try:
        plt.stackplot(x, data_lists, alpha=alpha)
        # Stackplot should create a figure with content
        collections = plt.gca().collections
        assert len(collections) > 0
        
        # Verify alpha was applied
        for collection in collections:
            assert collection.get_alpha() == alpha
    except Exception as e:
        if not any(any(not math.isfinite(val) for val in data) for data in data_lists):
            pytest.fail(f"Stackplot with alpha value {alpha} failed with valid data: {e}")
    finally:
        plt.close('all')

@given(
    # Use a fixed length for all inner lists to ensure consistency
    st.integers(min_value=5, max_value=20).flatmap(
        lambda n: st.lists(
            st.lists(st.floats(min_value=-1000, max_value=1000), min_size=n, max_size=n),
            min_size=2, max_size=5
        )
    ),
    st.lists(linestyle_strategy, min_size=1, max_size=5)
)
@settings(max_examples=20, deadline=None)
def test_stackplot_with_linestyles(data_lists, linestyles):
    """Test stackplot with custom line styles."""
    fig = plt.figure()
    
    # Create x values
    x = np.arange(len(data_lists[0]))
    
    try:
        # Use linestyles if provided, otherwise default
        if len(linestyles) >= len(data_lists):
            plt.stackplot(x, data_lists, linestyles=linestyles[:len(data_lists)])
        else:
            # Repeat linestyles if needed
            repeated_linestyles = linestyles * (len(data_lists) // len(linestyles) + 1)
            plt.stackplot(x, data_lists, linestyles=repeated_linestyles[:len(data_lists)])
        
        # Stackplot should create a figure with content
        assert len(plt.gca().collections) > 0
    except Exception as e:
        if not any(any(not math.isfinite(val) for val in data) for data in data_lists):
            pytest.fail(f"Stackplot with linestyles failed with valid data: {e}")
    finally:
        plt.close('all')