# The main class is foodProduct
# it uses the other classes to structure and the nurtitional information and the ingredients


# Class for storing the nutritional information
class nutritional_information:

    def __init__(self):
        self.servingSize = 'None'
        self.fats = 'None'
        self.carbohydrates = 'None'
        self.protein = 'None'

    def setServingSize(self, servingSize):
        self.servingSize = servingSize

    def setFats(self, fats):
        self.fats = fats

    def setCarbohydrates(self, carbs):
        self.carbohydrates = carbs

    def setProteins(self, protein):
        self.protein = protein


# Class for storing an ingredient and its sub-ingredients
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
        self.__name = 'None'
        self.__description = 'None'
        self.__brand = 'None'
        self.__price = 'None'
        self.__asin = 'None'
        self.__url = 'None'
        self.__category = 'None'
        self.__country_of_origin = 'None'
        self.__ingredients = 'None'
        self.__allergen = 'None'
        self.__nutritional_information = nutritional_information()
        self.__reviewNumber = 'None'
        self.__rating = 'None'

# --------------------------------------------Setters for the insertion of the attributes' values--------------------------------------------
    def setName(self, name):
        self.__name = name

    def setDecription(self, description):
        self.__description = description

    def setBrand(self, brand):
        self.__brand = brand

    def setPrice(self, price):
        self.__price = price

    def setAsin(self, asin):
        self.__asin = asin

    def setUrl(self, url):
        self.__url = url

    def setCategory(self, category):
        self.__category = category

    def setCountry(self, country):
        self.__country_of_origin = country

    def setIngredients(self, ingredient):
        # Input is a list of ingredients

        if (type(ingredient) is list and ingredient != list()) and self.__ingredients == 'None':

            # Create first an empty list of the type foodIngredient
            self.__ingredients = [foodIngredient()
                                  for i in range(len(ingredient))]

            # Add every ingredient in the list
            for i, value in enumerate(ingredient):
                if type(value) is str:
                    self.__ingredients[i].addIngredient(value)

                # if the ingredient value is a list then add the first value into the attribut ingredient --> with the method addIngredient
                # And then the follow up elements in the attribute subIngredients --> with the method addSubIngredient
                if type(value) is list:
                    self.__ingredients[i].addIngredient(value[0])
                    value.remove(value[0])
                    for value2 in value:
                        self.__ingredients[i].addSubIngredient(value2)

    # Add an allergen to the ingredient list

    def addAllergenToIngredients(self, allergen):
        ing = foodIngredient()

        if type(allergen) == str:
            ing.addIngredient(allergen)
            self.__ingredients.append(ing)

    # Finde an ingredient in the attribut list ingredients and return 'True'

    def findIngredient(self, a):

        for i in self.__ingredients:
            if i.ingredient == a:
                return True

            if i.subingredient != list():
                for sub in i.subingredient:
                    if sub == a:
                        return True
        return False

    def setAllergens(self, allergen):
        if allergen != 'None':
            self.__allergen = list()
            if type(allergen) is foodIngredient:
                allergen = [allergen.ingredient]
            self.__allergen.extend(allergen)

    def setNritional_information(self, nutrition):
        if type(nutrition) is nutritional_information:
            self.__nutritional_information = nutrition

    def setReviewNumber(self, number):
        self.__reviewNumber = number

    def setRating(self, rating):
        self.__rating = rating


# --------------------------------------------Getters for accessing the private attributes----------------------------------------------

    def getName(self):
        return self.__name

    def getDescription(self):
        return self.__description

    def getBrand(self):
        return self.__brand

    def getPrice(self):
        return self.__price

    def getAsin(self):
        return self.__asin

    def getUrl(self):
        return self.__url

    def getCategory(self):
        return self.__category

    def getCountry(self):
        return self.__country_of_origin

    def getNutritional_information(self):
        return self.__nutritional_information

    def getReviewNumber(self):
        return self.__reviewNumber

    def getRating(self):
        return self.__rating

    def getIngredients(self):
        return self.__ingredients

    def getAllergens(self):
        return self.__allergen
