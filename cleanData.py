
from os import remove
from rdflib import Graph, URIRef, BNode, Literal
from rdflib.namespace import Namespace, RDF, SDO, XSD, RDFS, URIPattern

foodGraph = Graph()

def serializeGraph():
    foodGraph.serialize('foodGraph.ttl', format='ttl')

def removeMissingData():

    # Removing missing data --> indicated with None or none
    # Removing unsed blank node for the nutritions
    for s,p,o in foodGraph:
        if 'None' in o or 'none' in o:
            foodGraph.remove((s,p,o))
            foodGraph.remove((o,None,None))

    for s,p,o in foodGraph:
        if type(o) is BNode and not((o,None,None)in foodGraph):
            foodGraph.remove((s,p,o))
    

    
    
def removeUncessaryData():

    print('\nRemoving unnecessary data from the ingredients')
    while 1: 
        s=None
        o=str(input('Enter the unneccesarry ingredient: '))

        
        if o =='':
             break
    
        o=Literal(o,datatype=XSD['string'])
        if o in foodGraph.objects():

            for (sub,pre,obj) in foodGraph:
                if obj==o:
                    s=sub
                    break

            foodGraph.remove((s,None,None))
            foodGraph.remove((None,None,s))
        else:
            print('ingredient',o.value,'does not exist in KG')


def changeIncorrectData():
    food = Namespace('http://data.lirmm.fr/ontologies/food#')
    print('\n\nRemoving incorrect data from the ingredients')
   
    while 1:
        s=None
        p=None
        old=str(input('Enter the incoorect ingredient: '))

        if old =='':
            break
        
        o=Literal(old,datatype=XSD['string'])

        if o in foodGraph.objects():
            for sub,pre,obj in foodGraph:
                if o==obj:
                    s=sub
                    p=pre
                    break
               
            newO=str(input('Enter the coorect ingredient: '))
            newO=Literal(newO,datatype=XSD['string'])

    

            for sub,pre,obj in foodGraph:
                if obj==s:
                    foodGraph.remove((None,None,s))
                    foodGraph.remove((s,None,None))

                    ingredient=s.rstrip(old.lower().replace(' ',''))
                    ingredient=URIRef(ingredient+newO.value.lower().replace(' ',''))

                    containsIngredient=pre
                    foodproduct=sub

                    foodGraph.add((foodproduct,containsIngredient,ingredient))
                    foodGraph.add((ingredient,RDF.type,food['Ingredient']))
                    foodGraph.add((ingredient,RDFS.label,newO))
                    break
        
        
        else: 
            print('ingredient does not exist')
            continue


def cleanKG():
    global foodGraph
    foodGraph.parse('foodGraph.ttl', format='ttl')

    removeMissingData()
    removeUncessaryData()
    changeIncorrectData()
    serializeGraph()
    print('\n\nfinished Cleaning')

if __name__=='__main__':
    cleanKG()