from flask import Flask, render_template, request
from flask_cors import cross_origin
from stats import get_stats

app = Flask(__name__)

@app.route('/')
@cross_origin()
def home():
    return render_template('index.html')

@app.route('/stats', methods=['GET', 'POST'])
@cross_origin()
def show_stat():
    if request.method == 'POST':
        country = request.form['Country']
        if (country != 'World'):
            total_cases, total_deaths, daily_cases, daily_deaths, date = get_stats(country)
            return (render_template('country_stats.html',
                                    date = date,
                                    country=country,
                                    total_cases=f'{total_cases: 10,.2f}',
                                    total_deaths=f'{total_deaths: 10,.2f}',
                                    daily_cases=f'{daily_cases: 10,.2f}',
                                    daily_deaths=f'{daily_deaths: 10,.2f}'))
        else:
            total_cases, total_deaths, daily_cases, daily_deaths, graphJSON, date = get_stats(country)
            return (render_template('world_stats.html',
                                    date=date,
                                    country=country,
                                    total_cases=f'{total_cases: 10,.2f}',
                                    total_deaths=f'{total_deaths: 10,.2f}',
                                    daily_cases=f'{daily_cases: 10,.2f}',
                                    daily_deaths=f'{daily_deaths: 10,.2f}',
                                    plot=graphJSON))

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
