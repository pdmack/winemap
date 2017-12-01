import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import mean
from plotly.offline import plot
import argparse
from flask import Flask, render_template


app = Flask(__name__)


def init(self):
    parser = argparse.ArgumentParser(description='map')
    parser.add_argument('-SERVER',
                        help='the postgreql ip address or server name')
    parser.add_argument('-USER', help="username")
    parser.add_argument('-DBNAME', help='database name')
    parser.add_argument('-PASSWORD', help='password')

    args = parser.parse_args()

    self.make(args.server,
              args.user, args.dbname, args.password)
    print("made")


def make(server, user, dbname, password):
    spark_session = SparkSession.builder \
        .getOrCreate()

    url = "jdbc:postgresql://" + server\
          + "/"+dbname+"?user="+user+"&password="+password
    print(url)
    df = (spark_session.read.format("jdbc")
          .options(url=url, dbtable="wine_reviews")
          .load())
    table = df.select('country', 'points')\
        .groupBy('country').agg(mean('points'))\
        .orderBy('avg(points)', ascending=False)
    country_cols = table.select('country').collect()
    countries = list()
    for country in country_cols:
        countries.append(str(country[0]))
    point_cols = table.select('avg(points)').collect()
    points = list()
    for point in point_cols:
        points.append(point[0])
    data = dict(type='choropleth',
                locationmode='country names',
                locations=countries,
                colorscale='Blues',
                z=points,
                colorbar={'title': 'Average Rating'}
                )
    layout = dict(geo={'scope': 'world'})
    choromap = dict(data=[data], layout=layout)
    plot(choromap, filename='map.html')
    print("map")


def make_template():
    # make the templates dir
    new_path = r'/opt/app-root/src/templates'
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    # move the file to the templates dir
    os.system('mv /opt/app-root/src/map.html '
              '/opt/app-root/src/templates/')
    resp = render_template("map.html", title='Maps')
    print(resp)
    return resp


@app.route('/')
def index():
    # create map
    print("in index")
    init()
    resp = make_template()
    print("NEXT      "+resp)
    return resp


if __name__ == '__main__':
    print("in main")
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
