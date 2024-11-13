import json
import asyncio
import time
import threading

import requests
import aiohttp

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from data_saver import DataSaver


class Scraper:
    login_url = "https://app.cosmosid.com/api/v1/login"
    folder_url = "https://app.cosmosid.com/api/metagenid/v3/users/60ea9ada-383f-4f6a-a4ae-8e8269df6c23/structure?limit=-1"
    sample_data_url = "https://app.cosmosid.com/api/search/v1/search"
    file_location = "credentials.json"
    localstorage_value = {}
    headers = {
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    }

    def __init__(self, data_saver: DataSaver):
        """authorization_token is the hash format of credentials. Endpoint don't accept the user credential
        It only accepts the hash format of credentials."""
        self.data_saver = data_saver
        self.authorization_token = "ZGVtb19lc3RlZTJAY29zbW9zaWQuY29tOnh5emZnMzIx"
        with open(self.file_location, "r") as file:
            self.file_data = json.load(file)

        # If access token is already generated collecting it from the credentials.py file
        # if not self.file_data.get('token'):
        self.token = self.generate_token()
        # self.file_data['token'] = self.token
        # with open(self.file_location, "w") as file:
        #     json.dump(self.file_data, file, indent=4)
        # else:
        #     self.token = self.file_data['token']

        self.headers['x-token'] = self.token
        if self.token == "":
            print("Invalid token is generated, something went wrong")
        else:
            # get folder information
            self.folder_information = self.get_folder_data()
            print(self.folder_information)
            # parsing each folder and download data for each sample
            asyncio.run(self.parsing_folder())

        file.close()

    def get_selenium_browser(self):
        options = Options()
        # options.add_argument('--headless')
        options.add_argument("user-data-dir=/var/www/python_proj_personal/scraping_data/task_1/profile")
        options.add_experimental_option("prefs", {
            "profile.managed_default_content_settings.images": 2,  # Disable images
            "profile.managed_default_content_settings.stylesheets": 2,  # Disable CSS
            # "profile.managed_default_content_settings.javascript": 2  # Disable JS (if not required)
        })

        service = Service('/var/www/python_proj/chromedriver')
        browser = webdriver.Chrome(options=options, service=service)
        browser.get("https://app.cosmosid.com/sign-in")
        browser.execute_script(f"window.localStorage.setItem('user', '{json.dumps(self.localstorage_value)}')")
        return browser

    async def parsing_folder(self):
        """Asynchronously run api for collection all sample information. After collecting sample information, with
           sample id generate analysis id and pass those ids to get_table_data function for collecting and download main
           data.
        """
        all_sample = {}
        try:
            # collect all sample information and mapped it with folder title for save data in correct ordering
            async with aiohttp.ClientSession() as session:
                tasks = []
                for folder in self.folder_information:
                    # mapping with title
                    tasks.append((folder['title'], self.get_sample_data(session, folder['id'])))
                result = await asyncio.gather(*[task[1] for task in tasks])

                for _, folder_name in enumerate([task[0] for task in tasks]):
                    all_sample[folder_name] = result[_]
        except Exception as e:
            print(f"Failed to get and mapped sample data because: {e}")

        threads = []
        for sample in all_sample:
            # print(sample, len(all_sample[sample]))
            # t = threading.Thread(target=self.get_table_data, args=(all_sample[sample], sample))
            # threads.append(t)
            # t.start()
            self.get_table_data(all_sample[sample], sample)
            break

        # for thread in threads:
        #     thread.join()

    def get_table_data(self, sample, sample_name):
        # with concurrent.futures.ThreadPoolExecutor(15) as executor:
        browser = self.get_selenium_browser()

        for data in sample:
            try:
                print(data, sample_name)
                url = f"https://app.cosmosid.com/samples/{data['uuid']}"
                # browser.implicitly_wait(10)
                browser.get(url)

                content = WebDriverWait(browser, 20).until(
                    EC.presence_of_element_located((By.TAG_NAME, "table"))
                )

                self.load_data_page(browser)
            except Exception as e:
                print(f"Failed to get data for {data['uuid']} because: {e}")
                continue

    def load_data_page(self, browser):
        self.save_table_data(browser)

        container = browser.find_element(By.XPATH, '//*[@id="analysis-select"]').click()
        # container = browser.find_element(By.CSS_SELECTOR, "ul[aria-labelledby='analysis-select-label']")

        try:
            next_analysis = WebDriverWait(browser, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//ul[@aria-labelledby='analysis-select-label']//li[@tabindex='0']/following-sibling::li"))
            )
        except TimeoutException:
            print("No analysis left")
            next_analysis = None
        except Exception as e:
            print(f"No analysis left: {e}")
            next_analysis = None

        # next_analysis = container.find_element(By.XPATH, "//li[@tabindex='0']//following-sibling::li")
        # next_analysis = current_analysis.find_element(By.XPATH, "following-sibling::li")

        if next_analysis:
            next_analysis.click()
            content = WebDriverWait(browser, 20).until(
                EC.any_of(
                    EC.presence_of_element_located((By.TAG_NAME, "table")),
                    EC.text_to_be_present_in_element((By.TAG_NAME, "h2"), "No data to display")
                )
            )
            self.load_data_page(browser)

    def save_table_data(self, browser, results="backteria"):
        content = browser.page_source
        soup = BeautifulSoup(content, 'html.parser')
        data = self.prepare_table_data(soup)
        time.sleep(3)
        print(len(data))

        if len(data):
            button = browser.find_element(
                By.XPATH, '//*[@id="scrollable-force-tabpanel-0"]/div/div/div[3]/div/div/div/div[2]/span[2]/button')
            class_name = button.get_attribute("class")

            if "Mui-disabled" not in class_name.split():
                button.click()
                self.save_table_data(browser)

    def prepare_table_data(self, soup: BeautifulSoup):
        data = []
        table = soup.find('table')
        if not table:
            return data
        thead = table.find("thead").find_all("th")
        header = [th.text for th in thead]
        data.append(header)

        rows = table.find("tbody").find_all("tr")

        for row in rows:
            try:
                all_td = row.find_all("td")
                data.append([td.text for td in all_td])
            except:
                continue
        return data

    def generate_token(self) -> str:
        """Manually login user and generate a token for authorization here authorization_token is the hash format
            of credentials
            :return token
        """
        headers = {
            'accept': 'application/json, text/plain, */*',
            'authorization': f"Basic {self.authorization_token}",
            'content-type': 'application/json',
            'origin': 'https://app.cosmosid.com',
            'referer': 'https://app.cosmosid.com/sign-in',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
        }
        payload = json.dumps({
            "expiry": 86400,
            "login_from": "login_form",
            "totp": ""
        })
        token = ""
        try:
            response = requests.post(self.login_url, headers=headers, data=payload)
            print(f"Get response for token creation with status code {response.status_code}")
            if response.status_code == 200:
                json_response = response.json()
                self.localstorage_value = json_response
                token = json_response["token"]

            return token
        except Exception as e:
            print(f"Failed to generate token because: {e}")
            return ""

    def get_folder_data(self) -> list[dict]:
        """Get folder information and mapped it with id and title
        :return mapped folder data
        """
        folder_information = []
        try:
            response = requests.get(self.folder_url, headers=self.headers)

            if response.status_code == 200:
                print(f"Get response for folder information with status code {response.status_code}")
                response_data = response.json()
                for data in response_data:
                    folder_information.append({"id": data["id"], "title": data["title"]})
        except Exception as e:
            print(f"Failed to get folder information because: {e}")
        return folder_information

    async def get_sample_data(self, session, folder_id: str) -> list:
        """Generate all sample for specific folder
        :param session: aiohttp session
        :param folder_id: folder id
        :return sample data
        """
        payload = json.dumps({
            "text": "",
            "key_values": [
                {
                    "key": "folder_uuid",
                    "data_type": "text",
                    "value_variants": [
                        {
                            "value_type": "single",
                            "value": folder_id
                        }
                    ]
                }
            ],
            "order": "desc",
            "orderBy": "created",
            "limit": 200,
            "offset": 0
        })
        all_file_id = []

        try:
            async with session.post(self.sample_data_url, headers=self.headers, data=payload) as response:
                if response.status == 200:
                    files = await response.json()
                    for file in files['files']:
                        all_file_id.append({"uuid": file["file_uuid"], "sample_name": file['sample_name']})
                    return all_file_id
                else:
                    print(f"Failed to get response for id {folder_id}")
                    return []
        except Exception as e:
            print(f"Failed to get sample data for id {folder_id} because: {e}")
            return []
