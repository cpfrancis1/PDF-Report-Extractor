[Back to Main Portfolio](../README.md)

# PDF Report Extractor

## Overview
The aim of this project was to find an alternative solution for the bulk extraction of PDF reports from Fulcrum repositories. This feature is locked behind a paywall within the platform. In this particular use case, Fulcrum is employed for recording asset survey information for utility companies, enabling technicians to gather data efficiently and accurately.

The script utilises the `requests` library to make HTTP requests and `BeautifulSoup` for parsing the HTML page to fetch the authenticity token.

Here's a brief video illutstrate the PDF extraction:

[![Video Title](https://img.youtube.com/vi/hb6MUKrPKZM/0.jpg)](https://www.youtube.com/watch?v=hb6MUKrPKZM)

Check this video where I 20x the extraction speed using the `asyncio` library:

[![Video Title](https://img.youtube.com/vi/H4v4M2DiXFU/0.jpg)](https://www.youtube.com/watch?v=H4v4M2DiXFU)

Follow this link to see how the reports look:

[![Fulcrum Report](https://github.com/cpfrancis1/Screenshots/blob/main/Fulcrum_sample_report.png?raw=true)](https://github.com/cpfrancis1/Screenshots/blob/main/Fulcrum_sample_report.png?raw=true)




## Tools Used
- Fulcrum Field Data Capture Platform
- Python
    - Requests
    - BeautifulSoup
    - Asyncio
    - Aiohttp
- Chrome DevTools
- Git

## How it Works
**1. Importing Libraries**
- We begin by importing essential Python libraries required for our script's functionality.

```python
import pandas as pd
from bs4 import BeautifulSoup
import re
import asyncio
import time
import aiohttp
import datetime
import random
import os
```

**2. Fetching CSRF Token**
- Before authenticating the user, we need to obtain the CSRF token from the login page.
- The get_csrf_token function fetches the login HTML, parses it using BeautifulSoup, and extracts the CSRF token value.

```python
async def get_csrf_token(login_url, session):
    # Fetch login HTML
    async with session.get(login_url) as response:
        response.raise_for_status()

        # Load the HTML into the Beautiful Soup library for parsing
        soup = BeautifulSoup(await response.text(), 'lxml')

        # Parse the HTML for the "csrf-token" tag and return its value
        csrf_token = soup.select_one('meta[name="csrf-token"]')['content']

    return csrf_token
```

**3. Authentication**
- After obtaining the CSRF token, we proceed to authenticate the user.
- The login function takes the user's email, password, and CSRF token as parameters, and constructs a payload for authentication.

```python
async def login(email, password, csrf_token, login_url, session):
    # Construct the payload
    payload = {
        'user[email]': email,
        'user[password]': password,
        'authenticity_token': csrf_token
    }

    # Authenticate to Fulcrum
    async with session.post(login_url, data=payload, allow_redirects=True) as response:
        if response.status == 200 or response.status == 302:
            print("Login successful")
            return response
        else:
            print(f"Login failed with status code {response.status}.")
            return None

```

**4. Creating a New Folder**
- To keep the downloaded files organised, we create a new folder for saving the PDF reports.
- The generate_folder_name function generates a unique folder name based on the current date and time.

```python
def generate_folder_name():
    # Get the current date and time in the desired format
    current_datetime = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

    # Generate a random number between 1 and 1000
    random_number = random.randint(1, 1000)

    # Create the folder name
    folder_name = f"Reports_{current_datetime}_{random_number}"

    return folder_name
```

**5. Cleaning Filenames**
- Filenames for downloaded reports need to be cleaned to ensure they are valid.
- The clean_filename function appends a report count for uniqueness and substitutes illegal characters with underscores.

```python
def clean_filename(record_name, report_count):
    # Append report count for filename uniqueness
    filename = f"{record_name}_{report_count}"

    # Substitute illegal characters with an underscore "_"
    cleaned_filename = re.sub('[^a-zA-Z0-9 \n\.]', "_", filename)

    return f"{cleaned_filename}.pdf"
```

**6. Downloading Reports**
- I use asynchronous tasks to download PDF reports.
- The download_report function handles downloading a report given its record ID, filename, and session.

```python
 async def download_report(record_id, filename, folder_name, session):
    url = f"https://web.fulcrumapp.com/reports/generate?report%5Brecord_id%5D={record_id}"
    async with session.get(url, allow_redirects=True) as response:
        if response.status == 200:
            with open(f"{folder_name}/{filename}", 'wb') as file:
                file.write(await response.read())
            print(f"PDF with filename {filename} Successfully extracted!")
        else:
            print(f"*FAILED* PDF with filename {filename} extraction failed!")
```

**7. Main Function**
- The main function orchestrates the entire process.
- It authenticates the user, reads data from an Excel file, generates a folder for saving reports, and initiates report downloads.

```python
 async def main(username, password, list_directory, login_url):
    # ... (code for authentication, data loading, folder creation, and report downloading)
```

## Value Generated

- **Time Savings**: This python script automates the PDF report extraction process, lowering the time spent on manual data extraction. This efficiency frees up time for other tasks. For Example, for 50 records, the manual process of extracting and renaming the reports would have taken 30 minutes, now it only takes 2 minutes in the background. **Update** After adding the `asyncio` functionality, the download time has been further significantly reduced, what use to take 2 minutes now takes 10 seconds.  

- **Data Accuracy**: Automated extraction ensures no document is missed and ensures proper naming conventions are followed without reduced risk of error associated with manual extraction. 
  
## Challenges and Learning
**Authentication**: Initially, I had to tackle the challenge of programmatically authenticating with Fulcrum. To achieve this, I used Chrome DevTools to inspect network activity during the login process. This analysis helped me understand the data sent in the HTTP Post payload for authentication. I discovered the necessity of a security token, which I located within the login page's HTML using Chrome DevTools' search function.

**Token Retrieval**: This program sends a HTTP GET request to Fulcrum's login page to retrieve the HTML. I then parse the HTML for the authenticity token tag using the `BeautifulSoup` library, it's worth noting that achieving the same result with the `re` (Regular Expressions) library was also feasible.

**Filename Uniqueness**: Another challenge arose when dealing with occasional multiple records sharing the same address. To prevent filename conflicts and overwriting, I appended a unique number to each filename.

**Web Scraping**: This experience provided valuable hands-on exposure to web scraping, automating web login processes, and a deeper understanding of web authentication mechanisms.

**Asyncronous Download**: In a later enhancement, I have implemented `asyncio` to perform GET requests for reports asynchronously. This improvement significantly enhances the script's speed. I have also set a limit of 20 concurrent requests to prevent overloading the Fulcrum servers with excessive requests.

## Future Improvements
- Implement better error handling.
- Create a Chrome plugin that adds Fulcrum functionality directly to your browser.
