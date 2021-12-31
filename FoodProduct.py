
class nutritional_information:

    def __init__(self):
        self.servingSize = 'None'
        self.fats = 'None'
        self.carbohydrates ='None'
        self.protein = 'None'

    def setServingSize(self, servingSize):
        self.servingSize = servingSize

    def setFats(self, fats):
        self.fats = fats

    def setCarbohydrates(self, carbs):
        self.carbohydrates = carbs

    def setProteins(self, protein):
        self.protein = protein


class foodIngredient:
    def __init__(self, ingredient=None):
        self.ingredient = ingredient
        self.subingredient = list()

    def addIngredient(self, ingredient):
        self.ingredient = ingredient

    def addSubIngredient(self, subingredient):

        if type(subingredient) is str:
            subingredient = [subingredient]

        self.subingredient.extend(subingredient)


class foodProduct:

    def __init__(self):
        self.name = 'None'
        self.description='None'
        self.brand ='None'
        self.price = 'None'
        self.asin = 'None'
        self.url = 'None'
        self.category = 'None'
        self.country_of_origin = 'None'
        self.ingredients = 'None'
        self.allergen = 'None'
        self.nutritional_information = nutritional_information()
        self.reviewNumber='None'
        self.rating='None'

    def setName(self, name):
        self.name = name

    def setDecription(self, description):
        self.description=description

    def setBrand(self, brand):
        self.brand = brand

    def setPrice(self, price):
        self.price = price

    def setAsin(self, asin):
        self.asin = asin

    def setUrl(self, url):
        self.url = url

    def setCategory(self, category):
        self.category = category

    def setCountry(self, country):
        self.country_of_origin = country

    def addIngredients(self, ingredient):
        
        if (type(ingredient) is list and ingredient!=list())and self.ingredients=='None':
            self.ingredients = [foodIngredient()
                                for i in range(len(ingredient))]

            for i, value in enumerate(ingredient):
                if type(value) is str:
                    self.ingredients[i].addIngredient(value)

                if type(value) is list:
                    self.ingredients[i].addIngredient(value[0])
                    value.remove(value[0])
                    for value2 in value:
                        self.ingredients[i].addSubIngredient(value2)


    def addAllergenToIngredients(self,allergen):
        ing=foodIngredient()
        if type(allergen)==str:
            ing.addIngredient(allergen)
            self.ingredients.append(ing)
            


    def findIngredient(self,a):
    
        for i in self.ingredients:
            if i.ingredient==a:
               return True
            if i.subingredient!=list():
                for sub in i.subingredient:
                    if sub==a:
                        return True
        return False
            

  

    def addAllergen(self, allergen):
        self.allergen=list()
        if type(allergen) is foodIngredient:
            allergen = [allergen.ingredient]
        self.allergen.extend(allergen)

    def set_nutritional_information(self, nutrition):
        if type(nutrition) is nutritional_information:
            self.nutritional_information = nutrition

    def set_reviewNumber(self, number):
        self.reviewNumber=number
    
    def set_rating(self,rating):
        self.rating=rating
