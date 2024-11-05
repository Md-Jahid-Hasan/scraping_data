import csv
import os
from data_saver import DataSaver


class DownloadFile(DataSaver):
    def __init__(self):
        self.initial_directory = ""

    def save_file(self, folder, sample_name, result_name, all_data):
        try:
            directory = f"{folder}/{sample_name}"
            if self.initial_directory:
                directory = os.path.join(self.initial_directory, directory)
            file_name = f"{result_name}.csv"
            filepath = os.path.join(directory, file_name)
            os.makedirs(directory, exist_ok=True)
            with open(filepath, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerows(all_data)
        except Exception as e:
            print(f"Failed to save data for {filepath} because: {e}")

    def save_bacteria_data(self, folder, sample_name, table_data, key):
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