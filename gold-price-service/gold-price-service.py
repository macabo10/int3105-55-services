import requests
import time
from flask import Flask, jsonify

app = Flask(__name__)

# API URL
url = "http://api.btmc.vn/api/BTMCAPI/getpricebtmc?key=3kd8ub1llcg9t45hnoh8hmn7t5kc2v"

def get_btmc_price():
    try:
        response = requests.get(url)
        response.raise_for_status()
        response = response.json()
        print("GOLDVIP", response)
        return response
    except requests.exceptions.RequestException as e:
        print("Error fetching data: {}".format(e))
        return None


# @app.route('/btmc_price', methods=['GET'])
def btmc_price():
      data = get_btmc_price()
      return jsonify(data)

if __name__ == "__main__":
    # # Run the Flask app, listening on port 5000 by default
    # app.run(host='0.0.0.0', port=5001)
    # while True:
    get_btmc_price()
    time.sleep(60)
