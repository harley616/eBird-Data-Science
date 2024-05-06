from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import datetime 
from flask import request
import math



data = pd.read_csv('bird_data.csv')


def getBirds(day, month, plusOrMinus):
    """
    returns a data frame of birds that have been observed from various years during the same day and month
    plus_or_minus so many days.
    
    """
    def distance(date, target):
        '''
        Helper function
        returns the number of days away the date is from the target
        '''
        givenMonth = int(date[5:7])
        targetMonth = int(target[5:7])
        givenDay = int(date[8:])
        targetDay = int(target[8:])
        
        total = abs(givenMonth - targetMonth)*30 #grab the difference in months
        
        if givenMonth > targetMonth:
            total = total - targetDay + givenDay
        elif givenMonth < targetMonth:
            total = total - givenDay + targetDay
        else: 
            total = abs(givenDay - targetDay)
        
        return total
        
     
    if month > 10:
        target = 'xxxx-{}-{}'.format(month,day) if day > 10 else 'xxxx-{}-0{}'.format(month,day)
    else:
        target = 'xxxx-0{}-{}'.format(month,day) if day > 10 else 'xxxx-0{}-0{}'.format(month,day)
        

    # This is not the best implementation, I am just lazy and didn't want to search for the right one (help if you can)
    mask = pd.Series([distance(date, target) <= plusOrMinus for date in data['OBSERVATION DATE']])
        
    return data[mask]


class Item:
    def __init__(self, name, birds, birdCounts = {}):
        self.name = name
        self.features = {bird: 0.0 for bird in birds}
        self.birdCounts = birdCounts #dictionary of bird name and count 
        
    def getFeatures(self):
        big = max(list(self.birdCounts.values()))
        for bird in self.birdCounts:
            self.features[bird] = self.birdCounts[bird]/big
        
    
class User:
    def __init__(self, ratings, birds):
        self.features = {bird: 0.0 for bird in birds}
        self.ratings = ratings
        
    def getFeatures(self):
        big = max(list(self.ratings.values()))
        for bird in self.ratings:
            self.features[bird] = self.ratings[bird]/big


def eucDist(a, b):    
    total = 0
    for (i,j) in zip(a,b):
        total += (i-j)**2
    return math.sqrt(total)
    

def getTop5Scores(user):
    '''
    Find top 5 counties for user
    Use cosine similarity to compare user's scores to county's bird populations
    returns list containing top 5 counties
    '''
    countyScores = []
    
    for county in countyFeatures:
        # Only calculate cosine similrity on
        # birds (in counties) the user has rated (has a non-zero value)
        user_ratings = []
        county_ratings = []
        for index, (bird, user_rating) in enumerate(user.features.items()):
            if user_rating != 0:
                user_ratings.append(user_rating)
                county_ratings.append(county.features.get(bird, 0))  # If bird not in county features, use 0
        countyScores.append((county, eucDist(user_ratings, county_ratings)))
    countyScores = sorted(countyScores, key = lambda x: x[1], reverse=False)
    # for (county, score) in countyScores[:5]:
    #     print(f'{county.name} score of Canada Goose: {county.features["Canada Goose"]}, Common Raven: {county.features["Common Raven"]}')
    
    top5 = [x[0].name for x in countyScores[:5]]
    print(top5)
    return top5

counties = data['COUNTY'].unique()
birds = data['COMMON NAME'].unique()

rawDate = datetime.datetime.now()

month = rawDate.month
day = rawDate.day

seasonal_birds_within_20_days = getBirds(day,month, 10)

unique_birds_in_season = seasonal_birds_within_20_days['COMMON NAME'].unique()

groupByCounty = data.groupby(by = ["COUNTY"])['COMMON NAME'].value_counts()

countyFeatures = []

for county in counties:
    counts = {i: groupByCounty[county][i] for i in groupByCounty[county].index}
    countyFeatures.append(Item(county, birds, counts))


for county in countyFeatures:
    county.getFeatures()




'''
-----------------------------API STARTS HERE--------------------------------->
'''





# Create a Flask application
app = Flask(__name__)

CORS(app)
# Define a route for the homepage

@app.route('/')
def index():
    res = [{'res': 'Hello world'}]
    return jsonify(res)

@app.route('/birds')
def getBirds():
    return jsonify(unique_birds_in_season.tolist())

@app.route('/counties')
def getCounties():
    return jsonify(counties.tolist())

# Post the users ratings then return a list of the top 5 counties they should visit
@app.route('/birds', methods=['POST'])
def updateBirds():
    user = User({}, birds)
    birds_list = request.get_json()
    print(birds_list)
    for bird in birds_list:
        print(int(birds_list[bird]))
        user.ratings[bird] = int(birds_list[bird])
    user.getFeatures()
    top5 = getTop5Scores(user)
    return jsonify(top5)


if __name__ == '__main__':
    app.run(debug=False)
