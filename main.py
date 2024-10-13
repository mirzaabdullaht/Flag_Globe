from flask import Flask, render_template, request, jsonify
import requests
import re
from flask_cors import CORS  # Add this import

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def get_country_info(country_name):
    url = f"https://restcountries.com/v3.1/name/{country_name}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        country_data = response.json()[0]  # Get the first country result
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}

    country_info = {
        'name': country_data['name']['common'],
        'capital': country_data.get('capital', ['No capital'])[0],
        'population': country_data.get('population', 'N/A'),
        'area': country_data.get('area', 'N/A'),
        'region': country_data.get('region', 'N/A'),
        'flag': country_data['flags']['png'],
        'languages': ', '.join(country_data['languages'].values()),
        'subregion': country_data.get('subregion', 'N/A')
    }

    return country_info

def get_wikipedia_info(country_name):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'search',
        'srsearch': country_name,
        'utf8': '',
        'formatversion': '2'
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        search_results = data.get('query', {}).get('search', [])
        articles = []

        for result in search_results:
            title = result['title']
            snippet = result['snippet']
            clean_snippet = re.sub('<.*?>', '', snippet)
            articles.append({
                'title': title,
                'snippet': clean_snippet,
                'url': f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
            })

        return articles

    except requests.exceptions.RequestException as e:
        return str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_country', methods=['POST'])
def get_country():
    country_name = request.form['country']
    country_info = get_country_info(country_name)

    if 'error' in country_info:
        return jsonify(country_info)  # Return the error message

    wikipedia_info = get_wikipedia_info(country_info['name'])
    country_info['wikipedia_info'] = wikipedia_info
    return jsonify(country_info)

@app.route('/compare_countries', methods=['POST'])
def compare_countries():
    country_name_1 = request.form['country1']
    country_name_2 = request.form['country2']
    country_info_1 = get_country_info(country_name_1)
    country_info_2 = get_country_info(country_name_2)

    comparison_info = {
        'country1': country_info_1,
        'country2': country_info_2
    }

    return jsonify(comparison_info)

@app.route('/get_cultural_insights', methods=['POST'])
def get_cultural_insights():
    country_name = request.form['country']
    country_info = get_country_info(country_name)

    insights = {
        'traditions': ["Traditional Dance", "Cultural Festival"],  # Replace with real data
        'foods': ["Local Dish 1", "Local Dish 2"],  # Replace with real data
        'facts': ["Interesting Fact 1", "Interesting Fact 2"]  # Replace with real data
    }

    return jsonify(insights)

@app.route('/quiz', methods=['GET'])
def get_quiz():
    quiz_data = [
        {"question": "What is the capital of France?", "options": ["Paris", "Rome", "Berlin"], "answer": "Paris"},
        {"question": "Which country is known as the Land of the Rising Sun?", "options": ["Japan", "China", "Korea"], "answer": "Japan"},
    ]
    return jsonify(quiz_data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
