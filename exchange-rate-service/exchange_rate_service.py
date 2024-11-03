import requests;
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import os

API = "https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx?b=10"

def get_exchange_rate(currency):    
    data = get_data()

    if data is None:
        return None
    
    for child in data.findall('Exrate'):
        if child.attrib["CurrencyCode"] == currency:
            return child.attrib["Transfer"]
        
    return None;


def fetch_data_from_api():
    print("Fetching data from API")
    response = requests.get(API);
    if response.status_code == 200:
        # Remove BOM if present
        data = response.text.lstrip('\ufeff')

        # Remove the first two lines
        lines = data.splitlines()
        data = "\n".join(lines[2:])

        try:
            root = ET.fromstring(data)
            
            current_dir = os.path.dirname(__file__)
            data_file_path = os.path.join(current_dir, "exchange_rate.xml")

            with open(data_file_path, "wb") as f:
                f.write(ET.tostring(root))
            return root
        except ET.ParseError as e:
            print(f"Failed to parse XML: {e}")
            return None
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return None
    
def get_data():
    try:
        current_dir = os.path.dirname(__file__)
        data_file_path = os.path.join(current_dir, "exchange_rate.xml")

        tree = ET.parse(data_file_path)
        root = tree.getroot()
        date_time_str = root.find('DateTime').text
        date_time = datetime.strptime(date_time_str, "%m/%d/%Y %I:%M:%S %p")

        current_time = datetime.now()
        if current_time - date_time > timedelta(hours=1):
            return fetch_data_from_api()
        else:
            return root
    except FileNotFoundError:
        return fetch_data_from_api()
    except ET.ParseError as e:
        print(f"Failed to parse XML: {e}")
        return None
    