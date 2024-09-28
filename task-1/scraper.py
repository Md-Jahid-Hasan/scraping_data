import csv
import json
import asyncio
import os

import requests
import aiohttp


class Scraper:
    login_url = "https://app.cosmosid.com/api/v1/login"
    folder_url = "https://app.cosmosid.com/api/metagenid/v3/users/60ea9ada-383f-4f6a-a4ae-8e8269df6c23/structure?limit=-1"
    sample_data_url = "https://app.cosmosid.com/api/search/v1/search"
    file_location = "credentials.json"
    headers = {
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    }

    def __init__(self):
        """authorization_token is the hash format of credentials. Endpoint don't accept the user credential
        It only accepts the hash format of credentials."""
        self.authorization_token = "ZGVtb19lc3RlZTJAY29zbW9zaWQuY29tOnh5emZnMzIx"
        with open(self.file_location, "r") as file:
            self.file_data = json.load(file)

        # If access token is already generated collecting it from the credentials.py file
        if not self.file_data.get('token'):
            self.token = self.generate_token()
            self.file_data['token'] = self.token
            with open(self.file_location, "w") as file:
                json.dump(self.file_data, file, indent=4)
        else:
            self.token = self.file_data['token']

        self.headers['x-token'] = self.token
        if self.token == "":
            print("Invalid token is generated, something went wrong")
        else:
            # get folder information
            self.folder_information = self.get_folder_data()

            # parsing each folder and download data for each sample
            asyncio.run(self.parsing_folder())

        file.close()

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

        # iterate over all sample and generate analysis id for each sample then asynchronously call get_table_data
        # function for retrieve data
        try:
            for key in all_sample:
                tasks = []
                async with aiohttp.ClientSession() as session:
                    for data in all_sample[key]:
                        try:
                            result_ids = self.generate_analysis_id(data['uuid'])
                            for each_result_id in result_ids:
                                print(f"getting data of {folder['title']}/{data['sample_name']}/{each_result_id['name']}")
                                # calling function for retrieve data
                                tasks.append(asyncio.create_task(
                                    self.get_table_data(session, data['uuid'], each_result_id['id'], key,
                                                        data['sample_name'], each_result_id['name'])))
                        except Exception as e:
                            print(f"Failed to get data because: {e}")
                    await asyncio.gather(*tasks)
        except Exception as e:
            print(f"Failed to generate analysis id or get main data: {e}")

    async def get_table_data(self, session, sample_data_id: str, result_id: str, folder: str, sample_name: str,
                             result_name: str):
        """This retrieve downloadable data by api call and pass to other method for download data in csv file
            :param session: aiohttp session
            :param sample_data_id: data id for sample
            :param result_id: data id for result/category
            :param folder: folder id for save data in correct ordering
            :param sample_name: sample name for save data in correct ordering
            :param result_name: result name for save data in correct ordering and api call
        """
        # update api for each result name as different for different result
        if result_name == 'virulence-factors' or result_name == "antibiotic-resistance":
            post_tag = "phylogeny"
        elif result_name == "bacteria":
            post_tag = "biom"
        else:
            post_tag = "taxonomy"

        data_url = f"https://app.cosmosid.com/api/metagenid/v1/files/{sample_data_id}/analysis/{result_id}/{post_tag}?artifact_version=2&filter=filtered"

        print(f"getting data of {folder}/{sample_name}/{result_name}")
        try:
            async with session.get(data_url, headers=self.headers) as response:
                # calling api and pass response data to other method for prepare and download
                if response.status == 200:
                    response_json = await response.json()
                    # as taxonomy of bacteria has different data format call a different method for download
                    if result_name == "bacteria":
                        data = self.prepare_table_data_for_bacteria(response_json, folder, sample_name)
                    else:
                        # other result/category have same data format call two different method call for prepare/mapped data
                        # and other method for download those data as CSV
                        analysis_data = response_json['analysis']
                        analysis_data = analysis_data if analysis_data.get("children", False) else []
                        data = self.prepare_table_data(analysis_data, [])
                        self.download_data(data, folder, sample_name, result_name)
        except Exception as e:
            print(f"Failed to get main data in get_table_data method because: {e}")

    def download_data(self, data: list, folder: str, sample_name: str, result_name: str):
        """Modify and save data as csv. all data except bacteria type are saved in this method
            :param data: list of data
            :param folder: folder name for save data in correct ordering
            :param sample_name: sample name for save data in correct ordering
            :param result_name: result name for save data in correct ordering
        """
        print(f"saving data of {folder}/{sample_name}/{result_name} -> {len(data)}")
        all_data = [['name', 'tax_id', 'relative_abundance', 'abundance_score', 'total_matches', 'unique_matches',
                     'unique_matches_frequency']]
        if result_name == 'virulence-factors' or result_name == "antibiotic-resistance":
            all_data[0].insert(2, 'class')
            all_data[0][1] = 'accession_id'

        # format data for saving as csv
        try:
            for row in data:
                if not bool(row):
                    continue
                relative_abundance = round(row['relative_abundance'] * 100, 2)
                abundance_score = round(row['abundance_score'] * 100, 2)
                total_matches = round(row['total_stats']['percent_unique_hits'] * 100, 2)
                unique_matches = round(row['node_stats']['percent_unique_hits'] * 100, 2)
                unique_matches_frequency = row['node_stats']['total_hits']
                name = row['taxonomy']['name'] if row['taxonomy'].get('name', False) else row['title']
                tax_id = row['taxonomy'].get("tax_id", "")

                row_data = [name, tax_id, relative_abundance, abundance_score, total_matches, unique_matches,
                            unique_matches_frequency]
                if result_name == 'virulence-factors' or result_name == "antibiotic-resistance":
                    row_data.insert(2, '-')
                all_data.append(row_data)
        except Exception as e:
            print(f"Failed to format data for downloading inside download_data, because: {e}")

        try:
            directory = f"{folder}/{sample_name}"
            file_name = f"{result_name}.csv"
            filepath = os.path.join(directory, file_name)
            os.makedirs(directory, exist_ok=True)
            with open(filepath, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerows(all_data)
        except Exception as e:
            print(f"Failed to save data for {filepath} because: {e}")

    def prepare_table_data_for_bacteria(self, response, folder, sample_name):
        """This method only prepare and download bacteria and its taxonomy data as csv
        :param response: response data from api
        :param folder: folder name for save data in correct ordering
        :param sample_name: sample name for save data in correct ordering
        """
        data = response.get('data')
        rows = response.get('rows')
        columns = response.get('columns')

        table_data = {}
        # map the value into dictionary from 2D list
        value_mapping = self.map_data(data, columns)

        # iterate over each data and calculate each data by accessing value from dict and prepare each taxonomy
        try:
            for _, row in enumerate(rows):
                for sample in row['metadata']['lineage']:
                    # table_data[sample['rank']] = table_data.get(sample['rank'], []).append()
                    if sample['rank'] == 'no rank':
                        continue

                    x = table_data.get(sample['rank'], [])

                    is_new = True
                    for i, item in enumerate(x):
                        # if data already exist then add new value to it
                        if item.get("name") == sample['name']:
                            item['relative_abundance'] = item.get("relative_abundance", 0) + value_mapping[_][
                                'relative_abundance']
                            item['abundance_score'] = item.get("abundance_score", 0) + value_mapping[_]['abundance_score']
                            item['hit_frequency'] = item.get("hit_frequency", 0) + value_mapping[_]['hit_frequency']
                            x[i] = item
                            is_new = False
                    else:
                        # if data not exist then assign it
                        if is_new or not x:
                            item = {
                                "name": sample['name'], "tax_id": sample['tax_id'],
                                "relative_abundance": round(value_mapping[_]['relative_abundance']*100, 2),
                                "abundance_score": round(value_mapping[_]['abundance_score']),
                                "hit_frequency": value_mapping[_]['hit_frequency']
                            }
                            x.append(item)

                    table_data[sample['rank']] = x
        except Exception as e:
            print(f"Failed to prepare data for bacteria because {e}")

        # save the final Data
        for key in table_data:
            try:
                print(f"Saving data in {folder}/{sample_name}/bacteria/{key}.csv")
                directory = f"{folder}/{sample_name}/bacteria/"
                file_name = f"{key}.csv"
                filepath = os.path.join(directory, file_name)
                os.makedirs(directory, exist_ok=True)
                with open(filepath, mode='w', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=table_data[key][0].keys())
                    writer.writeheader()
                    writer.writerows(table_data[key])
            except Exception as e:
                print(f"Failed to download data as csv for bacteria - {key} because: {e}")
        return table_data

    def map_data(self, data, columns) -> list[dict]:
        """Map 2d list into dict against column name for easier access
        :param data: 2d list
        :param columns: column name
        :return: list of column value(dict)
        """
        value_mapping = []
        try:
            for d in data:
                if len(value_mapping) > d[0]:
                    x = value_mapping[d[0]]
                    x[columns[d[1]]['id']] = d[2]
                    value_mapping[d[0]] = x
                else:
                    x = {columns[d[1]]['id']: d[2]}
                    value_mapping.append(x)
        except Exception as e:
            print(f"Failed to map data in map_data method, because - {e}")
        return value_mapping

    def prepare_table_data(self, data, result) -> list[dict]:
        """recursively get the dict where dict has no children key. This is the final dict where main data exists
        :param data: response data as dict
        :param result: a list that is used as result and append final data here
        :return list of final data as dict
        """
        if 'children' not in data:
            result.append(data)
        else:
            for x in data['children']:
                self.prepare_table_data(x, result)
        return result

    def generate_analysis_id(self, data_id: str) -> list:
        """Generate analysis token and with this token generate all id for a specific sample
        :param data_id: sample id
        :return: list of result/category id mapped with mapped in name
        """
        analysis_token = None
        try:
            # generate analysis token
            analysis_token_url = f"https://app.cosmosid.com/api/metagenid/v1/files/{data_id}/runs"
            response = requests.get(analysis_token_url, headers=self.headers)
            if response.status_code == 200:
                response_json = response.json()
                analysis_token = response_json['runs'][0]['id']
        except Exception as e:
            print(f"Failed to generate analysis id because: {e}")

        # with this token generate analysis id and id only mapped with name
        results_ids = []
        if analysis_token:
            try:
                results_id_url = f"https://app.cosmosid.com/api/metagenid/v1/runs/{analysis_token}/analysis"
                response = requests.get(results_id_url, headers=self.headers)
                if response.status_code == 200:
                    response_json = response.json()
                    for data in response_json['analysis']:
                        results_ids.append({"id": data['id'], "name": data['database']['name']})
            except Exception as e:
                print(f"Failed to generate result id because: {e}")

        return results_ids

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

Scraper()