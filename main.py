from flask import Flask
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def extract_data_from_url(url):
    response = requests.get(url)

    if response.status_code == 200:
        # Parse the HTML content of the detailed page
        detailed_soup = BeautifulSoup(response.text, 'html.parser')

        # Extract information based on specific tags, classes, etc.
        name = detailed_soup.find('span', class_='name_class').text
        phone_number = detailed_soup.find('span', class_='phone_class').text

        return f"Name: {name}, Phone Number: {phone_number}"
    else:
        print(f"Error: {response.status_code}")
        return None

def get_data(string, ou, page):
    base_url = "https://www.telecontact.ma/trouver/index.php"
    params = {
        'string': string,
        'ou': ou,
        'nxo': 'moteur',
        'nxs': 'process',
        'page': page
    }

    response = requests.get(base_url, params=params)
    echo response
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extracting href from a div with a specific class (replace 'your_div_class' with the actual class)
        href_elements = soup.select('.result-search-item-non-annonceur-description-title h2 a')
        results = []
        for href_element in href_elements:
            href = href_element['href']

            # data = extract_data_from_url(href)
            # if data:
            #     results.append(data)
        return results
    else:
        print(f"Error: {response.status_code}")
        return None

@app.route('/')
def index():
    strings = ["veterinaire"]
    ous = ["Casablanca"]

    html_content = "<h1>Scraping Results</h1><ul>"

    for string in strings:
        for ou in ous:
            page = 1
            while page<5:
                data = get_data(string, ou, page)
                print("data : ",data)
                if not data:
                    break
                for item in data:
                    html_content += f"<li>{item}</li>"
                page += 1  # Increment the page number for the next request

    html_content += "</ul>"
    return html_content

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
