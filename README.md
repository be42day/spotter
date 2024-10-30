# spotter

## Virtual Environment
Create an environment and activate it:

`conda create -n spotter python=3.10`

`conda activate spotter`

## Dependencies
Open a terminal at the root of the project and install the dependencies:

`pip install -r requirements.txt`

## Run

`cd myproject`

`python manage.py runserver`

To get the optimal route, send the coordinates of the origin and the destination cities:

`{
  "city1_lat": 40.730610,
  "city1_long": -73.935242,
  "city2_lat": 34.052235,
  "city2_long": -118.243683
}`
