import json
import asyncio
import time

import requests
import aiohttp


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


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
        service = Service('chromedriver.exe')
        browser = webdriver.Chrome(service=service)
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

        for sample in all_sample:
            self.get_table_data(all_sample[sample])
            break

    def get_table_data(self, sample):
        for data in sample:
            print(data)
            browser = self.get_selenium_browser()
            url = f"https://app.cosmosid.com/samples/{data['uuid']}"
            browser.get("https://app.cosmosid.com/sign-in")
            browser.execute_script(f"window.localStorage.setItem('user', '{json.dumps(self.localstorage_value)}')")
            browser.get(url)
            browser.implicitly_wait(10)
            time.sleep(10)

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
