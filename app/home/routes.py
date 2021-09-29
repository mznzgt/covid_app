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

@blueprint.route('/index')
@login_required
def index():
    return render_template('index.html', segment='index')

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