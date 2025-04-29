---
title: "Testing and Validation Procedures"
category: "archival/implementation"
date_created: "2025-04-27"
last_updated: "2025-04-27"
priority: "medium"
components: ["testing", "validation"]
keywords: ["testing", "validation", "quality", "verification", "tests", "scrapers"]
---

# Testing and Validation Procedures

## Purpose

This document outlines the testing and validation procedures for the restaurant review scraper. It provides guidelines for ensuring the reliability, accuracy, and robustness of the scraper through systematic testing.

## Testing Framework

The scraper uses a multi-layered testing approach:

1. **Unit Tests**: Verify individual components in isolation
2. **Integration Tests**: Validate component interactions
3. **Site-Specific Tests**: Ensure site-specific scrapers work correctly
4. **End-to-End Tests**: Confirm complete scraping workflows
5. **Validation Tests**: Verify data quality and accuracy
6. **Performance Tests**: Assess speed and resource usage
7. **Anti-Detection Tests**: Evaluate stealth capabilities

## Unit Tests

Unit tests focus on testing individual functions and classes in isolation. They are located in the `tests/unit` directory.

### Running Unit Tests

```bash
# Run all unit tests
pytest tests/unit

# Run specific unit test file
pytest tests/unit/test_data_processing.py

# Run specific test function
pytest tests/unit/test_data_processing.py::test_clean_review_text
```

### Key Unit Test Categories

#### Data Processing Tests

```python
# tests/unit/test_data_processing.py

def test_clean_review_text():
    # Test with HTML tags
    input_text = "<div>This is a <b>formatted</b> review.</div>"
    expected = "This is a formatted review."
    assert data_processing.clean_review_text(input_text) == expected
    
    # Test with excess whitespace
    input_text = "  Multiple    spaces   and\nline breaks\n\n"
    expected = "Multiple spaces and line breaks"
    assert data_processing.clean_review_text(input_text) == expected
    
    # Test with special characters
    input_text = "Restaurant & café was 100% amazing!"
    expected = "Restaurant & café was 100% amazing!"
    assert data_processing.clean_review_text(input_text) == expected

def test_categorize_review():
    # Test food quality category
    food_review = "The food was delicious, especially the steak."
    assert data_processing.categorize_review(food_review) == "foodQuality"
    
    # Test service category
    service_review = "The waiter was friendly and attentive."
    assert data_processing.categorize_review(service_review) == "service"
    
    # Test atmosphere category
    atmosphere_review = "The ambiance was cozy with nice decor."
    assert data_processing.categorize_review(atmosphere_review) == "atmosphere"

def test_parse_date():
    # Test various date formats
    assert data_processing.parse_date("April 12, 2024", "tripadvisor") == "2024-04-12"
    assert data_processing.parse_date("4/12/2024", "yelp") == "2024-04-12"
    assert data_processing.parse_date("2 weeks ago", "google") == "2024-04-13"  # Assuming test date is April 27, 2025
```

#### Configuration Tests

```python
# tests/unit/test_config.py

def test_load_config():
    # Test loading valid config
    config = config_utils.load_config("tests/fixtures/valid_config.yaml")
    assert config is not None
    assert "restaurant_name" in config
    
    # Test loading with missing file
    with pytest.raises(FileNotFoundError):
        config_utils.load_config("nonexistent_file.yaml")
    
    # Test loading invalid YAML
    with pytest.raises(yaml.YAMLError):
        config_utils.load_config("tests/fixtures/invalid_config.yaml")

def test_merge_client_config():
    # Test merging client config with global config
    global_config = config_utils.load_config("tests/fixtures/global_config.yaml")
    client_config = config_utils.load_config("tests/fixtures/client_config.yaml")
    
    merged = config_utils.merge_configs(global_config, client_config)
    
    # Client settings should override global
    assert merged["restaurant_name"] == client_config["restaurant_name"]
    
    # Global settings should be preserved if not in client config
    assert merged["anti_bot_settings"]["delay_variance"] == global_config["anti_bot_settings"]["delay_variance"]
```

#### Anti-Bot Utility Tests

```python
# tests/unit/test_anti_bot_utils.py

def test_random_delay():
    # Test delay is within expected range
    base_delay = 1.0
    variance = 50  # 50%
    
    # Test with 100 iterations to ensure statistical validity
    for _ in range(100):
        delay = anti_bot_utils.calculate_random_delay(base_delay, variance)
        # Should be between 50% and 150% of base
        assert 0.5 * base_delay <= delay <= 1.5 * base_delay

def test_human_like_typing():
    # Test typing delay generator
    text = "Hello, world!"
    delays = anti_bot_utils.generate_typing_delays(text)
    
    # Should have one delay per character
    assert len(delays) == len(text)
    
    # Delays should be realistic (typically 0.1s to 0.4s per character)
    for delay in delays:
        assert 0.05 <= delay <= 0.5
```

## Integration Tests

Integration tests verify that components work correctly together. They are located in the `tests/integration` directory.

### Running Integration Tests

```bash
# Run all integration tests
pytest tests/integration

# Run specific integration test file
pytest tests/integration/test_scraper_data_pipeline.py
```

### Key Integration Test Categories

#### Scraper + Data Processing Integration

```python
# tests/integration/test_scraper_data_pipeline.py

def test_extract_and_process_reviews():
    # Mock raw review data from scraper
    raw_reviews = [
        {
            "platform": "tripadvisor",
            "reviewerName": "JohnDoe",
            "rating": 4,
            "date": "April 10, 2024",
            "text": "<div>Great food but slow service!</div>"
        },
        {
            "platform": "yelp",
            "reviewerName": "JaneSmith",
            "rating": 2,
            "date": "3/15/2024",
            "text": "The atmosphere was nice but the food was disappointing."
        }
    ]
    
    # Process the raw reviews
    processed_reviews = data_processing.process_reviews(raw_reviews)
    
    # Verify processing was correct
    assert len(processed_reviews) == 2
    assert processed_reviews[0]["standardizedDate"] == "2024-04-10"
    assert processed_reviews[0]["text"] == "Great food but slow service!"
    assert processed_reviews[0]["category"] == "foodQuality"
    assert processed_reviews[0]["sentiment"] == "mixed"
    
    assert processed_reviews[1]["standardizedDate"] == "2024-03-15"
    assert processed_reviews[1]["category"] == "foodQuality"
    assert processed_reviews[1]["sentiment"] == "negative"
```

#### Config + Scraper Integration

```python
# tests/integration/test_config_scraper_integration.py

def test_scraper_applies_config_settings():
    # Load test config
    config = config_utils.load_config("tests/fixtures/test_config.yaml")
    
    # Initialize scraper with config
    scraper = Scraper(config)
    
    # Verify config was applied correctly
    assert scraper.max_reviews_per_platform == config["scraping_settings"]["max_reviews_per_platform"]
    assert scraper.enable_random_delays == config["anti_bot_settings"]["enable_random_delays"]
    assert len(scraper.platforms) == len(config["scraping_settings"]["platforms"])
```

## Site-Specific Tests

Site-specific tests ensure each platform's scraper works correctly. They use mock HTML responses to avoid actual web requests during testing.

### Mock Response Fixtures

The `tests/fixtures` directory contains mock HTML responses for each platform:

- `tripadvisor_restaurant_page.html`
- `yelp_restaurant_page.html`
- `google_restaurant_page.html`

### Site-Specific Test Examples

```python
# tests/site_specific/test_tripadvisor_scraper.py

def test_tripadvisor_review_extraction():
    # Load mock HTML
    with open("tests/fixtures/tripadvisor_restaurant_page.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Create a mock page object
    mock_page = MockPage(html_content)
    
    # Initialize scraper
    tripadvisor_scraper = TripAdvisorScraper({})
    
    # Extract reviews from the mock page
    reviews = tripadvisor_scraper.extract_reviews(mock_page)
    
    # Verify extraction worked correctly
    assert len(reviews) > 0
    assert "reviewerName" in reviews[0]
    assert "rating" in reviews[0]
    assert "date" in reviews[0]
    assert "text" in reviews[0]
    
    # Verify specific review content
    assert any(review["text"].lower().find("delicious food") != -1 for review in reviews)

# Similar tests for Yelp and Google
```

## End-to-End Tests

End-to-end tests verify complete scraping workflows. They can either use mock data or run against real websites with appropriate safeguards.

### Mock-Based End-to-End Tests

```python
# tests/e2e/test_full_scraping_workflow.py

def test_full_scraping_workflow_with_mocks():
    # Setup mocks for all external requests
    with requests_mock.Mocker() as m:
        # Mock TripAdvisor
        with open("tests/fixtures/tripadvisor_restaurant_page.html", "r", encoding="utf-8") as f:
            m.get("https://www.tripadvisor.com/Restaurant_Review-test", text=f.read())
        
        # Mock Yelp
        with open("tests/fixtures/yelp_restaurant_page.html", "r", encoding="utf-8") as f:
            m.get("https://www.yelp.com/biz/test", text=f.read())
        
        # Mock Google
        with open("tests/fixtures/google_restaurant_page.html", "r", encoding="utf-8") as f:
            m.get("https://www.google.com/maps/place/test", text=f.read())
        
        # Create test config with mocked URLs
        test_config = {
            "restaurant_name": "Test Restaurant",
            "tripadvisor_url": "https://www.tripadvisor.com/Restaurant_Review-test",
            "yelp_url": "https://www.yelp.com/biz/test",
            "google_url": "https://www.google.com/maps/place/test",
            "date_range": {
                "start": "2024-01-01",
                "end": "2025-12-31"
            },
            "csv_file_path": "tests/output/test_reviews.csv",
            # Other config settings...
        }
        
        # Run the scraper with test config
        main.run_scraper(test_config)
        
        # Verify CSV was created
        assert os.path.exists("tests/output/test_reviews.csv")
        
        # Verify CSV contains expected data
        df = pd.read_csv("tests/output/test_reviews.csv")
        assert len(df) > 0
        assert "Platform" in df.columns
        assert "Restaurant Name" in df.columns
        assert "Text" in df.columns
        
        # Verify data from all platforms is present
        platforms = df["Platform"].unique()
        assert "tripadvisor" in platforms
        assert "yelp" in platforms
        assert "google" in platforms
```

### Real-World End-to-End Tests

These tests should be used cautiously and with proper rate limiting.

```python
# tests/e2e/test_real_world.py

@pytest.mark.realworld  # Mark to exclude from regular test runs
def test_single_platform_real_scraping():
    # This test runs against actual websites - use with caution
    # Only run with explicit approval and proper rate limiting
    
    # Create minimal config with very restrictive limits
    test_config = {
        "restaurant_name": "Test Restaurant",
        "tripadvisor_url": "https://www.tripadvisor.com/Restaurant_Review-g54171-d436679-Reviews-Bowens_Island_Restaurant-Charleston_South_Carolina.html",
        "date_range": {
            "start": "2024-01-01",
            "end": "2025-12-31"
        },
        "scraping_settings": {
            "max_reviews_per_platform": 2,  # Very low limit for testing
            "platforms": ["tripadvisor"]    # Only test one platform
        },
        "anti_bot_settings": {
            "enable_random_delays": true,
            "delay_base_values": {
                "click": 2.0,       # Longer delays for real sites
                "scroll": 3.0,
                "navigation": 5.0,
                "typing": 0.5
            }
        },
        "csv_file_path": "tests/output/real_test_reviews.csv"
    }
    
    # Run the scraper with minimal real-world config
    main.run_scraper(test_config)
    
    # Verify CSV was created
    assert os.path.exists("tests/output/real_test_reviews.csv")
    
    # Verify CSV contains expected data
    df = pd.read_csv("tests/output/real_test_reviews.csv")
    assert len(df) > 0
    assert len(df) <= 2  # Should respect max_reviews_per_platform
    assert df["Platform"].iloc[0] == "tripadvisor"
```

## Validation Tests

Validation tests verify the accuracy and quality of the extracted data.

### Data Quality Validation

```python
# tests/validation/test_data_quality.py

def test_review_completeness():
    # Load a sample CSV output
    df = pd.read_csv("tests/fixtures/sample_reviews.csv")
    
    # Check for completeness
    missing_values = df.isnull().sum()
    
    # Critical fields should never be null
    assert missing_values["Platform"] == 0
    assert missing_values["Restaurant Name"] == 0
    assert missing_values["Rating"] == 0
    
    # Text can occasionally be missing (some platforms allow ratingonly reviews)
    assert missing_values["Text"] / len(df) < 0.1  # Less than 10% missing
    
    # Check data types
    assert pd.api.types.is_numeric_dtype(df["Rating"])
    assert pd.api.types.is_string_dtype(df["Text"])
    assert pd.api.types.is_string_dtype(df["Standardized Date"])

def test_date_standardization():
    # Load sample data
    df = pd.read_csv("tests/fixtures/sample_reviews.csv")
    
    # Verify all standardized dates follow YYYY-MM-DD format
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'
    
    for date in df["Standardized Date"]:
        assert re.match(date_pattern, date) is not None
    
    # Verify dates are within configured range
    min_date = pd.to_datetime("2024-01-01")
    max_date = pd.to_datetime("2025-12-31")
    
    dates = pd.to_datetime(df["Standardized Date"])
    assert (dates >= min_date).all() and (dates <= max_date).all()
```

### Known Data Validation

```python
# tests/validation/test_known_data.py

def test_against_known_reviews():
    # This test compares scraped data against manually collected reviews
    
    # Load scraped data
    scraped_df = pd.read_csv("tests/output/test_reviews.csv")
    
    # Load known good data (manually validated)
    known_df = pd.read_csv("tests/fixtures/known_good_reviews.csv")
    
    # Join the datasets on common fields
    merged = pd.merge(
        scraped_df,
        known_df,
        on=["Platform", "Reviewer Name", "Date"],
        suffixes=("_scraped", "_known")
    )
    
    # Check if ratings match
    rating_accuracy = (merged["Rating_scraped"] == merged["Rating_known"]).mean()
    assert rating_accuracy >= 0.95  # At least 95% match
    
    # Check text similarity (considering minor formatting differences)
    def text_similarity(row):
        return difflib.SequenceMatcher(
            None,
            row["Text_scraped"].lower(),
            row["Text_known"].lower()
        ).ratio()
    
    similarity_scores = merged.apply(text_similarity, axis=1)
    assert similarity_scores.mean() >= 0.9  # At least 90% similarity
```

## Performance Tests

Performance tests evaluate the speed and resource usage of the scraper.

```python
# tests/performance/test_scraper_performance.py

def test_memory_usage():
    # Test memory usage during scraping
    config = config_utils.load_config("tests/fixtures/performance_test_config.yaml")
    
    # Track memory before and after
    mem_before = psutil.Process().memory_info().rss / 1024 / 1024  # MB
    
    # Run with mock data to isolate performance of our code
    with requests_mock.Mocker() as m:
        # Setup mocks for external requests
        # ... (same as in E2E tests)
        
        # Run scraper
        main.run_scraper(config)
    
    mem_after = psutil.Process().memory_info().rss / 1024 / 1024  # MB
    mem_increase = mem_after - mem_before
    
    # Memory increase should be reasonable
    assert mem_increase < 200  # Less than 200MB increase

def test_execution_time():
    # Test execution time
    config = config_utils.load_config("tests/fixtures/performance_test_config.yaml")
    
    # Setup mocks
    with requests_mock.Mocker() as m:
        # ... (same as in E2E tests)
        
        # Time execution
        start_time = time.time()
        main.run_scraper(config)
        end_time = time.time()
    
    execution_time = end_time - start_time
    
    # Execution should be reasonably fast with mocks
    assert execution_time < 60  # Less than 60 seconds
```

## Anti-Detection Tests

Tests that verify the effectiveness of anti-bot detection measures.

```python
# tests/anti_bot/test_detection_evasion.py

def test_webdriver_detection():
    # Test if webdriver is properly hidden
    config = {"anti_bot_settings": {"enable_stealth_plugins": True}}
    browser = setup_browser(config)
    page = await browser.newPage()
    
    # Check if webdriver is detectable
    is_webdriver_detectable = await page.evaluate('''
        () => {
            return (
                navigator.webdriver ||
                navigator.languages.length === 0 ||
                navigator.plugins.length === 0
            )
        }
    ''')
    
    assert not is_webdriver_detectable
    await browser.close()

def test_bot_detection_sites():
    # Test against known bot detection services
    # Be cautious with these tests as they may lead to IP blocking
    
    @pytest.mark.parametrize("detection_url", [
        "https://bot.sannysoft.com/",
        "https://abrahamjuliot.github.io/creepjs/",
        # Add other detection sites
    ])
    @pytest.mark.realworld
    def test_detection_site(detection_url):
        config = {"anti_bot_settings": {"enable_stealth_plugins": True}}
        browser = setup_browser(config)
        page = await browser.newPage()
        
        # Visit bot detection site
        await page.goto(detection_url)
        
        # Take screenshot for manual verification
        await page.screenshot({'path': f'tests/output/bot_test_{detection_url.replace("https://", "").replace("/", "_")}.png'})
        
        # For some sites, we can programmatically check results
        if "bot.sannysoft.com" in detection_url:
            # Check specific elements that indicate bot detection
            failed_tests = await page.evaluate('''
                () => {
                    const failedElements = document.querySelectorAll('.failed');
                    return failedElements.length;
                }
            ''')
            
            # Should have minimal failed tests
            assert failed_tests <= 2  # Allow up to 2 failures
        
        await browser.close()
```

## Test Fixtures

The `tests/fixtures` directory contains:

1. Sample HTML files for each platform
2. Sample configuration files
3. Known good review data for validation
4. Mock browser and page objects

## Test Run Configuration

The `pytest.ini` file configures test execution:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Mark categories
markers =
    unit: Unit tests
    integration: Integration tests
    site_specific: Site-specific tests
    e2e: End-to-end tests
    validation: Validation tests
    performance: Performance tests
    anti_bot: Anti-bot detection tests
    realworld: Tests that run against real websites (use with caution)

# Exclude realworld tests by default
addopts = -v -m "not realworld"
```

## Automated Testing

A GitHub Actions workflow automates testing:

```yaml
# .github/workflows/tests.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest tests/unit tests/integration tests/site_specific
```

## Manual Testing Checklist

Before major releases, perform these manual checks:

1. **Configuration Verification**:
   - Test with various configuration options
   - Verify command-line arguments override configuration

2. **Real-World Platform Tests**:
   - Manually verify scraping works on current versions of each platform
   - Check for any changes in site structure

3. **Anti-Bot Detection**:
   - Run against bot detection test sites
   - Test with headless and non-headless mode

4. **Multi-Client Setup**:
   - Test with multiple clients configured
   - Verify client-specific settings work correctly

5. **Error Handling**:
   - Test with deliberately incorrect URLs
   - Verify proxy error handling works

## Related Components

- [Scraper Design](scraper_design.md)
- [Data Processing](data_processing.md)
- [Anti-Bot Measures](anti_bot_measures.md)
- [Proxy Management](proxy_management.md)
