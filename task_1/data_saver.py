# This is a abstract class for DataSaver. It has a method save_file which is not implemented.
class DataSaver:
    def save_file(self, folder, sample_name, result_name, all_data):
        raise NotImplementedError("This method should be implemented in a child class")

    def save_bacteria_data(self, folder, sample_name, table_data, key):
        raise NotImplementedError("This method should be implemented in a child class")