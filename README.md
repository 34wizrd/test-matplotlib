# Matplotlib Testing Project

This project contains a suite of tests for various Matplotlib plotting functions. It is designed to help you verify the correctness of plots and generate test reports.

## Project Structure

- `requirements.txt` — Python dependencies
- `tests/` — Test files for different plot types
- `report.html` — HTML test report (generated after running tests)
- `htmlcov/` — Coverage reports (if generated)
- `assets/` — Static assets (e.g., CSS)

## Setup Instructions

### 1. Clone the Repository

```sh
git clone https://github.com/34wizrd/test-matplotlib.git
cd matplotlib-testing
```

### 2. Create and Activate a Virtual Environment (Recommended)

**Windows (PowerShell):**
```sh
python -m venv env
.\env\Scripts\Activate.ps1
```

**macOS/Linux:**
```sh
python3 -m venv env
source env/bin/activate
```

### 3. Install Dependencies

```sh
pip install -r requirements.txt
```

## Running Tests

### Run All Tests

```sh
pytest
```

### Run a Specific Test File

```sh
pytest tests/test_bar.py
```

### Run a Specific Test Function

```sh
pytest tests/test_bar.py::test_function_name
```

## Generating a Coverage Report

After running your tests with `pytest`, you can generate a coverage report to see how much of your code is covered by tests:

```sh
pytest --cov=.
```

- This will display a coverage summary in the terminal.
- To generate an HTML coverage report, run:

  ```sh
  pytest --cov=. --cov-report=html
  ```

- The HTML coverage report will be available in the `htmlcov/` directory. Open `htmlcov/index.html` in your browser to view detailed coverage information.

## Generating and Viewing the HTML Test Report (pytest-html)

You can also generate a detailed HTML test report using the `pytest-html` plugin. After running your tests, run:

```sh
pytest --html=report.html
```

- This will create a `report.html` file in the project root.
- To open the report:
  - **Double-click** `report.html` to open it in your web browser, or
  - **Right-click** the file and select "Open with" → your preferred browser.

## Additional Notes

- For more advanced pytest options, see the [pytest documentation](https://docs.pytest.org/en/stable/).

---

If you encounter any issues, please check your Python version and ensure all dependencies are installed correctly.
