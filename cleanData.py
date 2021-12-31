from rdflib import Graph, URIRef, BNode, Literal
from rdflib.namespace import Namespace, RDF, XSD, RDFS

foodGraph = Graph()


def serializeGraph():
    foodGraph.serialize('foodGraph.ttl', format='ttl')


def get_asin():
    asin=str(input('Enter the ID of the product that has to be changed\nID='))
    return asin

def removeMissingData():

    # Removing missing data --> indicated with None or none
    # Removing unsed blank node for the nutritions
    for s, p, o in foodGraph:
        if 'None' in o or 'none' in o:
            foodGraph.remove((s, p, o))
            foodGraph.remove((o, None, None))

    for s, p, o in foodGraph:
        if type(o) is BNode and not((o, None, None) in foodGraph):
            foodGraph.remove((s, p, o))

    serializeGraph()


def removeUncessaryData(asin):
    food = Namespace('http://data.lirmm.fr/ontologies/food#')
    product=Namespace('https://example.org/food/')
    ing=Namespace('https://example.org/food/'+asin.strip()+'/ingredient/')

    print('\nRemoving unnecessary data from the ingredients')
    while 1:
        ingredient= str(input('Enter the name of the unneccesarry ingredient: '))

        if ingredient == '':
            break

        ingredient=URIRef(ing[ingredient.lower().replace(' ', '')])        

        if ingredient in foodGraph.subjects():
        
            for (s,p,o) in foodGraph:
             if ingredient==s and p==food['containsIngredient']:

                foodGraph.remove((ingredient, None, None))
                fproduct=URIRef(product[asin.strip()])
                foodGraph.add((fproduct,p,o))
            
             foodGraph.remove((ingredient, None, None))
             foodGraph.remove((None, None, ingredient))
            
            serializeGraph()
        else:
            print('ingredient', ingredient.value, 'does not exist in KG')


def changeIncorrectData(asin):
    food = Namespace('http://data.lirmm.fr/ontologies/food#')
    ing=Namespace('https://example.org/food/'+asin.strip()+'/ingredient/')


    print('\n\nRemoving incorrect data from the ingredients')

    while 1:
    
        ingredientName= str(input('Enter the incoorect ingredient: '))
    
        if ingredientName == '':
            break
        ingredient=URIRef(ing[ingredientName.lower().replace(' ', '')])

    
        if ingredient in foodGraph.subjects():

            newO = str(input('Enter the coorect ingredient: '))
            newIngr=URIRef(ing[newO.lower().replace(' ','')])
            newO = Literal(newO, datatype=XSD['string'])


            # Change the other relations
            for sub, pre, obj in foodGraph:
                if obj == ingredient:
                    foodGraph.remove((sub,pre,obj))
                    foodGraph.add((sub, pre, newIngr))
                   

                if sub==ingredient:

                    if pre==RDFS.label:
                        foodGraph.remove((sub,pre,obj))
                        foodGraph.add((newIngr,pre,newO))

                    elif pre==food['containsIngredient'] or pre==RDF.type:
                        foodGraph.remove((sub,pre,obj))
                        foodGraph.add((newIngr, pre, obj))

            serializeGraph()

        else:
            print('ingredient ', ingredientName, 'does not exist')
            continue


def cleanKG():
    foodGraph.parse('foodGraph.ttl', format='ttl')
    asin=get_asin()
    if asin!='':
        removeMissingData()
        removeUncessaryData(asin)
        changeIncorrectData(asin)
        print('\n\nfinished cleaning')


if __name__ == '__main__':
    cleanKG()
