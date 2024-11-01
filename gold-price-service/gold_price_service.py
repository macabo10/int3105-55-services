import requests
from datetime import datetime, timedelta
from flask import Flask, jsonify
import xml.etree.ElementTree as ET

# API URL
# url = "http://api.btmc.vn/api/BTMCAPI/getpricebtmc?key=3kd8ub1llcg9t45hnoh8hmn7t5kc2v"
url = "http://giavang.doji.vn/api/giavang/?api_key=258fbd2a72ce8481089d88c678e9fe4f"


def fetch_from_api():
    try:
        response = requests.get(url)
        response.raise_for_status()
        # response = response.json()
        data = response.text.lstrip('\ufeff')
        lines = data.splitlines()
        data = "\n".join(lines[2:])

        try:
            # parse the xml string (data) into an xml element tree
            root = ET.fromstring(data)
            # write that data into the gold_price.xml file
            with open("gold-price-service/gold_price.xml", "wb") as f:
                f.write(ET.tostring(root))
            return root
        except ET.ParseError as e:
            print(f"Failed to parse XML: {e}")
            return None

    except requests.exceptions.RequestException as e:
        print("Error fetching data: {}".format(e))
        return None


def get_data_from_file():
    try:
        tree = ET.parse("gold_price.xml")
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
    jewelry_list = data.find("JewelryList")

    if data is None:
        return None

    for child in jewelry_list.findall('Row'):
        if child.attrib["Key"] == gold_type:
            return child.attrib["Buy"]

    return None
