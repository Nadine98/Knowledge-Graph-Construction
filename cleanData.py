from rdflib import Graph, URIRef, BNode, Literal
from rdflib.namespace import Namespace, RDF, XSD, RDFS

foodGraph = Graph()


def serializeGraph():
    foodGraph.serialize('foodGraph.ttl', format='ttl')


def get_asin():
    asin = str(input('Enter the product\'s ID of this ingredient: '))
    return asin


# Function for removing missing data
def removeMissingData():

    # Missing data are indicated with 'None' or 'none'
    for s, p, o in foodGraph:
        if 'None' in o or 'none' in o:
            foodGraph.remove((s, p, o))
            foodGraph.remove((o, None, None))

    # Removing blank node if it is not used --> is not a subject in a Node-to-Node relation
    for s, p, o in foodGraph:
        if type(o) is BNode and not((o, None, None) in foodGraph):
            foodGraph.remove((s, p, o))

    serializeGraph()


# Function for removing unnecessary data from the ingredients
def removeUncessaryData():
    food = Namespace('http://data.lirmm.fr/ontologies/food#')
    product = Namespace('https://example.org/food/')

    print('\nRemoving unnecessary ingredients\n')

    while 1:

        ingredientName = str(input('Enter an ingredient you want to delete: '))

        # Break this cleaning process if the user don't enter an ingredient
        if ingredientName == '':
            break

        # Set the namespace of the ingredient to 'https://example.org/food/ingredient/' --> is for ingredient without subs
        ingr = Namespace('https://example.org/food/ingredient/')
        ingredient = URIRef(ingr[ingredientName.lower().replace(' ', '')])

        # Check now if the ingredient has no subs
        # if it has subs then change the namespace to 'https://example.org/food/{product's ASIN}/ingredient/'
        if not(ingredient in foodGraph.subjects()):
            asin = get_asin()
            ingr = Namespace('https://example.org/food/' +
                             asin.strip()+'/ingredient/')
            ingredient = URIRef(ingr[ingredientName.lower().replace(' ', '')])

        # Remove now this ingredient
        if ingredient in foodGraph.subjects():
            for (s, p, o) in foodGraph:

                # set its sub-ingredients in a 'containsIngredient'-relation with the food product
                if ingredient == s and p == food['containsIngredient']:

                    foodGraph.remove((ingredient, None, None))
                    fproduct = URIRef(product[asin.strip()])
                    foodGraph.add((fproduct, p, o))

                # Now delete every relation and the node of this unnecessary ingredient

                foodGraph.remove((ingredient, None, None))
                foodGraph.remove((None, None, ingredient))

            serializeGraph()
        else:
            print('ingredient ', ingredientName, ' does not exist in KG')


# Function for modifying incorrect ingredients
def changeIncorrectData():
    food = Namespace('http://data.lirmm.fr/ontologies/food#')

    print('\n\nModifying incorrect ingredients\n')

    while 1:

        ingredientName = str(input('Enter an ingredient you want to change: '))

        # Break this cleaning process if the user don't enter an ingredient
        if ingredientName == '':
            break

        # Set the namespace of the ingredient to 'https://example.org/food/ingredient/' --> is for ingredient without subs
        ing = Namespace('https://example.org/food/ingredient/')
        ingredient = URIRef(ing[ingredientName.lower().replace(' ', '')])

        # Check if the ingredient has sub-ingredients
        # if it has subs then change the namespace to 'https://example.org/food/{product's ASIN}/ingredient/'
        if not(ingredient in foodGraph.subjects()):
            asin = get_asin()
            ing = Namespace('https://example.org/food/' +
                            asin.strip()+'/ingredient/')
            ingredient = URIRef(ing[ingredientName.lower().replace(' ', '')])

        # Now change the wronge ingredient --> user input for the new name of the ingredient 
        if ingredient in foodGraph.subjects():

            newO = str(input('Enter the correct ingredient: '))
            print()
            newIngr = URIRef(ing[newO.lower().replace(' ', '')])
            newO = Literal(newO.title(), datatype=XSD['string'])

            # Change all the node-to-node relations of the incorrect ingredient 
            for sub, pre, obj in foodGraph:
                
                # All relation where the incorrect ingredient is the object 
                if obj == ingredient:
                    foodGraph.remove((sub, pre, obj))
                    foodGraph.add((sub, pre, newIngr))

                # All relation where the incorrect ingredient is the subject 
                if sub == ingredient:
                    if pre == RDFS.label:
                        foodGraph.remove((sub, pre, obj))
                        foodGraph.add((newIngr, pre, newO))

                    elif pre == food['containsIngredient'] or pre == RDF.type:
                        foodGraph.remove((sub, pre, obj))
                        foodGraph.add((newIngr, pre, obj))

            serializeGraph()

        else:
            print('ingredient ', ingredientName, 'does not exist\n')
            continue


def cleanKG():
    try:
        foodGraph.parse('foodGraph.ttl', format='ttl')
        removeMissingData()
        removeUncessaryData()
        changeIncorrectData()
        print('\n\nfinished cleaning')

    except:
        print('Graph does not exist')
