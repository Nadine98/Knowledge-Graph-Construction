
from FoodProduct import foodProduct, nutritional_information
from getFoodProduct import get_product
from pathlib import Path

from rdflib import Graph, URIRef, BNode, Literal
from rdflib.namespace import Namespace, RDF, SDO, XSD

foodGraph = Graph()


def buildKG(fproduct):

    global foodGraph

    # Creating the namespaces
    ex = Namespace('https://example.org/food/')
    food = Namespace('http://data.lirmm.fr/ontologies/food#')
    nutritionalInformation = Namespace(
        'https://schema.org/NutritionInformation#')
    individualProduct = Namespace('https://schema.org/IndividualProduct#')
    allergen = Namespace('http://purl.obolibrary.org/obo/OBI_')
    dbpediaResource = Namespace('http://de.dbpedia.org/resource/')

    schema = SDO
    rdf = RDF
    xsd = XSD

    # Binding the namespaces to a prefix
    foodGraph.bind('', ex)
    foodGraph.bind('food', food)
    foodGraph.bind('individualProduct', individualProduct)
    foodGraph.bind('nutritionInformation', nutritionalInformation)
    foodGraph.bind('allergen', allergen)
    foodGraph.bind('dbr', dbpediaResource)
    foodGraph.bind('schema', schema)
    foodGraph.bind('rdf', rdf)
    foodGraph.bind('xsd', xsd)

    # Creating nodes for the general information
    country = URIRef(dbpediaResource[fproduct.country_of_origin])
    foodproduct = URIRef(ex[fproduct.asin])
    description = Literal(fproduct.description, datatype=xsd['string'])
    name = Literal(fproduct.name, datatype=xsd['string'])
    brand = Literal(fproduct.brand, datatype=xsd['string'])
    price = Literal(fproduct.price, datatype=xsd['string'])
    asin = Literal(fproduct.asin, datatype=xsd['string'])
    url = Literal(fproduct.url, datatype=xsd['string'])
    category = Literal(fproduct.category, datatype=xsd['string'])
    countryName = Literal(fproduct.country_of_origin, datatype=xsd['string'])

    # Adding the nodes for general information
    foodGraph.add((foodproduct, rdf.type, food['FoodProduct']))
    foodGraph.add((foodproduct, individualProduct['description'], description))
    foodGraph.add((foodproduct, individualProduct['name'], name))
    foodGraph.add((foodproduct, individualProduct['brand'], brand))
    foodGraph.add((foodproduct, individualProduct['price'], price))
    foodGraph.add((foodproduct, individualProduct['productID'], asin))
    foodGraph.add((foodproduct, individualProduct['url'], url))
    foodGraph.add((foodproduct, schema['isBasedOn'], url))
    foodGraph.add((foodproduct, individualProduct['category'], category))
    foodGraph.add((foodproduct, individualProduct['countryOfOrigin'], country))
    foodGraph.add((country, schema.name, countryName))

    # Creating nodes for the nuritional information

    nutritionalFacts = BNode(value='nutritional Information of'+fproduct.asin)
    servingSize = Literal(fproduct.nutritional_information.servingSize)
    fats = Literal(fproduct.nutritional_information.fats)
    carbohydrates = Literal(fproduct.nutritional_information.carbohydrates)
    proteins = Literal(fproduct.nutritional_information.protein)

   # Adding the nutritional information
    foodGraph.add((foodproduct, schema['nutrition'], nutritionalFacts))
    foodGraph.add(
        (nutritionalFacts, nutritionalInformation['servingSize'], servingSize))
    foodGraph.add(
        (nutritionalFacts, nutritionalInformation['fatContent'], fats))
    foodGraph.add(
        (nutritionalFacts, nutritionalInformation['proteinContent'], proteins))
    foodGraph.add(
        (nutritionalFacts, nutritionalInformation['carbohydrateContent'], carbohydrates))

    # Adding the ingredients and its subingredients
    ingr = Namespace('https://example.org/food/'+fproduct.asin+'/ingredient/')
    foodGraph.bind('ing', ingr)

    for i in fproduct.ingredients:
        # Creating the nodes for the ingredient
        ingredient = URIRef(ingr[i.ingredient.lower().replace(' ', '')])
        ingredientName = Literal(i.ingredient, datatype=xsd['string'])

        # Adding the ingredient to the graph
        foodGraph.add((foodproduct, food['containsIngredient'], ingredient))
        foodGraph.add((ingredient, schema['name'], ingredientName))

        if i.subingredient:

            # Creating the nodes for the subingredients
            for sub in i.subingredient:
                subing = URIRef(ingr[sub.lower().replace(' ', '')])
                subIngredientName = Literal(sub, datatype=xsd['string'])

                # Adding subingredients of an ingredient
                foodGraph.add((ingredient, food['containsIngredient'], subing))
                foodGraph.add((subing, schema['name'], subIngredientName))

    # Adding the allergens
    for a in fproduct.allergen:
        allergy = URIRef(ingr[a.lower().replace(' ', '')])
        foodGraph.add((allergy, rdf.type, allergen['1110201'],))


def serializeGraph():
    foodGraph.serialize('foodGraph.ttl', format='ttl')


# Fetching the url
def get_url():
    while 1:
        url = str(input('\nEnter here the url: \n'))

        if url == '':
            url = ''
            return url

        elif "https://www.amazon.de/"not in url:
            print("not an Amazon URL")
            continue
        else:
            return url


def main():

    # Check if there is a Turtle file
    # if yes, parse this file
    if Path('foodGraph.ttl').is_file():
        exists = True
        foodGraph.parse('foodGraph.ttl')
    else:
        exists = False

   # Fetching the url from the input stream
   # Break the process if enter an empty url
    url = get_url()
    while url != '':
        if exists:
            # Check if the food product is allready in the Knowledge Graph
            # if yes, ingnore this url
            # else, fetch all information to this product and add it to the KG
            node = Literal(url, datatype=XSD['string'])
            if not (None, None, node) in foodGraph:
                f = get_product(url)
                buildKG(f)
        else:
            f = get_product(url)
            buildKG(f)

        serializeGraph()
        url = get_url()


if __name__ == '__main__':
    main()
