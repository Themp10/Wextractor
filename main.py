from flask import Flask, render_template, redirect, url_for, send_file,request
import requests
import pandas as pd
from bs4 import BeautifulSoup

app = Flask(__name__)

maxpage=6 # par defaut sur le site le max est 5 pages ici c'est 5+1question de tableau
ipm_counter=0
#vérifier si on recois un tableau avec d'essayer de récupérer le numéro
def getTel(arr):
    if (len(arr)==0):
        return "pas de tel"
    return arr[1]

# fonction pour logger la data au cas ou ca coupe pendant le chargement 
def writeLog(text,type):
    file1 = open("log.txt", type)
    file1.write(text+" \n")
    file1.close()

#on call cette fonction pour car il faut ouvrir la fiche pour extraire les données qu'on cherche ( on peut s'en passer si tout se trouve sur la meme page)
def extract_data_from_url(url,string,ou,ipm):
    global ipm_counter
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Referer': 'https://www.telecontact.ma/'
        # ce header est important car ce site spécifiquement bloque les agents bizzare comme un code python par exemple, 
        #on se fait passr pour un navigateur .. chuuuut ;)
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
            "Nom":name,
            "Tel" :tel,
            "Metier":string,
            "Ville":ou
        }
        writeLog(name+";"+tel+";"+string+";"+ou,"a")
        print("ohohohohoohoh",ipm_counter)
        ipm_counter+=1
        if (ipm==ipm_counter):
            ipm_counter=0
        return info
    else:
        print(f"Error: {response.status_code}")
        return None

# recupération initiale des données 
def get_data(string, ou, ipm,page):
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
    }
    response = requests.get(base_url, params=params, headers=headers)
    
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Modifier la class qui contient le lien a ouvrir
        href_elements = soup.select('.result-search-item-non-annonceur-description-title h2 a')
        results = []
        for href_element in href_elements:
            href = href_element['href']
            data = extract_data_from_url(href,string, ou,ipm)

            if data:
                results.append(data)
            if ipm_counter==0:
                break                
        return results
    else:
        print(f"Error: {response.status_code}")
        return None

# route principale pour acceder a la recherche
@app.route('/', methods=['GET', 'POST'])
def search():
    #on peut modifier a volonté le fichier html dans le dossier templates ( syntaxe de flask )
    return render_template('search.html')

#permet de récuper le fichier texte log qu'on préparé au cas oué ca a coupé
@app.route('/getLog', methods=['GET', 'POST'])
def getLog():
    return send_file('log.txt', as_attachment=True, download_name='Backup.txt')


# créer et envoyé le fichier excel
@app.route('/download', methods=['GET', 'POST'])
def download_excel():
    global ipm_counter
    writeLog("Nom;Tel;Metier;Ville","w")
    strings = request.form['strings'].splitlines()
    ous = request.form['ous'].splitlines()
    ipm = int(request.form['ipm'])
    data_list = []

    for string in strings:
        for ou in ous:
            page = 1
            
            while page < maxpage:
                
                data = get_data(string, ou,ipm, page)
                
                if not data:
                    break
                data_list.extend(data)
                if ipm_counter==0:
                    break
                page += 1  # passer à la page suivante
        ipm_counter=0

    # Create a DataFrame from the data list
    df = pd.DataFrame(data_list)
   # Save the Excel file to a temporary location
    excel_filename = 'resultat.xlsx'
    df.to_excel(excel_filename, index=False)
    # Return the Excel file for download
    return send_file(excel_filename, as_attachment=True, download_name='resultat.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

#fonction principale 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
