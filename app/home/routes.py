# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from app.home import blueprint
from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app import login_manager
from jinja2 import TemplateNotFound

from flask import Flask
import io
import random
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd

from altair import Chart, X, Y, Axis, Data, DataFormat
import numpy as np
from flask import render_template, url_for, flash, redirect, request, make_response, jsonify, abort
#from web import app
from app.home.utils import utils, altair_plot, plotly_plot
import json

# section for covid diagram for country

data_url = "https://covid19-lake.s3.us-east-2.amazonaws.com/rearc-covid-19-world-cases-deaths-testing/csv/covid-19-world-cases-deaths-testing.csv"

data = pd.read_csv(data_url)

def plot_data():

    newzealand = data[data["location"] == "New Zealand"]   

    last30 = newzealand[-30:]

    date = pd.to_datetime(last30["date"]).dt.strftime("%m/%d")

    fig = Figure(figsize=(18, 12))

    axis1 = fig.add_subplot(2, 1, 1)

    axis1.plot(date, last30["total_cases"], label='Total Cases')

    axis1.set_title("Total Cases in recent 30 days")

    axis2 = fig.add_subplot(2, 1, 2)

    axis2.plot(date, last30["total_deaths"], label = "Total Deaths")

    axis2.set_title("Total Deaths in recent 30 days")
    
    output = io.BytesIO()

    FigureCanvas(fig).print_png(output)

    return data, output
def all_data():
    Asia = data[data["continent"] == "Asia"]
    last30 = Asia[-30:]   
    return data, output
data, output = plot_data()


@blueprint.route('/plot.png')
def image_plot():
    # fig = create_figure()
    # output = io.BytesIO()
    # FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

# end of plot section

#app = Flask(__name__)
#@app.route("/")

@blueprint.route('/ui-maps')
@login_required
def plot_chartjs():
    pagetitle = "HomePage"
    return render_template('ui-maps.html',segment='ui-maps', mytitle=pagetitle, mycontent="Hello World")

total_confirmed, total_death, total_recovered, df_pop = utils.load_data()

(grouped_total_confirmed, grouped_total_recovered,
 grouped_total_death, timeseries_final, country_names) = utils.preprocessed_data(total_confirmed, total_death, total_recovered)

final_df = utils.merge_data(grouped_total_confirmed,
                            grouped_total_recovered, grouped_total_death, df_pop)


@blueprint.route('/index')
@login_required
def index():
    total_all_confirmed = total_confirmed[total_confirmed.columns[-1]].sum()
    total_all_recovered = total_recovered[total_recovered.columns[-1]].sum()
    total_all_deaths = total_death[total_death.columns[-1]].sum()
    countries = final_df['Country/Region'].values.tolist()
    total_values = final_df['confirmed'].values.tolist()
    cases_per_million = final_df['cases/million'].values.round(2).tolist()
    
    #  time series for each cases
    confirmed_timeseries = timeseries_final["daily new cases"].values.tolist()
    death_timeseries = timeseries_final["daily new deaths"].values.tolist()
    recovered_timeseries = timeseries_final["daily new recovered"].values.tolist()
    timeseries_dates = timeseries_final["date"].values.tolist()
    #load json file for highchart map
    datamap = utils.load_chartjs_map_data(final_df, df_pop)

    context = {"total_all_confirmed": total_all_confirmed,
               "total_all_recovered": total_all_recovered, "total_all_deaths": total_all_deaths,
               "confirmed_timeseries": confirmed_timeseries, "death_timeseries": death_timeseries,
               "recovered_timeseries": recovered_timeseries, 'timeseries_dates': timeseries_dates,
               'countries': countries, 'total_values': total_values,
               'cases_per_million': cases_per_million, 'datamap': datamap}
    return render_template('index.html', segment='index',context=context)

@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith( '.html' ):
            template += '.html'

        # Detect the current page
        segment = get_segment( request )

        # Serve the file (if exists) from app/templates/FILE.html
        return render_template( template, segment=segment )

    except TemplateNotFound:
        return render_template('page-404.html'), 404
    
    except:
        return render_template('page-500.html'), 500

# Helper - Extract current page name from request 
def get_segment( request ): 

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment    

    except:
        return None  
