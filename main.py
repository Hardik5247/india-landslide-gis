import requests
import time
import os

from flask import Flask, jsonify
from flask_cors import CORS, cross_origin

from pandas import DataFrame
from spacy import displacy, load
from tabula import read_pdf
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app, support_credentials=True)
nlp = None


@app.route('/extract/<string:path>', methods=['GET'])
def pdf_extract(path):
    data = read_pdf('./reports/2020/dcport1gsigovi824861.pdf', pages='all', stream=True, multiple_tables=True)
    for i in range(len(data)):
        data[i] = data[i].to_dict()
    return jsonify(data)


@app.route('/<int:pages>', methods=['GET'])
def news_api(pages):
    global nlp
    if nlp is None:
        nlp = load('en_core_web_trf')  # en_core_web_trf gives better results than en_core_web_sm

    data = []
    baseUrl = 'https://timesofindia.indiatimes.com/topic/landslides/news/{}'

    for page in range(1, pages + 1):
        url = baseUrl.format(str(page))

        try:
            page = requests.get(url)
            time.sleep(2)
        except Exception as e:
            print(e)
            continue

        soup = BeautifulSoup(page.text, 'html.parser')
        links = soup.find_all('div', attrs={'class': 'Mc7GB'})
        data.extend(links)

    for i in range(len(data)):
        news = data[i]

        title = news.find("span").text.strip()
        body = news.find("p").find("span").text.strip()
        date = news.find("div", attrs={'class': 'hVLK8'}).text.strip()
        locations = [ent.text for ent in nlp(body).ents if ent.label_ == "GPE" or ent.label_ == "LOC"]

        data[i] = (date, title, body, locations)

    # print(DataFrame(data, columns=['Date', 'Title', 'Body', 'Locations']))

    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True, host="localhost")
