# Flight Price Alert

## Application Workflow
- Programed to harvest flight price data from [Experdia](www.expedia.com.hk) and [Skyscanner](www.skyscanner.com.hk) using Beautiful soup and Selenium, scheduled to run daily with Macbook's built-in job automater.
- Cleaned, normalized, and transformed the raw data into usable information in Pandas and Numpy, designed a alert trigger when the expected price is hitted.

## Tech Stack
- Python
- Chrome Headless Webdriver
- Macbook Automator

## Automation in Macbook
- Search "Automator" in application, open it.

![screenshoot](https://raw.githubusercontent.com/hlpangaa/python-web-scraping/master/assets/0.png)

- Create a action from navigation bar in the left, utilities>Run Shell Scripts. 

- Type the script to run your python file and save as a application.

![screenshoot](https://raw.githubusercontent.com/hlpangaa/python-web-scraping/master/assets/1.png)

- Search "Login Items", it should be in your macbook setting. Create a login Items of your application that your created.

![screenshoot](https://raw.githubusercontent.com/hlpangaa/python-web-scraping/master/assets/2.png)

- Now you can run the script everytime you turn on your computer.

## Requirements
* Python >= 3.1
* Python Libraries: `bs4` `requests` `re` `selenium` `urllib` `datetime` `json` `pyshorteners` `pandas` `numpy` `os` `time`
