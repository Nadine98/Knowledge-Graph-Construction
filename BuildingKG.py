
from FoodProduct import foodProduct, nutritional_information
from getFoodProduct import get_product
from pathlib import Path

from rdflib import Graph, URIRef, BNode, Literal
from rdflib.namespace import Namespace, RDF, SDO, XSD, RDFS
foodGraph = Graph()


def addfoodProduct(fproduct):

    global foodGraph

    # Creating the namespaces
    ex = Namespace('https://example.org/food/')
    food = Namespace('http://data.lirmm.fr/ontologies/food#')
    nutritionalInformation = Namespace(
        'https://schema.org/NutritionInformation#')
    individualProduct = Namespace('https://schema.org/IndividualProduct#')
    dbpediaResource = Namespace('http://de.dbpedia.org/resource/')

    schema = SDO
    rdf = RDF
    rdfs = RDFS
    xsd = XSD

    # Binding the namespaces to a prefix
    foodGraph.bind('', ex)
    foodGraph.bind('food', food)
    foodGraph.bind('ip', individualProduct)
    foodGraph.bind('ni', nutritionalInformation)
    foodGraph.bind('dbr', dbpediaResource)
    foodGraph.bind('schema', schema)
    foodGraph.bind('rdf', rdf)
    foodGraph.bind('rdfs', rdfs)
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
    countryName = Literal(fproduct.country_of_origin, lang='de')

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
    foodGraph.add((country, rdfs.label, countryName))

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
        ingredientName = Literal(
            i.ingredient.lower().title(), datatype=xsd['string'])

        # Adding the ingredient to the graph
        foodGraph.add((foodproduct, food['containsIngredient'], ingredient))
        foodGraph.add((ingredient, rdf.type, food['Ingredient']))
        foodGraph.add((ingredient, rdfs.label, ingredientName))

        if i.subingredient:

            # Creating the nodes for the subingredients
            for sub in i.subingredient:
                subing = URIRef(ingr[sub.lower().replace(' ', '')])
                subIngredientName = Literal(
                    sub.lower().title(), datatype=xsd['string'])

                # Adding subingredients of an ingredient
                foodGraph.add((ingredient, food['containsIngredient'], subing))
                foodGraph.add((subing, rdf.type, food['Ingredient']))
                foodGraph.add((subing, rdfs.label, subIngredientName))

    # Adding the class allergen
    allergen = URIRef(dbpediaResource['Allergen'])
    foodGraph.add((allergen, rdfs.label, Literal('Allergen', lang='de')))

    # Adding the allergens from the ingredients
    for a in fproduct.allergen:
        allergy = URIRef(ingr[a.lower().replace(' ', '')])
        foodGraph.add((allergy, rdf.type, allergen))

    # Add the rating and the reviewNumber
    foodGraph.add((foodproduct, schema['ratingValue'], Literal(
        fproduct.rating, datatype=xsd['string'])))
    foodGraph.add((foodproduct, schema['reviewCount'], Literal(
        fproduct.reviewNumber, datatype=xsd['nonNegativeInteger'])))


def serializeGraph():
    foodGraph.serialize('foodGraph.ttl', format='ttl')


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


def buildGraph():

    # Check if there is a Turtle file
    # if yes, parse this file
    if Path('foodGraph.ttl').is_file():
        exists = True
        foodGraph.parse('foodGraph.ttl', format='ttl')
    else:
        exists = False

   # Fetch the url from the input stream
   # Break the process if enter an empty url
    url = get_url()
    while url != '':
        if exists:
            # Check if the food product is allready in the Knowledge Graph
            # if yes, ingnore this product
            # else, fetch all information to this product and add it to the KG
            node = Literal(url, datatype=XSD['string'])
            if not (None, None, node) in foodGraph:
                fp = get_product(url)
                addfoodProduct(fp)
        else:
            fp = get_product(url)
            addfoodProduct(fp)

        serializeGraph()
        url = get_url()


def main():
    buildGraph()


if __name__ == '__main__':
    main()
