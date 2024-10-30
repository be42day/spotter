from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .utils import main

@api_view(['POST'])
def process_data(request):
    # Extract lat and long for two cities from request data
    city1_lat = request.data.get('city1_lat')
    city1_long = request.data.get('city1_long')
    city2_lat = request.data.get('city2_lat')
    city2_long = request.data.get('city2_long')

    result = main(city1_lat, city1_long, city2_lat, city2_long)
    return Response(result)