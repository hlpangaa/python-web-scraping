# Flight Price Alert

## Application Workflow
- Programed to harvest flight price data from [Experdia](www.expedia.com.hk) and [Skyscanner](www.skyscanner.com.hk) using Beautiful soup and Selenium, scheduled to run daily with Macbook's built-in job automater.
- Cleaned, normalized, and transformed the raw data into usable information in Pandas and Numpy, designed a alert trigger when the expected price is hitted.

## Requirements
* Python >= 3.1
* Python Libraries: `bs4` `requests` `re` `selenium` `urllib` `datetime` `json` `pyshorteners` `pandas` `numpy` `os` `time`
