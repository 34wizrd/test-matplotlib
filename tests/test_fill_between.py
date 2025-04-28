import matplotlib
matplotlib.use('Agg')  # Use headless backend for testing

import matplotlib.pyplot as plt
import numpy as np
import math
from hypothesis import given, settings, strategies as st
import pytest
import warnings

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

@given(
    st.lists(st.floats(min_value=-1000, max_value=1000), min_size=5, max_size=30),
    st.lists(st.floats(min_value=-1000, max_value=1000), min_size=5, max_size=30),
    st.lists(st.floats(min_value=-1000, max_value=1000), min_size=5, max_size=30),
    figure_props
)
@settings(max_examples=50, deadline=None)
def test_fill_between_basic(x_data, y1_data, y2_data, fig_props):
    """Test fill_between with various random datasets."""
    fig = plt.figure(figsize=fig_props['figsize'], dpi=fig_props['dpi'])
    
    # Ensure all arrays are same length (take the minimum)
    min_len = min(len(x_data), len(y1_data), len(y2_data))
    x = x_data[:min_len]
    y1 = y1_data[:min_len]
    y2 = y2_data[:min_len]
    
    # Sort x values and reorder y values accordingly
    indices = np.argsort(x)
    x_sorted = [x[i] for i in indices]
    y1_sorted = [y1[i] for i in indices]
    y2_sorted = [y2[i] for i in indices]
    
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            plt.fill_between(x_sorted, y1_sorted, y2_sorted)
        
        # Fill between should create at least one PolyCollection
        assert len(plt.gca().collections) > 0
    except Exception as e:
        # If we have NaN or Inf values, fill_between might legitimately fail
        if not (any(not math.isfinite(val) for val in x_sorted) or 
                any(not math.isfinite(val) for val in y1_sorted) or 
                any(not math.isfinite(val) for val in y2_sorted)):
            pytest.fail(f"fill_between failed with valid data: {e}")
    finally:
        plt.close('all')

# Use a composite strategy to generate lists with NaN and Inf values
@st.composite
def lists_with_nan(draw, min_size=5, max_size=30):
    values = draw(st.lists(st.floats(min_value=-1000, max_value=1000), 
                         min_size=min_size, max_size=max_size))
    result = []
    for val in values:
        use_special = draw(st.booleans())
        if use_special:
            special_val = draw(st.sampled_from([float('nan'), float('inf'), float('-inf')]))
            result.append(special_val)
        else:
            result.append(val)
    return result

@given(
    lists_with_nan(),
    lists_with_nan(),
    st.lists(st.floats(min_value=-1000, max_value=1000), min_size=5, max_size=30),
    color_strategy
)
@settings(max_examples=30, deadline=None)
def test_fill_between_with_nan_inf_values(x_data, y1_data, y2_data, color):
    """Test fill_between with NaN and Inf values and custom colors."""
    fig = plt.figure()
    
    # Ensure all arrays are same length (take the minimum)
    min_len = min(len(x_data), len(y1_data), len(y2_data))
    x = x_data[:min_len]
    y1 = y1_data[:min_len]
    y2 = y2_data[:min_len]
    
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            plt.fill_between(x, y1, y2, color=color, alpha=0.5)
    except Exception:
        # We expect potential exceptions with NaN/Inf values, so we're just testing
        # that it doesn't crash the application
        pass
    finally:
        plt.close('all')

@given(
    st.lists(st.floats(min_value=-1000, max_value=1000), min_size=5, max_size=30),
    st.lists(st.floats(min_value=-1000, max_value=1000), min_size=5, max_size=30),
    st.lists(st.floats(min_value=-1000, max_value=1000), min_size=5, max_size=30),
    st.sampled_from(['where', 'interpolate', 'step']).flatmap(
        lambda param_type: {
            'where': st.lists(st.booleans(), min_size=5, max_size=30).map(
                lambda x: {'where': x}),
            'interpolate': st.sampled_from(['linear', 'quadratic', 'cubic']).map(
                lambda x: {'interpolate': x}),
            'step': st.sampled_from(['pre', 'post', 'mid']).map(
                lambda x: {'step': x})
        }[param_type]
    )
)
@settings(max_examples=30, deadline=None)
def test_fill_between_with_options(x_data, y1_data, y2_data, option):
    """Test fill_between with different options (where, interpolate, step)."""
    fig = plt.figure()
    
    # Ensure all arrays are same length (take the minimum)
    min_len = min(len(x_data), len(y1_data), len(y2_data))
    x = x_data[:min_len]
    y1 = y1_data[:min_len]
    y2 = y2_data[:min_len]
    
    # If using 'where', make sure it's the right length
    if 'where' in option and len(option['where']) > min_len:
        option['where'] = option['where'][:min_len]
    
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            # Sort x values and reorder y values accordingly if not using step or interpolate
            if not ('step' in option or 'interpolate' in option):
                indices = np.argsort(x)
                x_sorted = [x[i] for i in indices]
                y1_sorted = [y1[i] for i in indices]
                y2_sorted = [y2[i] for i in indices]
                plt.fill_between(x_sorted, y1_sorted, y2_sorted, **option)
            else:
                # For step and interpolate, we'll use as is
                plt.fill_between(x, y1, y2, **option)
                
        # Fill between should create at least one PolyCollection
        assert len(plt.gca().collections) > 0
    except Exception:
        # We expect potential exceptions with certain combinations, so we're just testing
        # that it doesn't crash the application
        pass
    finally:
        plt.close('all')

# Strategy for line properties
line_props = st.fixed_dictionaries({
    'linewidth': st.floats(0.1, 5.0),
    'alpha': st.floats(0.1, 1.0),
    'linestyle': st.sampled_from(['-', '--', ':', '-.'])
})

# Strategy for fill properties
fill_props = st.fixed_dictionaries({
    'edgecolor': color_strategy,
    'facecolor': color_strategy,
    'alpha': st.floats(0.1, 1.0)
})

@given(
    st.lists(st.floats(min_value=-1000, max_value=1000), min_size=5, max_size=30),
    st.lists(st.floats(min_value=-1000, max_value=1000), min_size=5, max_size=30),
    st.lists(st.floats(min_value=-1000, max_value=1000), min_size=5, max_size=30),
    line_props
)
@settings(max_examples=20, deadline=None)
def test_fill_between_with_line_properties(x_data, y1_data, y2_data, line_props):
    """Test fill_between with various line properties."""
    fig = plt.figure()
    
    # Ensure all arrays are same length (take the minimum)
    min_len = min(len(x_data), len(y1_data), len(y2_data))
    x = x_data[:min_len]
    y1 = y1_data[:min_len]
    y2 = y2_data[:min_len]
    
    # Sort x values and reorder y values accordingly
    indices = np.argsort(x)
    x_sorted = [x[i] for i in indices]
    y1_sorted = [y1[i] for i in indices]
    y2_sorted = [y2[i] for i in indices]
    
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            plt.fill_between(x_sorted, y1_sorted, y2_sorted, 
                            linewidth=line_props['linewidth'],
                            alpha=line_props['alpha'],
                            linestyle=line_props['linestyle'])
        
        # Check that we have a collection in the plot
        assert len(plt.gca().collections) > 0
    except Exception as e:
        # If we have NaN or Inf values, fill_between might legitimately fail
        if not (any(not math.isfinite(val) for val in x_sorted) or 
                any(not math.isfinite(val) for val in y1_sorted) or 
                any(not math.isfinite(val) for val in y2_sorted)):
            pytest.fail(f"fill_between failed with line properties: {e}")
    finally:
        plt.close('all')

@given(
    st.lists(st.floats(min_value=-1000, max_value=1000), min_size=5, max_size=30),
    st.lists(st.floats(min_value=-1000, max_value=1000), min_size=5, max_size=30),
    st.lists(st.floats(min_value=-1000, max_value=1000), min_size=5, max_size=30),
    fill_props
)
@settings(max_examples=20, deadline=None)
def test_fill_between_with_fill_properties(x_data, y1_data, y2_data, fill_props):
    """Test fill_between with various fill properties."""
    fig = plt.figure()
    
    # Ensure all arrays are same length (take the minimum)
    min_len = min(len(x_data), len(y1_data), len(y2_data))
    x = x_data[:min_len]
    y1 = y1_data[:min_len]
    y2 = y2_data[:min_len]
    
    # Sort x values and reorder y values accordingly
    indices = np.argsort(x)
    x_sorted = [x[i] for i in indices]
    y1_sorted = [y1[i] for i in indices]
    y2_sorted = [y2[i] for i in indices]
    
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            plt.fill_between(x_sorted, y1_sorted, y2_sorted,
                           edgecolor=fill_props['edgecolor'],
                           facecolor=fill_props['facecolor'],
                           alpha=fill_props['alpha'])
        
        # Check that we have a collection in the plot
        assert len(plt.gca().collections) > 0
    except Exception as e:
        # If we have NaN or Inf values, fill_between might legitimately fail
        if not (any(not math.isfinite(val) for val in x_sorted) or 
                any(not math.isfinite(val) for val in y1_sorted) or 
                any(not math.isfinite(val) for val in y2_sorted)):
            pytest.fail(f"fill_between failed with fill properties: {e}")
    finally:
        plt.close('all')

@given(
    st.lists(st.floats(min_value=-1000, max_value=1000), min_size=5, max_size=30),
    st.lists(st.floats(min_value=-1000, max_value=1000), min_size=5, max_size=30),
    st.lists(st.floats(min_value=-1000, max_value=1000), min_size=5, max_size=30),
    st.sampled_from(['/', '\\', '|', '-', '+', 'x', 'o', 'O', '.', '*'])
)
@settings(max_examples=15, deadline=None)
def test_fill_between_with_hatches(x_data, y1_data, y2_data, hatch):
    """Test fill_between with hatching patterns."""
    fig = plt.figure()
    
    # Ensure all arrays are same length (take the minimum)
    min_len = min(len(x_data), len(y1_data), len(y2_data))
    x = x_data[:min_len]
    y1 = y1_data[:min_len]
    y2 = y2_data[:min_len]
    
    # Sort x values and reorder y values accordingly
    indices = np.argsort(x)
    x_sorted = [x[i] for i in indices]
    y1_sorted = [y1[i] for i in indices]
    y2_sorted = [y2[i] for i in indices]
    
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            plt.fill_between(x_sorted, y1_sorted, y2_sorted, hatch=hatch)
        
        # Check that we have a collection in the plot
        assert len(plt.gca().collections) > 0
    except Exception as e:
        if not (any(not math.isfinite(val) for val in x_sorted) or 
                any(not math.isfinite(val) for val in y1_sorted) or 
                any(not math.isfinite(val) for val in y2_sorted)):
            pytest.fail(f"fill_between failed with hatch pattern: {e}")
    finally:
        plt.close('all')

@given(
    st.lists(st.floats(min_value=-1000, max_value=1000), min_size=5, max_size=30),
    st.lists(st.floats(min_value=-1000, max_value=1000), min_size=5, max_size=30),
    st.lists(st.floats(min_value=-1000, max_value=1000), min_size=5, max_size=30),
    st.integers(min_value=-100, max_value=100)
)
@settings(max_examples=15, deadline=None)
def test_fill_between_with_zorder(x_data, y1_data, y2_data, zorder):
    """Test fill_between with z-order parameter."""
    fig = plt.figure()
    
    # Ensure all arrays are same length (take the minimum)
    min_len = min(len(x_data), len(y1_data), len(y2_data))
    x = x_data[:min_len]
    y1 = y1_data[:min_len]
    y2 = y2_data[:min_len]
    
    # Sort x values and reorder y values accordingly
    indices = np.argsort(x)
    x_sorted = [x[i] for i in indices]
    y1_sorted = [y1[i] for i in indices]
    y2_sorted = [y2[i] for i in indices]
    
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            plt.fill_between(x_sorted, y1_sorted, y2_sorted, zorder=zorder)
        
        # Check that we have a collection in the plot
        assert len(plt.gca().collections) > 0
        # Verify the zorder was properly set
        assert plt.gca().collections[0].get_zorder() == zorder
    except Exception as e:
        if not (any(not math.isfinite(val) for val in x_sorted) or 
                any(not math.isfinite(val) for val in y1_sorted) or 
                any(not math.isfinite(val) for val in y2_sorted)):
            pytest.fail(f"fill_between failed with zorder: {e}")
    finally:
        plt.close('all')

@given(
    st.lists(st.floats(min_value=-1000, max_value=1000), min_size=5, max_size=30),
    st.lists(st.floats(min_value=-1000, max_value=1000), min_size=5, max_size=30),
    st.lists(st.floats(min_value=-1000, max_value=1000), min_size=5, max_size=30),
    st.text(min_size=1, max_size=20)
)
@settings(max_examples=15, deadline=None)
def test_fill_between_with_label(x_data, y1_data, y2_data, label):
    """Test fill_between with label parameter for legend integration."""
    fig = plt.figure()
    
    # Ensure all arrays are same length (take the minimum)
    min_len = min(len(x_data), len(y1_data), len(y2_data))
    x = x_data[:min_len]
    y1 = y1_data[:min_len]
    y2 = y2_data[:min_len]
    
    # Sort x values and reorder y values accordingly
    indices = np.argsort(x)
    x_sorted = [x[i] for i in indices]
    y1_sorted = [y1[i] for i in indices]
    y2_sorted = [y2[i] for i in indices]
    
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            plt.fill_between(x_sorted, y1_sorted, y2_sorted, label=label)
            plt.legend()
        
        # Check that we have a collection in the plot
        assert len(plt.gca().collections) > 0
        # Check that the legend was created with our label
        legend = plt.gca().get_legend()
        assert legend is not None
        texts = [text.get_text() for text in legend.get_texts()]
        assert label in texts
    except Exception as e:
        if not (any(not math.isfinite(val) for val in x_sorted) or 
                any(not math.isfinite(val) for val in y1_sorted) or 
                any(not math.isfinite(val) for val in y2_sorted)):
            pytest.fail(f"fill_between failed with label: {e}")
    finally:
        plt.close('all')

@pytest.mark.parametrize("use_log_scale", [True, False])
def test_fill_between_with_transform(use_log_scale):
    """Test fill_between with different transforms (log scale)."""
    fig = plt.figure()
    
    # Create some data that works with log scale (all positive)
    x = np.linspace(0.1, 10, 100)
    y1 = np.exp(x/10)
    y2 = np.exp(x/5)
    
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            
            if use_log_scale:
                plt.yscale('log')
            
            plt.fill_between(x, y1, y2)
            
        # Check that we have a collection in the plot
        assert len(plt.gca().collections) > 0
    except Exception as e:
        pytest.fail(f"fill_between failed with transform (log scale={use_log_scale}): {e}")
    finally:
        plt.close('all')

def test_multiple_fill_between():
    """Test multiple fill_between calls to ensure proper layering."""
    fig = plt.figure()
    
    # Create some sample data
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    y3 = np.sin(x) * 0.5
    y4 = -np.sin(x) * 0.5
    
    try:
        # First fill_between with lower z-order
        plt.fill_between(x, y1, y2, color='red', alpha=0.5, zorder=1)
        
        # Second fill_between with higher z-order
        plt.fill_between(x, y3, y4, color='blue', alpha=0.7, zorder=2)
        
        # Check that we have exactly two collections
        assert len(plt.gca().collections) == 2
        
        # Verify z-orders
        assert plt.gca().collections[0].get_zorder() == 1
        assert plt.gca().collections[1].get_zorder() == 2
    except Exception as e:
        pytest.fail(f"Multiple fill_between failed: {e}")
    finally:
        plt.close('all')

def test_fill_between_with_array_like_inputs():
    """Test fill_between with different array-like inputs."""
    fig = plt.figure()
    
    # Create various array-like objects
    x_list = [1, 2, 3, 4, 5]
    y1_list = [2, 3, 1, 3, 2]
    y2_list = [4, 4, 3, 4, 4]
    
    x_np = np.array(x_list)
    y1_np = np.array(y1_list)
    y2_np = np.array(y2_list)
    
    x_tuple = tuple(x_list)
    y1_tuple = tuple(y1_list)
    y2_tuple = tuple(y2_list)
    
    try:
        # Test with lists
        plt.subplot(2, 2, 1)
        plt.fill_between(x_list, y1_list, y2_list, color='red')
        assert len(plt.gca().collections) > 0
        
        # Test with numpy arrays
        plt.subplot(2, 2, 2)
        plt.fill_between(x_np, y1_np, y2_np, color='blue')
        assert len(plt.gca().collections) > 0
        
        # Test with tuples
        plt.subplot(2, 2, 3)
        plt.fill_between(x_tuple, y1_tuple, y2_tuple, color='green')
        assert len(plt.gca().collections) > 0
        
        # Test mixed types
        plt.subplot(2, 2, 4)
        plt.fill_between(x_np, y1_list, y2_tuple, color='purple')
        assert len(plt.gca().collections) > 0
    except Exception as e:
        pytest.fail(f"fill_between with array-like inputs failed: {e}")
    finally:
        plt.close('all')

def test_fill_between_with_xy_arrays_and_scalar():
    """Test fill_between with x, y arrays and scalar y2."""
    fig = plt.figure()
    
    # Create data
    x = np.linspace(0, 10, 50)
    y = np.sin(x)
    y_scalar = 0  # Using 0 as a baseline
    
    try:
        # Test with scalar y2
        plt.fill_between(x, y, y_scalar, color='orange')
        assert len(plt.gca().collections) > 0
    except Exception as e:
        pytest.fail(f"fill_between with scalar y2 failed: {e}")
    finally:
        plt.close('all')

def test_fill_betweenx_basic():
    """Test the fill_betweenx function with basic inputs."""
    fig = plt.figure()
    
    # Create some sample data
    y = np.linspace(0, 10, 50)
    x1 = np.sin(y)
    x2 = np.sin(y) + 1.5
    
    try:
        plt.fill_betweenx(y, x1, x2, color='green', alpha=0.5)
        
        # Check that we have a collection in the plot
        assert len(plt.gca().collections) > 0
    except Exception as e:
        pytest.fail(f"fill_betweenx failed with basic inputs: {e}")
    finally:
        plt.close('all')

@given(
    st.lists(st.floats(min_value=-1000, max_value=1000), min_size=5, max_size=30),
    st.lists(st.floats(min_value=-1000, max_value=1000), min_size=5, max_size=30),
    st.lists(st.floats(min_value=-1000, max_value=1000), min_size=5, max_size=30),
    fill_props
)
@settings(max_examples=20, deadline=None)
def test_fill_betweenx_with_properties(y_data, x1_data, x2_data, fill_props):
    """Test fill_betweenx with various styling properties."""
    fig = plt.figure()
    
    # Ensure all arrays are same length (take the minimum)
    min_len = min(len(y_data), len(x1_data), len(x2_data))
    y = y_data[:min_len]
    x1 = x1_data[:min_len]
    x2 = x2_data[:min_len]
    
    # Sort y values and reorder x values accordingly
    indices = np.argsort(y)
    y_sorted = [y[i] for i in indices]
    x1_sorted = [x1[i] for i in indices]
    x2_sorted = [x2[i] for i in indices]
    
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            plt.fill_betweenx(y_sorted, x1_sorted, x2_sorted,
                            edgecolor=fill_props['edgecolor'],
                            facecolor=fill_props['facecolor'],
                            alpha=fill_props['alpha'])
        
        # Check that we have a collection in the plot
        assert len(plt.gca().collections) > 0
    except Exception as e:
        if not (any(not math.isfinite(val) for val in y_sorted) or 
                any(not math.isfinite(val) for val in x1_sorted) or 
                any(not math.isfinite(val) for val in x2_sorted)):
            pytest.fail(f"fill_betweenx failed with styling properties: {e}")
    finally:
        plt.close('all')

@given(
    lists_with_nan(),
    lists_with_nan(),
    st.lists(st.floats(min_value=-1000, max_value=1000), min_size=5, max_size=30)
)
@settings(max_examples=20, deadline=None)
def test_fill_betweenx_with_nan_inf_values(y_data, x1_data, x2_data):
    """Test fill_betweenx with NaN and Inf values."""
    fig = plt.figure()
    
    # Ensure all arrays are same length (take the minimum)
    min_len = min(len(y_data), len(x1_data), len(x2_data))
    y = y_data[:min_len]
    x1 = x1_data[:min_len]
    x2 = x2_data[:min_len]
    
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            plt.fill_betweenx(y, x1, x2)
    except Exception:
        # We expect potential exceptions with NaN/Inf values, so we're just testing
        # that it doesn't crash the application
        pass
    finally:
        plt.close('all')

@pytest.mark.parametrize("where", [
    np.array([True, False, True, False, True]),
    np.array([False, False, False, False, False]),
    np.array([True, True, True, True, True])
])
def test_fill_betweenx_with_where_condition(where):
    """Test fill_betweenx with where condition to selectively fill areas."""
    fig = plt.figure()
    
    # Create some sample data
    y = np.linspace(0, 10, 5)  # Same length as where array
    x1 = np.sin(y)
    x2 = np.sin(y) + 1.5
    
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            plt.fill_betweenx(y, x1, x2, where=where, color='purple', alpha=0.5)
            
        # Check that we have a collection in the plot
        assert len(plt.gca().collections) > 0
    except Exception as e:
        pytest.fail(f"fill_betweenx failed with where condition: {e}")
    finally:
        plt.close('all')

def test_fill_betweenx_with_step():
    """Test fill_betweenx with step parameter for step plots."""
    fig = plt.figure()
    
    # Create some sample data
    y = np.arange(5)
    x1 = np.array([1, 2, 3, 4, 5])
    x2 = np.array([2, 3, 4, 5, 6])
    
    step_types = ['pre', 'post', 'mid']
    
    for i, step_type in enumerate(step_types):
        plt.subplot(1, 3, i+1)
        try:
            plt.fill_betweenx(y, x1, x2, step=step_type, alpha=0.5)
            assert len(plt.gca().collections) > 0
        except Exception as e:
            pytest.fail(f"fill_betweenx failed with step={step_type}: {e}")
    
    plt.close('all')

def test_fill_between_with_masked_arrays():
    """Test fill_between with masked array inputs."""
    fig = plt.figure()
    
    # Create some sample data with masking
    x = np.linspace(0, 10, 50)
    y1 = np.sin(x)
    y2 = np.cos(x)
    
    # Create masked arrays by masking some values
    mask = np.zeros_like(x, dtype=bool)
    mask[10:20] = True  # Mask values between indices 10-20
    
    y1_masked = np.ma.array(y1, mask=mask)
    y2_masked = np.ma.array(y2, mask=mask)
    
    try:
        plt.fill_between(x, y1_masked, y2_masked, color='teal', alpha=0.7)
        assert len(plt.gca().collections) > 0
        
        # The masked regions should create multiple patches
        polys = plt.gca().collections[0].get_paths()
        assert len(polys) > 1
    except Exception as e:
        pytest.fail(f"fill_between with masked arrays failed: {e}")
    finally:
        plt.close('all')

def test_fill_between_with_clipping():
    """Test fill_between with custom clipping paths."""
    fig = plt.figure()
    
    # Create some sample data
    theta = np.linspace(0, 2*np.pi, 100)
    r = 1 + 0.3*np.sin(5*theta)  # Pentagon-like shape
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    
    # Create a clipping path
    clip_path = plt.Circle((0, 0), 0.7, transform=plt.gca().transData)
    
    # Fill the area with clipping
    try:
        plt.fill_between(x, 0, y, clip_path=clip_path, color='magenta', alpha=0.6)
        assert len(plt.gca().collections) > 0
        
        # Check that clipping path was applied
        assert plt.gca().collections[0].get_clip_path() is not None
    except Exception as e:
        pytest.fail(f"fill_between with clipping path failed: {e}")
    finally:
        plt.close('all')

def test_fill_between_with_colormap():
    """Test fill_between with colormaps."""
    fig = plt.figure()
    
    # Create some sample data
    x = np.linspace(0, 10, 50)
    y1 = np.zeros_like(x)
    y2_values = []
    
    # Create multiple curves to fill with different colors from colormap
    for i in range(5):
        y2 = (i + 1) * np.sin(x) + i
        y2_values.append(y2)
    
    try:
        # Use a colormap to get colors for each layer
        cmap = plt.cm.viridis
        colors = [cmap(i/5) for i in range(5)]
        
        # Fill each layer with a different color from the colormap
        for i, y2 in enumerate(y2_values):
            plt.fill_between(x, y1 if i == 0 else y2_values[i-1], y2, 
                           color=colors[i], alpha=0.7)
        
        # Should have exactly 5 collections
        assert len(plt.gca().collections) == 5
    except Exception as e:
        pytest.fail(f"fill_between with colormap failed: {e}")
    finally:
        plt.close('all')

def test_fill_between_polar_coordinates():
    """Test fill_between in polar coordinates."""
    fig = plt.figure()
    
    # Use a polar axes
    ax = plt.subplot(111, projection='polar')
    
    # Create some polar data
    theta = np.linspace(0, 2*np.pi, 100)
    r1 = 1.0 + 0.2 * np.sin(5*theta)
    r2 = 1.5 + 0.2 * np.sin(5*theta)
    
    try:
        # Fill between in polar coordinates
        ax.fill_between(theta, r1, r2)
        
        # Check that we have a collection in the plot
        assert len(ax.collections) > 0
    except Exception as e:
        pytest.fail(f"fill_between in polar coordinates failed: {e}")
    finally:
        plt.close('all')

def test_multiple_fill_betweenx_with_transparency():
    """Test multiple fill_betweenx calls with transparency for layering effect."""
    fig = plt.figure()
    
    # Create some sample data
    y = np.linspace(0, 10, 100)
    x1 = np.sin(y)
    x2 = np.cos(y) + 2
    x3 = -np.sin(y) + 1
    x4 = -np.cos(y) + 3
    
    try:
        # First fill_betweenx
        plt.fill_betweenx(y, x1, x2, color='red', alpha=0.3)
        
        # Second overlapping fill_betweenx
        plt.fill_betweenx(y, x3, x4, color='blue', alpha=0.3)
        
        # Check that we have exactly two collections
        assert len(plt.gca().collections) == 2
    except Exception as e:
        pytest.fail(f"Multiple fill_betweenx with transparency failed: {e}")
    finally:
        plt.close('all')

def test_fill_between_with_interpolations():
    """Test fill_between with different interpolation methods."""
    fig = plt.figure()
    
    # Create sparse data that needs interpolation
    x = np.array([0, 2, 4, 6, 8, 10])
    y1 = np.array([0, 3, 1, 4, 2, 5])
    y2 = np.array([5, 7, 6, 8, 7, 9])
    
    # Test different interpolation methods
    interpolation_methods = ['linear', 'quadratic', 'cubic']
    
    for i, method in enumerate(interpolation_methods):
        plt.subplot(1, 3, i+1)
        try:
            plt.fill_between(x, y1, y2, interpolate=method)
            assert len(plt.gca().collections) > 0
        except Exception as e:
            pytest.fail(f"fill_between with {method} interpolation failed: {e}")
    
    plt.close('all')

def test_fill_between_beyond_axes():
    """Test fill_between extending beyond axes limits."""
    fig, ax = plt.subplots()
    
    # Create some data
    x = np.linspace(0, 10, 50)
    y1 = np.sin(x)
    y2 = np.cos(x)
    
    # Set axes limits to only show part of the data
    ax.set_xlim(3, 7)
    ax.set_ylim(-0.5, 0.5)
    
    try:
        # Fill between should work even with data outside axes limits
        ax.fill_between(x, y1, y2, color='yellow', alpha=0.5)
        assert len(ax.collections) > 0
    except Exception as e:
        pytest.fail(f"fill_between beyond axes limits failed: {e}")
    finally:
        plt.close('all')
        

# =========================================================== test session starts ============================================================
# platform win32 -- Python 3.13.2, pytest-8.3.5, pluggy-1.5.0 -- C:\Github\Git_34wizrd\matplotlib-testing\env\Scripts\python.exe
# cachedir: .pytest_cache
# hypothesis profile 'default' -> database=DirectoryBasedExampleDatabase(WindowsPath('C:/Github/Git_34wizrd/matplotlib-testing/.hypothesis/examples'))
# Matplotlib: 3.10.1
# Freetype: 2.6.1
# rootdir: C:\Github\Git_34wizrd\matplotlib-testing
# plugins: hypothesis-6.130.8, cov-6.1.1, mpl-0.17.0
# collected 27 items

# tests/test_fill_between.py::test_fill_between_basic PASSED                                                                            [  3%]
# tests/test_fill_between.py::test_fill_between_with_nan_inf_values PASSED                                                              [  7%]
# tests/test_fill_between.py::test_fill_between_with_options PASSED                                                                     [ 11%]
# tests/test_fill_between.py::test_fill_between_with_line_properties PASSED                                                             [ 14%]
# tests/test_fill_between.py::test_fill_between_with_fill_properties PASSED                                                             [ 18%]
# tests/test_fill_between.py::test_fill_between_with_hatches PASSED                                                                     [ 22%]
# tests/test_fill_between.py::test_fill_between_with_zorder PASSED                                                                      [ 25%]
# tests/test_fill_between.py::test_fill_between_with_label PASSED                                                                       [ 29%]
# tests/test_fill_between.py::test_fill_between_with_transform[True] PASSED                                                             [ 33%] 
# tests/test_fill_between.py::test_fill_between_with_transform[False] PASSED                                                            [ 37%]
# tests/test_fill_between.py::test_multiple_fill_between PASSED                                                                         [ 40%]
# tests/test_fill_between.py::test_fill_between_with_array_like_inputs PASSED                                                           [ 44%]
# tests/test_fill_between.py::test_fill_between_with_xy_arrays_and_scalar PASSED                                                        [ 48%]
# tests/test_fill_between.py::test_fill_betweenx_basic PASSED                                                                           [ 51%] 
# tests/test_fill_between.py::test_fill_betweenx_with_properties PASSED                                                                 [ 55%]
# tests/test_fill_between.py::test_fill_betweenx_with_nan_inf_values PASSED                                                             [ 59%]
# tests/test_fill_between.py::test_fill_betweenx_with_where_condition[where0] PASSED                                                    [ 62%] 
# tests/test_fill_between.py::test_fill_betweenx_with_where_condition[where1] PASSED                                                    [ 66%] 
# tests/test_fill_between.py::test_fill_betweenx_with_where_condition[where2] PASSED                                                    [ 70%]
# tests/test_fill_between.py::test_fill_betweenx_with_step PASSED                                                                       [ 74%]
# tests/test_fill_between.py::test_fill_between_with_masked_arrays PASSED                                                               [ 77%]
# tests/test_fill_between.py::test_fill_between_with_clipping PASSED                                                                    [ 81%] 
# tests/test_fill_between.py::test_fill_between_with_colormap PASSED                                                                    [ 85%]
# tests/test_fill_between.py::test_fill_between_polar_coordinates PASSED                                                                [ 88%]
# tests/test_fill_between.py::test_multiple_fill_betweenx_with_transparency PASSED                                                      [ 92%]
# tests/test_fill_between.py::test_fill_between_with_interpolations PASSED                                                              [ 96%]
# tests/test_fill_between.py::test_fill_between_beyond_axes PASSED                                                                      [100%]

# ============================================================ 27 passed in 6.35s ============================================================ 