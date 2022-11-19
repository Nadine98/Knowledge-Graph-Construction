# Knowledge Graph Construction

This is a software implementation for the project _Knowledge Graph Construction_. The project’s goal is to build a Knowledge Graph (KG) about food products sold on Amazon (Germany). For the construction, the Resource Description Framework (RDF) is used

---

&nbsp;

## Installation Steps

1. Open Command Line/ Terminal and navigate to a preferred folder
2. Clone git-repository:

   - `git clone https://github.com/Nadine98/Knowledge-Graph-Construction.git`

3. Install the [WebDriver for Chrome](https://chromedriver.chromium.org/downloads) according to your Chrome version
4. In the function `get_soup(url)` (**Foodproduct.py**) change the variable `executable_path` to the path of the execution file (.exe) of the Chrome Web Driver.

5. To prevent version conflicts, it is recommended to use the virtual environment **env** which is provided by **environment.yaml**.
   - For the set up you need the latest version of [Anaconda](https://www.anaconda.com/products/distribution) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) and the following command line/ terminal commands
   - `conda env create -f environment.yaml`
   - `conda activate env`

---

&nbsp;

## Program Execution

- After the Set up, the program can be executed by the following command `python BuildKG.py`

- During the execution, the program asks you to enter an URL of a food product that is sold on Amazon. This entry causes the execution of the program **getFoodProduct.py**, it extracts the HTML code of the web page and scraps all the necessary product information. After the data extraction, the program BuildKG.py creates the knowledge graph and exports it into a Turtle file **foodGraph.ttl**. This whole procedure is repeated until the user enters an empty URL. In this case, the Data Cleaning program (cleanData.py) will be executed. This program interact with the user in the way it takes the user’s input to modify or remove data from the knowledge graph.

- The software implementation includes four programs:
  - **BuildingKG.py**: Main Program for building the knowledge graph
  - **getFoodProduct.py**: Program for scraping the product’s information from Amazon
  - **cleanData.py**: Program for cleaning the data in the knowledge graph
  - **FoodProduct.py**: Program includes helpful classes

---

&nbsp;

## Documentation of BuildingKG.py

### Library RDFLib

- is a Python library for working with RDF and creating the knowledge graph
- The used Objects from RDFLib
  > - `graph=Graph()` creates a container object for storing the triples/statments
  > - `Namespace()` is for creating namespaces
  > - `URIRef()` is a node where the exact URI is known
  > - `BNode()` is a node where the exact URI is not known
  > - `Literal()` is a node that represents attribute values
- The used Methods of Graph()
  > - `graph.add()` is for storing the triples in the graph
  > - `graph.bind` is for binding a namespace to a prefix
  > - `graph.subjects()` extracts all subjects from the graph
  > - `Graph.objects()` extracts all objects from the graph
  > - `graph.predicates()` extracts all predicates from the graph
  > - `graph.serialize()` is for storing the graph in a file
  > - `graph.parse()` is for reading and loading an existing rdf graph in a program

&nbsp;

### Functions in BuildingKG.py

| Function                   | Description                                                                                                                                                                                                              | Return value |
| :------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------- |
| `buildGraph()`             | is the first executed function. It runs the other functions which are necessary for the KG's creation. In order to avoid duplicates this function also checks if a specific product (by its URL) is already in the graph | No value     |
| `get_url()`                | This function asks the user to enter an URL. Thereby it checks whether the URL is an Amazon URL or not. This URL will be used in the function `get_product(url)`                                                         | Entered URL  |
| `addfoodProduct(fproduct)` | The function addfoodProduct adds a food product and its information into the graph                                                                                                                                       | No value     |
| `serializeGraph()`         | A function for saving the graph as a ttl file                                                                                                                                                                            | No value     |

---

&nbsp;

## Documentation getFoodProduct.py

### Libraries

- Selenium

  - is for controlling and automating a web browser by using a webdriver (ChromeDriver)
  - The used objects
    > - `driver=webdriver.Chrome ('C:\Program Files (x86)\chromedriver.exe)'` for creating an instance of Chrome WebDriver
  - The used methods
    > - `driver.get(url)` navigates the Chrome browser to the given URL
    > - `driver.page_source()` gives the HTML code of the website
    > - `driver.quit()` closes the browser and shuts down the ChromeDriver

- Beautiful Soup
  - for scraping information from websites
  - The used object
    > - `soup=BeautifulSoup(source, 'html.parser')` creates an instance of BeautifulSoup. This instance contains the parsed HTML code (here in source)
  - The used methods
    > - `soup.find()` finds a certain tag
    > - `soup.find_all()` finds all elements of a specific tag typ
    > - 'soup.find_parent()' finds the parent tag of a tag

&nbsp;

### Functions in getFoodProduct.py

| Function                           | Description                                                                                                                                                                                                                                                                                                                                                                   | Return value             |
| :--------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------- |
| `get_product(url)`                 | This function will be executed first if you run the program getFoodProduct.py. It executes the necessary functions in an specific order. These functions return the scraped information from the Amazon websites. Any information will be stored into an object `foodproduct` which is an instance of the classe `foodProduct`                                                | `foodproduct`            |
| `get_ASIN(url)`                    | It extracts the ASIN from the URL and saves it into the variable `asin`                                                                                                                                                                                                                                                                                                       | `asin`                   |
| `get_soup(url)`                    | This function uses the ChromeDriver to fetch and parse the HTML code from the Amazon webpage. The parsed HTML code will be saved it into a variable `soup`.This variable is used as the input of the follow up functions.                                                                                                                                                     | `soup`                   |
| `name(soup)`                       | This function extracts the product's name from a tag that has the id='productTitle'. The name of the product will be saved in the variable `name`                                                                                                                                                                                                                             | `name`                   |
| `description(soup)`                | This function extracts the product's description from a tag that has the id='productTitle'. The description of the product will be saved in the variable `description`                                                                                                                                                                                                        | `description`            |
| `price(soup)`                      | This function extracts the product's price from a tag span with the class= 'a-offscreen'. The price of the product will be saved in the variable `price`                                                                                                                                                                                                                      | `price`                  |
| `brand(soup)`                      | This function extracts the product's brand from the table 'Allgemeine Produktinformationen'. The brand is located in the second column of a table row that has the first column entry 'Marke'. The brand of the product will be saved in the variable `brand`                                                                                                                 | `brand`                  |
| `country(soup)`                    | This function extracts the product's origin from a table 'Allgemeine Produktinformationen'. The origin is located in the entry of the second table column of a row that has the first column entry 'Ursprungsland' or 'Herkunftsland'. The origin of the product will be saved in the variable `country`                                                                      | `country`                |
| `nutritionalInformation(soup)`     | It extracts the product's nutritional information from the table 'Nährwertangaben'. The nutritional information are located in the table rows that have the column entries 'Portionsgröße', 'Fett', 'Kohlenhydrate' and 'Eiweiß'. The nutritional information will be saved in an object `nutritionalInformation` which is an instance of the class `nutritional_information` | `nutritionalInformation` |
| `amazon_category(soup)`            | This function extracts the Amazon category from the breadcrumbs which are links of the categories on Amazon. The category will be saves in the variable `category`                                                                                                                                                                                                            | `category`               |
| `ingredients(soup)`                | This function extracts the ingredients from the food product which are located in a section 'Bestandteile' on the wegpage. The ingredients will stored in a list `ingredients`.                                                                                                                                                                                               | `ingredients`            |
| `allergens(soup, foodIngredients)` | It extracts the allergens from the scraped ingredients and the allery table and stores them into the variable `allergens`                                                                                                                                                                                                                                                     | `allergens`              |
| `reviewNumber(soup)`               | It scraps the number of reviews the tag span with id='acrCustomerReviewText' and saves this into the variable `reviewNumber`                                                                                                                                                                                                                                                  | `reviewNumber`           |
| `rating(soup)`                     | It extracts the star rating from the tag span with the class='a-icon-alt' and saves this into `review_score`                                                                                                                                                                                                                                                                  | `review_score`           |

---

&nbsp;

## Documentation cleanData.py

### Functions in cleanData.py

| Function                | Description                                                                                                                                                                    |
| :---------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `def cleanKG()`         | This is the main function that executes the others functions in a patricular order                                                                                             |
| `removeMissingData()`   | This function removes alle nodes indicates with 'None' or 'none'                                                                                                               |
| `removeUncessaryData()` | It removes uncessary and incorrect ingredients                                                                                                                                 |
| `changeIncorrectData()` | It modifies incorrect ingredients                                                                                                                                              |
| `get_asin()`            | This function is used in `removeUncessaryData()` and `changeIncorrectData()`. It fetchs the product's ASIN to identify the namespace of an ingredient that has sub-ingredients |

---

&nbsp;

## Documentation FoodProduct.py

### 1. Class foodProduct

- The class `foodProduct` represents a food product from Amazon. It contains private attributes and methods. Some attributes are instances of the class `nutritional_information` and the class `foodIngredient`

- The classe's attributes

  > | Attributes                | Datatyp                               |
  > | :------------------------ | :------------------------------------ |
  > | `name`                    | string                                |
  > | `description`             | string                                |
  > | `brand`                   | string                                |
  > | `price`                   | string                                |
  > | `asin`                    | string                                |
  > | `url`                     | string                                |
  > | `category`                | string                                |
  > | `country_of_origin`       | string                                |
  > | `ingredients`             | list of instances of `foodIngredient` |
  > | `allergen`                | list of strings                       |
  > | `nutritional_information` | `nutritional_information`             |
  > | `reviewNumber`            | unsigned integer                      |
  > | `rating`                  | string                                |

- Types of methods:
  > | Type of methods | Defintion          | Description                                                                     |
  > | :-------------- | :----------------- | :------------------------------------------------------------------------------ |
  > | Getter methods  | `get*Attribute*()` | For each attribute exits a getter method. It returns the value of the attribute |
  > | Setter methods  | `set*Attribute*()` | For each attribute exits a setter method. It sets the value of the attribute    |

&nbsp;

### 2. Class foodIngredient

- This class is used to store the ingredients and their sub-ingredients in a compact way. It has public attributes and methods

- The classe's attributes
  > | Attributes        | Datatyp         |
  > | :---------------- | :-------------- |
  > | `ingredient`      | string          |
  > | `sub-ingredients` | list of strings |
- Types of methods:
  > | Type of methods | Defintion          | Description                                                                  |
  > | :-------------- | :----------------- | :--------------------------------------------------------------------------- |
  > | Setter methods  | `set*Attribute*()` | For each attribute exits a setter method. It sets the value of the attribute |

&nbsp;

### 3. Class nutritional_information

- This class is used to store the nutritional information (serving size, protein, fat, carbohydrates). It has public attributes and methods

- The classe's attributes

  > | Attributes     | Datatyp |
  > | :------------- | :------ |
  > | `servingSize`  | string  |
  > | `fat`          | string  |
  > | `carbohydrate` | string  |
  > | `protein`      | string  |

- Types of methods:
  > | Type of methods | Defintion          | Description                                                                  |
  > | :-------------- | :----------------- | :--------------------------------------------------------------------------- |
  > | Setter methods  | `set*Attribute*()` | For each attribute exits a setter method. It sets the value of the attribute |

---

&nbsp;

## Documentation foodGraph.ttl

The created RDF graph is composed of triple statements that have the from <subject\> <predicate\> <object\>. The knowledge graph is serialized in Turtle (Terse RDF Triple Language).

&nbsp;

## Turtle

| synatax                            | Definition                                                                                                                                  |
| :--------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------ | --- |
| `<subject> <predicate> <ocject> .` | Is the triple structure of a statement                                                                                                      |
| `;`                                | Is used for statments that share the same subject. The first statement ends with it and the following statements follow without the subject |
| `,`                                | Is used for statements that share the same suject and predicate. The object are seperated by a comma                                        |     |
| `a`                                | Is a abbrevation of the predicate rdf:type (is_a)                                                                                           |
| `:`                                | Is used if an URI is abbrevated through a CURI                                                                                              |

&nbsp;

## URI

- URI is used for locating a resource of a subject, predicate or an object
- An URI is serialized by enclosing it in angle brackets < https://example.org\>

&nbsp;

## CURI

- CURI is a synatax for abbrevating URIs.
- CURI's Declaration

  > | @PREFIX | 'abbreviation' | :   | \< URI \> |
  > | :------ | :------------- | :-- | :-------- |

- CURIs in the Turtle File

  > | CURIs                                                                                    | Description                                                                                          |
  > | :--------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------- |
  > | @prefix : \< https://example.org/food/ \> .                                              | A CURI for all food products in the knowledge graph                                                  |
  > | @prefix dbr: \< http://dbpedia.org/resource/ \> .                                        | A CURI for all resources form dbpedia                                                                |
  > | @prefix dbp: \< http://dbpedia.org/property/ \> .                                        | A CURI for all properties form dbpedia                                                               |
  > | @prefix food: \< http://data.lirmm.fr/ontologies/food# \> .                              | A CURI for all resources from the ontology _food_                                                    |
  > | @prefix ing: \< https://example.org/food/ingredient/ \> .                                | A CURI for all ingredients without sub-ingredients                                                   |
  > | @prefix ingWithSub**I**: \<https://example.org/food/*ProductASIN*/ingredient/ \> . (I∈ℕ) | A CURI for ingredients (with sub-ingredients) of a sprecific food product (identified through ASIN). |
  > | @prefix ip: \< https://schema.org/IndividualProduct# \> .                                | A CURI for all properties from the ontology _Schema.org/IndividualProduct_                           |
  > | @prefix ni: \< https://schema.org/NutritionInformation# \> .                             | A CURI for all properties from the ontology _Schema.org/NutritionInformation_                        |
  > | @prefix rdfs: \< http://www.w3.org/2000/01/rdf-schema# \> .                              | A CURI for every usage of the RDF-Schema                                                             |
  > | @prefix schema: \< http://schema.org/ \> .                                               | A CURI for all resources and properties from the ontolgy _Schema.org_                                |
  > | @prefix xsd: \< http://www.w3.org/2001/XMLSchema# \> .                                   | A CURI for every usage of the XML Schema                                                             |
