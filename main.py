"""
author: Shru Kumar
filename: main.py
description: utilizes MongoAPI and answers 10 queries
"""
import pymongo
from mongo_api import MongoAPI
from pprint import pprint

mongo = MongoAPI(db = 'Cooking', col = 'Recipes')

# Q1: Can I get a list of meals that fulfill my desired macronutrient goals?
macro_meals = mongo.meals_with_macros(protein = 30, calories = 300, sodium = 400, fat = 20, num = 10)
pprint(macro_meals)

# Q2: Which recipes have 3 ingredients or less?
max_ingr_recipes = mongo.count_ingredients(max_ingredients=3, num=10)
pprint(max_ingr_recipes)

# Q3: What is the average rating of all recipes
avg_rating = mongo.average_tag(tag = 'rating')
print(avg_rating)

# Q4: What is the correlation between sodium and calories in all recipes? (vis1) (scatterplot)
mongo.scatter('sodium', 'calories')

# Q5: Which 10 categories are there the most recipes for? (vis2) (bar graph)
mongo.count_categories(num = 10)

# Q6: Which categories have the highest ratings? (vis3) (bar graph)
mongo.category_ratings(num = 10)

# Q7: Can I look for recipes with a specific ingredient?
recipes = mongo.search_ingredient('bacon', num = 10)
pprint(recipes)

# Q8: What is the historic trend for recipe uploads? (vis4) (line graph)
mongo.timeline()

# Q9: How many distinct-categories are there?
distinct = mongo.distinct_tag('categories')
print(distinct)

# Q10: Which recipes have the least directions?
directions = mongo.few_directions(num = 10)
pprint(directions)