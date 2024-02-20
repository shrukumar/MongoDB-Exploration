"""
author: Shru Kumar
filename: mongo_api.py
description: establishing class MongoAPI and functions to answer 10 queries
"""
import pymongo
import seaborn as sns
import matplotlib.pyplot as plt

class MongoAPI:

    def __init__(self, db, col, client = "mongodb://localhost:27017/"):
        self.myclient = pymongo.MongoClient(client)
        self.mydb = self.myclient[db]
        self.mycol = self.mydb[col]

    # Q1
    def meals_with_macros(self, protein, calories, sodium, fat, num = 5):
        """Takes desired macro breakdown and returns list of matching recipes
        Args:
            protein (int): desired grams of protein threshold
            calories (int): desired calories threshold
            sodium (int): desired grams of sodium threshold
            fat (int): desired grams of fat threshold
            num (int): number of recipes to return, default = 5
        Returns:
            result (list): list of recipes that meet criteria and associated macros
        """
        query = {"protein": {"$gte": protein}, 'calories': {"$lte": calories}, 'sodium': {"$lte": sodium}, 
                 'fat': {"$lte": fat}}
        projection = {"title": 1, "_id": 0, 'desc': 1, 'directions': 1, 'protein': 1, 'calories': 1, 
                      'sodium': 1, 'fat': 1, 'rating': 1, 'ingredients': 1}
        result = list(self.mycol.find(query, projection))[:num]

        return result
    
    # Q2
    def count_ingredients(self, max_ingredients = 5, num = 5):
        """Returns recipe list including recipes with a max number of ingredients
        Args:
            max_ingredients (int): max desired number of ingredients, default = 5
            num (int): number of recipes to return, default = 5
        Returns:
            result (list): list of recipes with desired number of ingredients or less
        """
        pipeline = [{'$project': {'_id': 0, 'title': 1, 'num_ingredients': {'$size': '$ingredients'}, 'ingredients': 1, 
                                  'directions': 1}},
                    {'$match': {'num_ingredients':{'$lte': max_ingredients}}}]
        result = list(self.mycol.aggregate(pipeline))[:num]

        return result

    # Q3
    def average_tag(self, tag):
        """Calculates average value for a specified tag
        Args:
            tag (str): desired tag to find average value
        Returns:
            result (list): list only containing average value of tag category
        """
        pipeline = [{'$group': {'_id':'average ' + tag, 'avg_val':{'$avg':'$' + tag}}}]
        result = list(self.mycol.aggregate(pipeline))

        return result

    # Q4
    def scatter(self, tag1, tag2):
        """Produces scatterplot comparing two tag categories
        Args:
            tag1 (str): tag to be x-axis values
            tag2 (str): tag to be y-axis values
        """
        projection = {tag1: 1, tag2: 1, '_id': 0}
        result = list(self.mycol.find({}, projection)) 
        
        # collecting x and ys from result list
        x = []
        y = []
        for idx in range(len(result)):
            # ensuring values are present
            if result[idx][tag1] is None:
                pass
            elif result[idx][tag2] is not None:
                x.append(result[idx][tag1])
                y.append(result[idx][tag2])

        # plotting
        fig = plt.figure(figsize=(8, 5))
        ax = sns.scatterplot(x = x, y = y)
        plt.xlabel(tag1)
        plt.ylabel(tag2)
        plt.title(tag1 + ' vs. ' + tag2)
        plt.ticklabel_format(style='plain', axis='y')
        plt.ticklabel_format(style='plain', axis='x')
        plt.show()
    
    # Q5
    def count_categories(self, num=5):
        """Plot the categories with the most occurences
        Args:
            num (int): number of categories to return, default = 5
        """
        pipeline = [{'$unwind': '$categories'},
                    {'$group' : { '_id' : '$categories', 'count' : {'$sum' : 1}}},
                    {"$sort" : { "count" : -1 }}]
        result = list(self.mycol.aggregate(pipeline))[:num]

        # collecting bar plot values from result list
        counts = []
        categories = []
        for idx in range(len(result)):
            categories.append(result[idx]['_id'])
            counts.append(result[idx]['count'])

        # plotting
        fig = plt.figure(figsize=(5, 8))
        ax = sns.barplot(x = counts, y = categories)
        plt.xlabel('Number of Recipes')
        plt.ylabel('Recipe Categories')
        plt.title(f'Top {num} Categories with the Most Recipes')
        plt.show()
        
    def category_ratings(self, num = 5):
        """Plot the categories with the top average ratings
        Args:
            num (int): number of categories to return, default = 5
        """
        # first pipeline for filtering categories with less than 10 occurences
        pipeline1 = [{'$unwind': '$categories'},
                    {'$group' : { '_id' : '$categories', 'count' : {'$sum' : 1}}}, 
                    {"$sort" : { "count" : -1 }}, 
                    {'$match' : {"count" :{'$gte': 10}}}
                    ]
        result1 = list(self.mycol.aggregate(pipeline1))
        categories = [result1[idx]['_id'] for idx in range(len(result1))]

        # second pipeline for getting top average rating
        pipeline2 = [{'$unwind': '$categories'},
                    {'$match' : {'categories' : {"$in": categories}}},
                    {'$group' : { '_id' : '$categories', 'avg_rating' : {'$avg' : '$rating'}}}, 
                    {"$sort" : { "avg_rating" : -1 }}]
        result2 = list(self.mycol.aggregate(pipeline2))[:num]

        # collecting bar plot values from result list
        counts = []
        categories = []
        for idx in range(len(result2)):
            categories.append(result2[idx]['_id'])
            counts.append(result2[idx]['avg_rating'])

        # plotting
        fig = plt.figure(figsize=(5, 8))
        ax = sns.barplot(x = counts, y = categories)
        plt.xlabel('Rating')
        plt.ylabel('Recipe Categories')
        plt.title(f'Top {num} Categories with the Best Ratings')
        plt.show()

    # Q7    
    def search_ingredient(self, target_ingredient, num=5):
        """Returns list of recipes containing target ingredient
        Args:
            target_ingredient (str): desired ingredient
            num (int): number of recipes to return, default = 5
        Returns:
            result (list): list of recipes containing target ingredient
        """
        query = {"ingredients" : {'$regex' : target_ingredient}}
        projection = {"title": 1, "_id": 0, 'desc': 1, 'directions': 1, 'rating': 1, 'ingredients': 1}
        result = list(self.mycol.find(query, projection))[:num]

        return result
    
    # Q8
    def timeline(self):
        """Plots number of recipes posted per year
        """
        projection = {"_id": 0, 'date' : 1}
        result = list(self.mycol.find({}, projection))

        dates = {}
        for idx in range(len(result)):
            date = result[idx]['date'][:4]
            if date not in dates.keys():
                dates[date] = 1
            else:
                dates[date] += 1
        dates = dict(sorted(dates.items()))

        fig = plt.figure(figsize=(5, 8))
        ax = sns.lineplot(x = dates.keys(), y = dates.values())

        plt.xlabel('Years')
        plt.ylabel('Number of Recipes Published')
        plt.title('Number of Recipes Published Over Time')
        plt.show()
    
    # Q9
    def distinct_tag(self, tag):
        """Returns distinct values of desired tag
        Args:
            tag
        """
        result = len(list(self.mycol.distinct(tag)))

        return result
    
    # Q10
    def few_directions(self, num = 5):
        """Returns recipes with the least directions
        Args:
            num (int): number of recipes to return, default = 5
        Returns:
            result (list): list of recipes with the least directions
        """
        pipeline = [{'$unwind': '$directions'},
                    {'$group' : { '_id' : '$title', 'count' : {'$sum' : 1}}}, 
                    {"$sort" : { "count" : 1 }}]
        result = list(self.mycol.aggregate(pipeline))[:num]

        return result