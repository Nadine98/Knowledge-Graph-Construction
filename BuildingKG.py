
from getFoodProduct import get_product
from pathlib import Path
from cleanData import cleanKG

from rdflib import Graph, URIRef, BNode, Literal
from rdflib.namespace import Namespace, RDF, SDO, XSD, RDFS

foodGraph = Graph()


def serializeGraph():
    foodGraph.serialize('foodGraph.ttl', format='ttl')


def addfoodProduct(fproduct):

    global foodGraph

    # Create the namespaces
    ex = Namespace('https://example.org/food/')
    food = Namespace('http://data.lirmm.fr/ontologies/food#')
    nutritionalInformation = Namespace(
        'https://schema.org/NutritionInformation#')
    individualProduct = Namespace('https://schema.org/IndividualProduct#')
    dbpediaResource = Namespace('http://dbpedia.org/resource/')


    schema = SDO
    rdf = RDF
    rdfs = RDFS
    xsd = XSD

    # Bind the namespaces to prefixes
    foodGraph.bind('', ex)
    foodGraph.bind('food', food)
    foodGraph.bind('ip', individualProduct)
    foodGraph.bind('ni', nutritionalInformation)
    foodGraph.bind('dbr', dbpediaResource)
    foodGraph.bind('schema', schema)
    foodGraph.bind('rdf', rdf)
    foodGraph.bind('rdfs', rdfs)
    foodGraph.bind('xsd', xsd)

# ------------------------------------ General product information-----------------------------------------

    # Create nodes for the general product information
    country = URIRef(dbpediaResource[fproduct.getCountry()])
    foodproduct = URIRef(ex[fproduct.getAsin()])
    description = Literal(fproduct.getDescription(), datatype=xsd['string'])
    name = Literal(fproduct.getName(), datatype=xsd['string'])
    brand = Literal(fproduct.getBrand(), datatype=xsd['string'])
    price = Literal(fproduct.getPrice(), datatype=xsd['string'])
    asin = Literal(fproduct.getAsin(), datatype=xsd['string'])
    url = Literal(fproduct.getUrl(), datatype=xsd['string'])
    category = Literal(fproduct.getCategory(), datatype=xsd['string'])

    # Add the nodes for general product information
    foodGraph.add((foodproduct, rdf.type, food['FoodProduct']))
    foodGraph.add((foodproduct, individualProduct['description'], description))
    foodGraph.add((foodproduct, individualProduct['name'], name))
    foodGraph.add((foodproduct, individualProduct['brand'], brand))
    foodGraph.add((foodproduct, individualProduct['price'], price))
    foodGraph.add((foodproduct, individualProduct['productID'], asin))
    foodGraph.add((foodproduct, individualProduct['url'], url))
    foodGraph.add((foodproduct, individualProduct['category'], category))
    foodGraph.add((foodproduct, individualProduct['countryOfOrigin'], country))

# ------------------------------------Nutritional information----------------------------------------------------------

    # Create nodes for the nutritional information
    nutritionalFacts = BNode(
        value='nutritional Information of'+fproduct.getAsin())
    servingSize = Literal(fproduct.getNutritional_information().servingSize)
    fats = Literal(fproduct.getNutritional_information().fats)
    carbohydrates = Literal(
        fproduct.getNutritional_information().carbohydrates)
    proteins = Literal(fproduct.getNutritional_information().protein)

    # Add the nutritional information to the graph
    foodGraph.add((foodproduct, schema['nutrition'], nutritionalFacts))
    foodGraph.add(
        (nutritionalFacts, nutritionalInformation['servingSize'], servingSize))
    foodGraph.add(
        (nutritionalFacts, nutritionalInformation['fatContent'], fats))
    foodGraph.add(
        (nutritionalFacts, nutritionalInformation['proteinContent'], proteins))
    foodGraph.add(
        (nutritionalFacts, nutritionalInformation['carbohydrateContent'], carbohydrates))


# ------------------------------------ Ingredients and sub-ingredients-------------------------------------------------------

    ingr = Namespace('https://example.org/food/ingredient/')

    # For sub-ingredients use the Namespace --> 'https://example.org/food/'+fproduct.getAsin()+'/ingredient/'
    ingrWithSubs = Namespace(
        'https://example.org/food/'+fproduct.getAsin()+'/ingredient/')

    foodGraph.bind('ing', ingr)
    foodGraph.bind('ingWithSub', ingrWithSubs)

    if fproduct.getIngredients() != 'None':

        for i in fproduct.getIngredients():

            # if an ingredient has sub-ingredients then use the Namespace ingrWithSub
            if i.subingredient:
                ingredient = URIRef(
                    ingrWithSubs[i.ingredient.lower().replace(' ', '')])

            # Else use ingr Namespace
            else:
                ingredient = URIRef(
                    ingr[i.ingredient.lower().replace(' ', '')])

            ingredientName = Literal(
                i.ingredient.lower().title(), datatype=xsd['string'])

            # Add the ingredient to the graph
            foodGraph.add(
                (foodproduct, food['containsIngredient'], ingredient))
            foodGraph.add((ingredient, rdf.type, food['Ingredient']))
            foodGraph.add((ingredient, rdfs.label, ingredientName))

            # Add the sub-ingredients
            if i.subingredient:

                # Create the nodes for the sub-ingredients
                for sub in i.subingredient:
                    subing = URIRef(ingr[sub.lower().replace(' ', '')])
                    subIngredientName = Literal(
                        sub.lower().title(), datatype=xsd['string'])

                    # Add sub-ingredients to the KG
                    foodGraph.add(
                        (ingredient, food['containsIngredient'], subing))
                    foodGraph.add((subing, rdf.type, food['Ingredient']))
                    foodGraph.add((subing, rdfs.label, subIngredientName))


# ------------------------------------ Allergens --------------------------------------------------

        if fproduct.getAllergens() != 'None':

            allergen = URIRef(dbpediaResource['Allergen'])

            # Add the allergens in the KG
            for a in fproduct.getAllergens():
                allergy = URIRef(ingr[a.lower().replace(' ', '')])
                foodGraph.add((allergy, rdf.type, allergen))


# ------------------------------------ Rating and the ReviewNumber --------------------------------------

    foodGraph.add((foodproduct, schema['ratingValue'], Literal(
        fproduct.getRating(), datatype=xsd['string'])))
    foodGraph.add((foodproduct, schema['reviewCount'], Literal(
        fproduct.getReviewNumber(), datatype=xsd['nonNegativeInteger'])))
# ----------------------------------------------------------------------------------------------


def get_url():
    while 1:
        url = str(input('\nEnter here the url: \n'))

        if "https://www.amazon.de/"not in url and url != '':
            print("not an Amazon URL")
            continue

        return url


def buildGraph():

    # Check if a Turtle file exists
    # if yes, parse this file
    if Path('foodGraph.ttl').is_file():
        exists = True
        foodGraph.parse('foodGraph.ttl', format='ttl')
    else:
        exists = False

    while 1:

        # Fetch the url from the input stream
        # Break the process if the user enter an empty url
        url = get_url()

        if url == '':
            break

        # if the KG exists, then check if the food product is already in the Knowledge Graph
        # if yes, skip this url
        # else, fetch all information to this product and add it to the KG
        node = Literal(url, datatype=XSD['string'])
        if exists and (None, None, node) in foodGraph:
            continue

        fp = get_product(url)
        addfoodProduct(fp)
        serializeGraph()

    # After adding food product into the KG start the Data Cleaning
    cleanKG()


def main():
    buildGraph()


if __name__ == '__main__':
    main()
