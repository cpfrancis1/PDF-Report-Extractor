import pandas as pd
from bs4 import BeautifulSoup
import re
import asyncio
import time
import aiohttp
import datetime
import random
import os

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
            print("Login successful with redirection.")
            return response
        else:
            print(f"Login failed with status code {response.status}.")
            return None

async def get_csrf_token(login_url, session):
    # Fetch login HTML
    async with session.get(login_url) as response:
        response.raise_for_status()

        # Load the HTML into the Beautiful Soup library for parsing
        soup = BeautifulSoup(await response.text(), 'lxml')

        # Parse the HTML for the "csrf-token" tag and return its value
        csrf_token = soup.select_one('meta[name="csrf-token"]')['content']

    return csrf_token

def clean_filename(record_name, report_count):
    # Append report count for filename uniqueness
    filename = f"{record_name}_{report_count}"

    # Substitute illegal characters with an underscore "_"
    cleaned_filename = re.sub('[^a-zA-Z0-9 \n\.]', "_", filename)

    return f"{cleaned_filename}.pdf"

async def download_report(record_id, filename, folder_name, session):
    url = f"https://web.fulcrumapp.com/reports/generate?report%5Brecord_id%5D={record_id}"
    async with session.get(url, allow_redirects=True) as response:
        if response.status == 200:
            with open(f"{folder_name}/{filename}", 'wb') as file:
                file.write(await response.read())
            print(f"PDF with filename {filename} Successfully extracted!")
        else:
            print(f"*FAILED* PDF with filename {filename} extraction failed!")

def generate_folder_name():
     # Get the current date and time in the desired format
    current_datetime = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

    # Generate a random number between 1 and 1000
    random_number = random.randint(1, 1000)

    # Create the folder name
    folder_name = f"Reports_{current_datetime}_{random_number}"

    return folder_name

async def main(username, password, list_directory, login_url):
    async with aiohttp.ClientSession() as session:
        csrf_token = await get_csrf_token(login_url, session)

        # Authenticate using aiohttp
        login_response = await login(username, password, csrf_token, login_url, session)

        if login_response.status == 200:
            print("Login successful")
        else:
            print(f"Login failed with status code {login_response.status}")
            return  # Exit the function if login fails

        record_data = pd.read_excel(list_directory, sheet_name=0)

        # Declare a list of records to download
        record_ids = record_data['_record_id'].tolist()
        record_names = record_data['address'].tolist()

        #Declare Folder Name
        folder_name = generate_folder_name()
        
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)

        # Initialize a counter for filename uniqueness
        report_count = 1
        print("Start reports download")

        tasks = []

        #start a timer to see how long the download takes
        download_start_time = time.time()

        # Loop through records and initiate download tasks asynchronously
        for record_id, record_name in zip(record_ids, record_names):
            filename = clean_filename(record_name, report_count)

            # Capture the start time before starting the download task
            start_time = time.strftime("%H:%M:%S")
            # print(f"Start downloading report for report: {record_name}, at {start_time}")

            task = download_report(record_id, filename, folder_name, session)
            tasks.append(task)

            # Increment the counter for each report for filename uniqueness
            report_count += 1

        await asyncio.gather(*tasks)

        print(f"Download Complete. {len(record_ids)} reports downloaded.")
        print(f"Total download time: {round(time.time() - download_start_time)} seconds")

if __name__ == "__main__":
    USERNAME = 'ENTER USERNAME HERE'
    PASSWORD = 'ENTER PASSWORD HERE'
    LIST_DIRECTORY = 'ENTER DIRECTORY HERE'
    LOGIN_URL = 'https://web.fulcrumapp.com/users/sign_in'
    main(USERNAME, PASSWORD, LIST_DIRECTORY, LOGIN_URL)
    
    asyncio.run(main(USERNAME, PASSWORD, LIST_DIRECTORY, LOGIN_URL))
