from flask import Flask, render_template, redirect, url_for, send_file,request
import requests
import pandas as pd
from bs4 import BeautifulSoup

app = Flask(__name__)
def getTel(arr):
    if (len(arr)==0):
        return "pas de tel"
    return arr[1]

def writeLog(text,type):
    file1 = open("log.txt", type)
    file1.write(text+" \n")
    file1.close()

def extract_data_from_url(url,string,ou):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Referer': 'https://www.telecontact.ma/'
        # Add more headers if needed
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Parse the HTML content of the detailed page
        detailed_soup = BeautifulSoup(response.text, 'html.parser')
        name_strong = detailed_soup.select_one('.searching-result h1 strong')
        name=name_strong.text
        
        tel_href = detailed_soup.select_one('.btns button a')
        print(tel_href)
        tel="Pas de tel"
        if tel_href is not None:
            tel=getTel(tel_href['href'].split(":"))
    
        info={
            "name":name,
            "tel" :tel,
            "metier":string,
            "Ville":ou
        }
        writeLog(name+";"+tel+";"+string+";"+ou,"a")
        return info
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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Referer': 'https://www.telecontact.ma/'
        # Add more headers if needed
    }
    response = requests.get(base_url, params=params, headers=headers)
    
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extracting href from a div with a specific class (replace 'your_div_class' with the actual class)
        href_elements = soup.select('.result-search-item-non-annonceur-description-title h2 a')
        results = []
        for href_element in href_elements:
            href = href_element['href']
            data = extract_data_from_url(href,string, ou)
            if data:
                results.append(data)
        return results
    else:
        print(f"Error: {response.status_code}")
        return None

# @app.route('/')
# def index():
#     strings = ["veterinaire"]
#     ous = ["Casablanca"]

#     html_content = "<h1>Scraping Results</h1><ul>"

#     for string in strings:
#         for ou in ous:
#             page = 1
#             while page<2:
#                 data = get_data(string, ou, page)
#                 if not data:
#                     break
#                 for item in data:
#                     html_content += f"<li>{item['name']} , {item['tel']}</li>"
#                 page += 1  # Increment the page number for the next request

#     html_content += "</ul>"
#     return html_content
@app.route('/oo')
def home():
    return render_template('index.html')

@app.route('/', methods=['GET', 'POST'])
def search():
    # if request.method == 'GET':
    #     # Get the values from the form
    #     strings = requests.form['strings'].split('\n')
    #     ous = requests.form['ous'].split('\n')

    #     # Redirect to the download page with the parameters
    #     return redirect(url_for('download_excel', strings='\n'.join(strings), ous='\n'.join(ous)))

    # # Render the search page
    return render_template('search.html')



@app.route('/download', methods=['GET', 'POST'])
def download_excel():
    writeLog("Nom;Tel;Metier;Ville","w")
    strings = request.form['strings'].split('\n')
    ous = request.form['ous'].split('\n')

    data_list = []

    for string in strings:
        for ou in ous:
            page = 1
            while page < 3:
                data = get_data(string, ou, page)
                if not data:
                    break
                data_list.extend(data)
                page += 1  # passer à la page suivante

    # Create a DataFrame from the data list
    df = pd.DataFrame(data_list)
   # Save the Excel file to a temporary location
    excel_filename = 'resultat.xlsx'
    df.to_excel(excel_filename, index=False)

    # Return the Excel file for download
    return send_file(excel_filename, as_attachment=True, download_name='resultat.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
