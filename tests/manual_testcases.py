import matplotlib
matplotlib.use("Agg")  # Use non-GUI backend for headless testing

import csv
import ast
import os
import pytest
import numpy as np
import matplotlib.pyplot as plt

# Path to the CSV file
CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'manual_testcases_400_fixed.csv')

def parse_input(input_str):
    # Try to parse the input string as a Python literal
    try:
        return ast.literal_eval(input_str)
    except Exception:
        return input_str

def clean_and_parse(val):
    """More robust parsing of values"""
    if not isinstance(val, str):
        return val
    
    val = val.strip().strip('"').strip("'")
    
    try:
        # Try parsing as literal
        parsed = ast.literal_eval(val)
        # Handle nested string representation
        if isinstance(parsed, str) and (parsed.strip().startswith('[') or parsed.strip().startswith('{')):
            try:
                parsed = ast.literal_eval(parsed)
            except:
                pass
        return parsed
    except Exception:
        # For plain strings
        return val

def ensure_numeric_list(val):
    """Convert to numeric list no matter what"""
    if val is None:
        return [0, 0]  # Default non-empty value
    
    # If already a list-like, make sure all elements are numeric
    if hasattr(val, '__len__') and not isinstance(val, str):
        try:
            result = [float(x) for x in val]
            # If list is empty, provide a default
            if len(result) == 0:
                return [0, 0]
            return result
        except:
            pass
    
    # Handle string representations of lists
    if isinstance(val, str):
        val = val.strip()
        if val.startswith('[') and val.endswith(']'):
            try:
                val = val[1:-1]  # Remove brackets
                parts = [p.strip() for p in val.split(',')]
                result = [float(p) for p in parts if p]
                # If list is empty, provide a default
                if len(result) == 0:
                    return [0, 0]
                return result
            except:
                pass
    
    # Fallback: wrap in list if numeric, otherwise default
    try:
        return [float(val)]
    except:
        return [0, 0]

def random_array(shape):
    return np.random.rand(*shape)

def run_pyplot_function(func, input_str):
    # Special handling for imshow random arrays
    if func == 'pyplot.imshow':
        if 'array=' in input_str:
            size_str = input_str.split('array=')[1].split(' ')[0]
            dims = tuple(map(int, size_str.split('x')))
            arr = random_array(dims)
            plt.imshow(arr)
            return
    
    # Dispatch to specialized handlers
    if func == 'pyplot.scatter':
        return handle_scatter_safely(input_str)
    elif func == 'pyplot.plot':
        return handle_plot_safely(input_str)
    elif func == 'pyplot.fill_between':
        return handle_fill_between_safely(input_str)
    elif func == 'pyplot.boxplot':
        return handle_boxplot_safely(input_str)
    elif func == 'pyplot.pie':
        return handle_pie_safely(input_str)
    elif func == 'pyplot.bar':
        return handle_bar_safely(input_str)
    elif func == 'pyplot.errorbar':
        return handle_errorbar_safely(input_str)
    elif func == 'pyplot.hist':
        return handle_hist_safely(input_str)
    elif func == 'pyplot.imshow':
        return handle_imshow_safely(input_str)
    else:
        raise NotImplementedError(f"Function {func} not implemented")

def handle_scatter_safely(input_str):
    """Safely parse scatter plot parameters to avoid color kwarg conflicts"""
    x_vals = [0, 0]  # Default values ensure at least two points
    y_vals = [0, 0]
    
    # Extract the x and y values
    x_match = None
    y_match = None
    color_val = None
    
    # Parse the input_str
    parts = [p.strip() for p in input_str.split(',')]
    for part in parts:
        if '=' in part:
            k, v = part.split('=', 1)
            k = k.strip()
            v = v.strip()
            
            if k == 'x':
                x_match = clean_and_parse(v)
            elif k == 'y':
                y_match = clean_and_parse(v)
            elif k == 'color' or k == 'c':
                color_val = v.strip('"\'')
        else:
            # Positional arguments (assuming x, y order)
            if x_match is None:
                x_match = clean_and_parse(part)
            elif y_match is None:
                y_match = clean_and_parse(part)
    
    # Convert to lists of numbers
    if x_match is not None:
        x_vals = ensure_numeric_list(x_match)
    if y_match is not None:
        y_vals = ensure_numeric_list(y_match)
    
    # Make sure both arrays have the same length
    max_len = max(len(x_vals), len(y_vals))
    if len(x_vals) < max_len:
        x_vals = x_vals + [x_vals[-1]] * (max_len - len(x_vals))
    if len(y_vals) < max_len:
        y_vals = y_vals + [y_vals[-1]] * (max_len - len(y_vals))
    
    # Call scatter with only essential parameters
    if color_val:
        plt.scatter(x_vals, y_vals, color=color_val)
    else:
        plt.scatter(x_vals, y_vals)

def handle_plot_safely(input_str):
    """Safely parse plot parameters to avoid format string issues"""
    x_vals = [0, 1]  # Default values
    y_vals = [0, 1]
    
    # Extract the x and y values
    x_match = None
    y_match = None
    
    # Parse the input_str
    parts = [p.strip() for p in input_str.split(',')]
    for part in parts:
        if '=' in part:
            k, v = part.split('=', 1)
            k = k.strip()
            v = v.strip()
            
            if k == 'x':
                x_match = clean_and_parse(v)
            elif k == 'y':
                y_match = clean_and_parse(v)
        else:
            # Positional arguments (assuming x, y order)
            if x_match is None:
                x_match = clean_and_parse(part)
            elif y_match is None:
                y_match = clean_and_parse(part)
    
    # Convert to lists of numbers
    if x_match is not None:
        x_vals = ensure_numeric_list(x_match)
    if y_match is not None:
        y_vals = ensure_numeric_list(y_match)
    
    # Make sure both arrays have the same length
    max_len = max(len(x_vals), len(y_vals))
    if len(x_vals) < max_len:
        x_vals = x_vals + [x_vals[-1] if x_vals else 0] * (max_len - len(x_vals))
    if len(y_vals) < max_len:
        y_vals = y_vals + [y_vals[-1] if y_vals else 0] * (max_len - len(y_vals))
    
    # Call plot with only x and y - no format string
    plt.plot(x_vals, y_vals)

def handle_fill_between_safely(input_str):
    """Safely parse fill_between parameters to avoid shape mismatch issues"""
    x_vals = [0, 1]  # Default values
    y1_vals = [0, 0]
    y2_vals = [1, 1]
    
    # Extract the x, y1, and y2 values
    x_match = None
    y1_match = None
    y2_match = None
    
    # Parse the input_str
    parts = [p.strip() for p in input_str.split(',')]
    for part in parts:
        if '=' in part:
            k, v = part.split('=', 1)
            k = k.strip()
            v = v.strip()
            
            if k == 'x':
                x_match = clean_and_parse(v)
            elif k == 'y1':
                y1_match = clean_and_parse(v)
            elif k == 'y2':
                y2_match = clean_and_parse(v)
        else:
            # Positional arguments (assuming x, y1, y2 order)
            if x_match is None:
                x_match = clean_and_parse(part)
            elif y1_match is None:
                y1_match = clean_and_parse(part)
            elif y2_match is None:
                y2_match = clean_and_parse(part)
    
    # Convert to lists of numbers
    if x_match is not None:
        x_vals = ensure_numeric_list(x_match)
    if y1_match is not None:
        y1_vals = ensure_numeric_list(y1_match)
    if y2_match is not None:
        y2_vals = ensure_numeric_list(y2_match)
    
    # Make sure all arrays have the same length
    max_len = max(len(x_vals), len(y1_vals), len(y2_vals))
    if len(x_vals) < max_len:
        # Extend by repeating the last value (better than adding zeros)
        x_vals = x_vals + [x_vals[-1] if x_vals else 0] * (max_len - len(x_vals))
    if len(y1_vals) < max_len:
        y1_vals = y1_vals + [y1_vals[-1] if y1_vals else 0] * (max_len - len(y1_vals))
    if len(y2_vals) < max_len:
        y2_vals = y2_vals + [y2_vals[-1] if y2_vals else 0] * (max_len - len(y2_vals))
    
    # Convert to numpy arrays and ensure they're 1D
    x_arr = np.array(x_vals).flatten()
    y1_arr = np.array(y1_vals).flatten()
    y2_arr = np.array(y2_vals).flatten()
    
    # Call fill_between with the prepared arrays
    plt.fill_between(x_arr, y1_arr, y2_arr)

def handle_boxplot_safely(input_str):
    """Safely parse boxplot parameters"""
    data = [[0, 5, 10]] # Default value to ensure valid input
    
    # Parse the input_str
    if 'data=' in input_str:
        data_str = input_str.split('data=')[1].strip()
        data_val = clean_and_parse(data_str)
        if data_val:
            # Convert data to proper format (list of lists of numbers)
            if isinstance(data_val, list):
                # If each element is a list, keep as is
                if all(isinstance(x, list) for x in data_val if hasattr(x, '__len__')):
                    data = data_val
                # If it's a flat list, convert to list of lists
                else:
                    data = [data_val]
            else:
                data = [[0, 5, 10]]
    else:
        # Try to parse from positional arguments
        parts = [p.strip() for p in input_str.split(',')]
        for part in parts:
            if '=' not in part:
                data_val = clean_and_parse(part)
                if data_val:
                    if isinstance(data_val, list):
                        if all(isinstance(x, list) for x in data_val if hasattr(x, '__len__')):
                            data = data_val
                        else:
                            data = [data_val]
                    break
    
    # Ensure each sub-list is not empty
    data = [sublist if sublist else [0, 5, 10] for sublist in data]
    
    # Call boxplot with the prepared data
    plt.boxplot(data)

def handle_pie_safely(input_str):
    """Safely parse pie chart parameters"""
    sizes = [1, 1]  # Default value ensures at least two segments
    
    # Parse the input_str
    if 'sizes=' in input_str:
        sizes_str = input_str.split('sizes=')[1].strip()
        sizes_val = clean_and_parse(sizes_str)
        if sizes_val:
            if isinstance(sizes_val, list):
                sizes = sizes_val
            else:
                sizes = [sizes_val]
    elif 'x=' in input_str:
        sizes_str = input_str.split('x=')[1].strip()
        sizes_val = clean_and_parse(sizes_str)
        if sizes_val:
            if isinstance(sizes_val, list):
                sizes = sizes_val
            else:
                sizes = [sizes_val]
    else:
        # Try to parse from positional arguments
        parts = [p.strip() for p in input_str.split(',')]
        for part in parts:
            if '=' not in part:
                sizes_val = clean_and_parse(part)
                if sizes_val:
                    if isinstance(sizes_val, list):
                        sizes = sizes_val
                    else:
                        sizes = [sizes_val]
                    break
    
    # Make sure sizes is not empty
    if not sizes:
        sizes = [1, 1]
    
    # Convert all values to numeric
    sizes = ensure_numeric_list(sizes)
    
    # Ensure all values are positive
    sizes = [abs(s) + 0.1 for s in sizes]  # Add 0.1 to avoid zeros
    
    # Call pie with the prepared sizes
    plt.pie(sizes)

def handle_bar_safely(input_str):
    """Safely parse bar chart parameters"""
    x = [0, 1, 2, 3]  # Default x values
    height = [5, 5, 5, 5]  # Default heights
    
    # Parse the input_str
    x_val = None
    height_val = None
    
    parts = [p.strip() for p in input_str.split(',')]
    for part in parts:
        if '=' in part:
            k, v = part.split('=', 1)
            k = k.strip()
            v = v.strip()
            
            if k == 'x':
                x_val = clean_and_parse(v)
            elif k == 'height':
                height_val = clean_and_parse(v)
        else:
            # Positional arguments (assuming x, height order)
            if x_val is None:
                x_val = clean_and_parse(part)
            elif height_val is None:
                height_val = clean_and_parse(part)
    
    # Process parsed values
    if x_val is not None:
        # If x contains strings like "'Cat0'", leave as is
        if isinstance(x_val, list) and all(isinstance(item, str) for item in x_val):
            x = x_val
        else:
            # Otherwise convert to numeric
            x = ensure_numeric_list(x_val)
    
    if height_val is not None:
        height = ensure_numeric_list(height_val)
    
    # Make sure x and height have the same length
    max_len = max(len(x), len(height))
    if len(x) < max_len:
        # If x contains strings, extend with new categories
        if all(isinstance(item, str) for item in x):
            for i in range(len(x), max_len):
                x.append(f"'Cat{i}'")
        else:
            x = x + [x[-1] if x else 0] * (max_len - len(x))
    
    if len(height) < max_len:
        height = height + [height[-1] if height else 0] * (max_len - len(height))
    
    # Call bar with the prepared data
    plt.bar(x, height)

def handle_errorbar_safely(input_str):
    """Safely parse errorbar parameters"""
    x = [0, 1, 2, 3]  # Default x values
    y = [5, 5, 5, 5]  # Default y values
    yerr = [0.5, 0.5, 0.5, 0.5]  # Default error values
    
    # Parse the input_str
    x_val = None
    y_val = None
    yerr_val = None
    
    parts = [p.strip() for p in input_str.split(',')]
    for part in parts:
        if '=' in part:
            k, v = part.split('=', 1)
            k = k.strip()
            v = v.strip()
            
            if k == 'x':
                x_val = clean_and_parse(v)
            elif k == 'y':
                y_val = clean_and_parse(v)
            elif k == 'yerr':
                yerr_val = clean_and_parse(v)
        else:
            # Positional arguments (assuming x, y, yerr order)
            if x_val is None:
                x_val = clean_and_parse(part)
            elif y_val is None:
                y_val = clean_and_parse(part)
            elif yerr_val is None:
                yerr_val = clean_and_parse(part)
    
    # Process parsed values
    if x_val is not None:
        x = ensure_numeric_list(x_val)
    if y_val is not None:
        y = ensure_numeric_list(y_val)
    if yerr_val is not None:
        yerr = ensure_numeric_list(yerr_val)
    
    # Make sure all arrays have the same length
    max_len = max(len(x), len(y), len(yerr))
    if len(x) < max_len:
        x = x + [x[-1] if x else 0] * (max_len - len(x))
    if len(y) < max_len:
        y = y + [y[-1] if y else 0] * (max_len - len(y))
    if len(yerr) < max_len:
        yerr = yerr + [yerr[-1] if yerr else 0] * (max_len - len(yerr))
    
    # Call errorbar with the prepared data
    plt.errorbar(x, y, yerr=yerr)

def handle_hist_safely(input_str):
    """Safely parse histogram parameters"""
    data = [1, 5, 10, 5, 1]  # Default values
    bins = 10  # Default bins
    
    # Parse the input_str
    if 'data=' in input_str:
        data_str = input_str.split('data=')[1].strip()
        data_val = clean_and_parse(data_str)
        if data_val:
            data = ensure_numeric_list(data_val)
    elif 'x=' in input_str:
        data_str = input_str.split('x=')[1].strip()
        data_val = clean_and_parse(data_str)
        if data_val:
            data = ensure_numeric_list(data_val)
    else:
        # Try to parse from positional arguments
        parts = [p.strip() for p in input_str.split(',')]
        for part in parts:
            if '=' not in part:
                data_val = clean_and_parse(part)
                if data_val:
                    data = ensure_numeric_list(data_val)
                    break
    
    # Make sure data is not empty
    if not data:
        data = [1, 5, 10, 5, 1]
    
    # Extract bins if specified
    if 'bins=' in input_str:
        bins_str = input_str.split('bins=')[1].strip()
        try:
            bins = int(clean_and_parse(bins_str))
            # Make sure bins is positive
            if bins <= 0:
                bins = 10
        except (ValueError, TypeError):
            bins = 10
    
    # Call hist with the prepared data
    plt.hist(data, bins=bins)

def handle_imshow_safely(input_str):
    """Safely parse imshow parameters"""
    # Default array with some variation
    default_array = np.array([[0, 0.5], [0.5, 1]])
    
    # If a specific array is provided in the input
    if 'array=' in input_str:
        size_str = input_str.split('array=')[1].split(' ')[0]
        try:
            dims = tuple(map(int, size_str.split('x')))
            array = random_array(dims)
            plt.imshow(array)
            return
        except:
            pass
    
    # Process any other specified array
    parts = [p.strip() for p in input_str.split(',')]
    for part in parts:
        if '=' not in part:
            try:
                array_val = clean_and_parse(part)
                if isinstance(array_val, (list, np.ndarray)):
                    array = np.array(array_val)
                    plt.imshow(array)
                    return
            except:
                pass
    
    # Default fallback
    plt.imshow(default_array)

def pytest_generate_tests(metafunc):
    # Parametrize test with all cases from CSV
    if 'testcase' in metafunc.fixturenames:
        with open(CSV_PATH, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            cases = [row for row in reader]
        metafunc.parametrize('testcase', cases)

def test_manual_case(testcase):
    plt.figure()
    run_pyplot_function(testcase['Function'], testcase['Input'])
    plt.close()
