# Web Scraper for Extracting Data from a Specific Source
This project is a Python-based web scraper designed to extract data from a specific source and organize it into designated 
folders. Follow the instructions below to set up and run the project on your system.

# Project Setup
## Prerequisites
1. Python 3, pip, and virtualenv must be installed on your system.

2. Create a virtual environment and activate it:<br>
      Create a virtual environment - 
    ```
    virtualenv venv
    ```
    Activate the virtual environment - <br>
   for ubuntu
    ```
    source venv/bin/activate
    ```
    for windows
    ```
    venv\Scripts\activate
    ```
3. Install the required dependencies by running the following command:
   ```
   pip install -r requirements.txt
   ```
4. Ensure you are in the correct directory and execute the scraper script:

   for ubuntu
   ```
   python3 scraper.py
   ```
   for windows
    ```
   python scraper.py
   ```
   

## Downloading Data
The scraper downloads and organizes data into specific folders named L-ear, L-elb, R-ear, and R-elb. These folders 
contain the data that the scraper collects.
   * Folder Structure: If the folders are already present in your directory, the scraper will replace the data. 
   However, if you'd like to see how the scraper works and downloads the data, 
   you can delete these folders before running the script.


### Additional Information
* Ensure that your internet connection is stable to avoid interruptions while the scraper downloads data.