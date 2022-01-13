from rdflib import Graph, URIRef, BNode, Literal
from rdflib.namespace import Namespace, RDF, XSD, RDFS

foodGraph = Graph()


def serializeGraph():
    foodGraph.serialize('foodGraph.ttl', format='ttl')


def get_asin():
    asin = str(input('Enter the product\'s ID of this ingredient: '))
    return asin


def removeMissingData():

    # Removing missing data --> indicated with 'None' or 'none'

    for s, p, o in foodGraph:
        if 'None' in o or 'none' in o:
            foodGraph.remove((s, p, o))
            foodGraph.remove((o, None, None))

    # Removing unsed blank node
    for s, p, o in foodGraph:
        if type(o) is BNode and not((o, None, None) in foodGraph):
            foodGraph.remove((s, p, o))

    serializeGraph()


def removeUncessaryData():
    food = Namespace('http://data.lirmm.fr/ontologies/food#')
    product = Namespace('https://example.org/food/')

    print('\nRemoving unnecessary ingredients\n')

    while 1:
        ingr = Namespace('https://example.org/food/ingredient/')
        ingredientName = str(input('Enter an ingredient you want to delete: '))

        if ingredientName == '':
            break

        # Check if the ingredient has no sub-ingredients
        ingredient = URIRef(ingr[ingredientName.lower().replace(' ', '')])

        if not(ingredient in foodGraph.subjects()):
            asin = get_asin()
            ingr = Namespace('https://example.org/food/' +
                             asin.strip()+'/ingredient/')
            ingredient = URIRef(ingr[ingredientName.lower().replace(' ', '')])

        if ingredient in foodGraph.subjects():

            for (s, p, o) in foodGraph:
                if ingredient == s and p == food['containsIngredient']:

                    foodGraph.remove((ingredient, None, None))
                    fproduct = URIRef(product[asin.strip()])
                    foodGraph.add((fproduct, p, o))

                foodGraph.remove((ingredient, None, None))
                foodGraph.remove((None, None, ingredient))

            serializeGraph()
        else:
            print('ingredient', ingredientName, 'does not exist in KG')


def changeIncorrectData():
    food = Namespace('http://data.lirmm.fr/ontologies/food#')

    print('\n\nRemoving incorrect ingredients\n')

    while 1:

        ingredientName = str(input('Enter an ingredient you want to change: '))

        ing = Namespace('https://example.org/food/ingredient/')
        ingredient = URIRef(ing[ingredientName.lower().replace(' ', '')])

        if ingredientName == '':
            return True

         # Check if the ingredient has no sub-ingredients
        if not(ingredient in foodGraph.subjects()):
            asin = get_asin()
            ing = Namespace('https://example.org/food/' +
                            asin.strip()+'/ingredient/')
            ingredient = URIRef(ing[ingredientName.lower().replace(' ', '')])

        if ingredient in foodGraph.subjects():

            newO = str(input('Enter the correct ingredient: '))
            print()
            newIngr = URIRef(ing[newO.lower().replace(' ', '')])
            newO = Literal(newO.title(), datatype=XSD['string'])

            # Change the other relations
            for sub, pre, obj in foodGraph:
                if obj == ingredient:
                    foodGraph.remove((sub, pre, obj))
                    foodGraph.add((sub, pre, newIngr))

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

        while 1:
            removeUncessaryData()
            stop = changeIncorrectData()

            if stop:
                break

        print('\n\nfinished cleaning')

    except:
        print('Graph does not exist')
