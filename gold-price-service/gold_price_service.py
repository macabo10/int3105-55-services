import requests
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import os

# API URL
url = "http://giavang.doji.vn/api/giavang/?api_key=258fbd2a72ce8481089d88c678e9fe4f"
xml_file_path = "./gold_price.xml"

def fetch_from_api():
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.text.lstrip('\ufeff')
        lines = data.splitlines()
        data = "\n".join(lines[2:])

        try:
            root = ET.fromstring(data)
            # Ensure the directory exists
            os.makedirs(os.path.dirname(xml_file_path), exist_ok=True)
            with open(xml_file_path, "wb") as f:
                f.write(ET.tostring(root))
            return root
        except ET.ParseError as e:
            print(f"Failed to parse XML: {e}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def get_data_from_file():
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        igp = root.find("IGPList")
        date_time_str = igp.find('DateTime').text
        date_time = datetime.strptime(date_time_str, "%d/%m/%Y %I:%M:%S %p")

        current_time = datetime.now()
        if current_time - date_time > timedelta(hours=1):
            return fetch_from_api()
        else:
            return root
    except FileNotFoundError:
        return fetch_from_api()
    except ET.ParseError as e:
        print(f"Failed to parse XML: {e}")
        return None

def get_gold_price(gold_type):
    data = get_data_from_file()
    if data is None:
        print("Data not available.")
        return None

    jewelry_list = data.find("JewelryList")
    for child in jewelry_list.findall('Row'):
        if child.attrib["Key"] == gold_type:
            return child.attrib["Buy"]

    return None