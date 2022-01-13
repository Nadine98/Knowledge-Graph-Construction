from bs4 import BeautifulSoup
from selenium import webdriver
import re
from googletrans import Translator

from FoodProduct import foodProduct
from FoodProduct import nutritional_information

# Extract the rating_score from the tag span with class='a-icon-alt'


def rating(soup):
    try:
        review_score = soup.find(
            'span', attrs={'class': 'a-icon-alt'}).text.strip()
        if 'Sternen' not in review_score:
            review_score = 'None'
    except:
        review_score = 'None'
    return review_score


# Extract the number of reviews from the tag span with id='acrCustomerReviewText'
def reviewNumber(soup):
    try:
        reviewNumber = soup.find(
            'span', attrs={'id': 'acrCustomerReviewText'}).text.strip().replace('.', '')
        reviewNumber = re.findall(r'\d+', reviewNumber)[0]

    except:
        reviewNumber = 'None'

    return reviewNumber


# Extract the allergens from the allergy table
def allergies_table(soup):

    allergen = 'None'

    info = soup.find("th", text=" Allergie-Informationen ")
    if info:
        allergen = list()
        content = info.find_parent('tr').select("td")[0].text

        if 'Kann' in content:
            content = content.replace('Kann', '')
            content = content.replace('enthalten', '')

        if ":" in content:
            allergen = [x.strip() for x in content.split(":")[1].split(",")]
        else:
            allergen = [x.strip() for x in content.split(",")]

    return allergen


# Extract the allergens from the ingredients
def allergens(soup, foodIngredients):
    allergen = list()

    if foodIngredients == 'None':
        allergen = 'None'
        return allergen

    # Searching for ingredient with capital letters
    for ingredient in foodIngredients:

        # For the German Umlaute
        ingr = ingredient.ingredient.replace(
            'Ä', 'AE').replace('O', 'OE').replace('Ü', 'UE')

        if re.search('.[A-Z][A-Z][A-Z]+.', ingr):
            allergen.append(ingredient.ingredient)

        # Search for allergens in the sub-ingredients
        if ingredient.subingredient:
            for sub in ingredient.subingredient:
                # for the German Umlaute
                subingr = sub.replace('Ä', 'AE').replace(
                    'O', 'OE').replace('Ü', 'UE')
                if re.search('.[A-Z][A-Z][A-Z]+.', subingr):
                    allergen.append(sub)

    # Search for further allergens in the allergy table
    table = allergies_table(soup)

    if table != 'None':
        for a in table:
            notIN = False

            for i in foodIngredients:

                # Check if the allergen from the table is in the ingredient list
                if a.lower() in i.ingredient.lower():
                    notIN = True

                    # if the allergen is in the ingredients then check if it not already in the allergen list
                    if not (i.ingredient in allergen):
                        allergen.append(i.ingredient)

            # Repeat this process for the sub-ingredients
                if i.subingredient != list():
                    for sub in i.subingredient:
                        if a.lower() in sub.lower():
                            notIN = True
                            if not (sub in allergen):
                                allergen.append(sub)

            # if the allergen is not a part of the ingredients, then added to the list
            if notIN == False:
                allergen.append(a)

    return allergen


# Extract ingredients from the text 'Bestandteile'
def ingredients(soup):

    ingredients = 'None'
    info = soup.find("h4", text="Bestandteile")

    if info:
        contents = info.find_parent('div').find_all('p')[1].text

        # Variable for storing an ingredient
        ingredient = ''
        # List for storing the ingredients
        ingredients = list()
        # List for the sub-ingredients of an ingredient --> first element is the ingredient and the follow up elements are the sub-ingredients
        subingredients = list()
        # Variable for counting the brackets
        x = 0

# -------------------------------------------------------------------------------------------------------------------------------------------------

        # Remove/Change words and characters from the ingredient list to create an unified structure

        # In the ingredient list, each ingredient is separated by a comma --> e.g. Mehl, Zucker, Wasser,...
        # The sub-ingredients of in ingredient are between round brackets --> e.g. Sauerteig (Weizenmehl,Roggenmehl)

        if 'Kann' in contents:
            contents = contents.replace('(Kann', ',')
            contents = contents.replace('Kann', '')
            contents = contents.replace('enthalten', '')
            contents = contents.replace('andere', '')

        if 'Zutaten:' in contents:
            contents = contents.replace('Zutaten:', '')

        if '[' and ']' in contents:
            contents = contents.replace('[', '(')
            contents = contents.replace(']', ')')
        if '{' and '}' in contents:
            contents = contents.replace('{', '(')
            contents = contents.replace('}', ')')
        if ';' in contents:
            contents = contents.replace(';', ',')
        if '.' in contents:
            contents = contents.replace('.', '')
        if '*' in contents:
            contents = contents.replace('*:', '')
        if 'und ' in contents:
            contents = contents.replace('und', ',')
        if 'aus ' in contents:
            contents = contents.replace('aus ', ':')
        if 'mit ' in contents:
            contents = contents.replace('mit ', '')
        if 'von ' in contents:
            contents = contents.replace('von ', '')
        if 'mindestens ' in contents:
            contents = contents.replace('mindestens ', '')
        if 'enthält ' in contents:
            contents = contents.replace('enthält', '')
        if 'gemahlen' in contents:
            contents = contents.replace('gemahlen', '')
        if 'gehackt' in contents:
            contents = contents.replace('gehackt', '')

        # Remove the percentages
        contents = re.sub(
            r'(\d+%|\d+.\d+%|\d+ %|\d+.\d+ %|\d+Prozent|\d+.\d+Prozent|\d+ Prozent|\d+.\d+ Prozent)', '', contents)
        contents = re.sub(r'[(][)]|[(] [)]', '', contents)

# -------------------------------------------------------------------------------------------------------------------------------

        # Extract the ingredients by reading every single character from the ingredient list
        for index, content in enumerate(contents):

            # Ignore the word before ':'
            if content == ':':
                ingredient = ''

            # Each character is stored in the variable ingredient
            elif (content != ',' and x <= 1) and (content != '(' and content != ')'):
                ingredient = ingredient+content

            # Store the ingredients in a ingredient list
            elif content == ',' and x == 0:
                ingredients.append(ingredient.strip())
                ingredient = ''

            # Store the sub-ingredients in a list
            elif content == ',' and x == 1:
                subingredients.append(ingredient.strip())
                ingredient = ''

            elif content == '(' and x == 0:

                subingredients.append(ingredient.strip())
                ingredient = ''
                x = 1
            elif content == ')' and x == 1:

                subingredients.append(ingredient.strip())
                ingredients.append(subingredients)

                ingredient = ''
                subingredients = list()
                x = 0

            # Ignore the brackets and its content if the brackets are listed in the sub-ingredients
            elif content == '(' and x >= 1:
                x += 1
            elif content == ')' and x > 1:
                x -= 1

        # Add the last ingredient if is not in the list
        if ingredient not in ingredients:
            ingredients.append(ingredient.strip())

        # Remove the empty entries
        ingredients = [x for x in ingredients if x]

        # Remove empty lists
        for i, x in enumerate(ingredients):
            if type(x) is list and ('' in x or ' ' in x):
                ingredients.remove(x)

    return ingredients


#  Extract the category from the breadcrumbs/ path of links
def amazon_category(soup):

    category = 'None'

    info = soup.find('div', attrs={'id': 'showing-breadcrumbs_div'})
    if info:
        info = info.find(
            'ul', attrs={'class': 'a-unordered-list a-horizontal a-size-small'})

        if info:
            list = info.find_all('li')

            for index, value in enumerate(list):
                if 'Lebensmittel & Getränke' in value.text:
                    # list[index]='Lebensmittel & Getränke'
                    # list[index+1]= '>'
                    # list[index+2]='Süßigkeiten & Knabbereien'
                    category = list[index+2].text.strip()
                    break

    return category

# Extract the nutritional information from a table with the headline 'Nährwertangaben'
# In the table rows with the content 'Portionsgröße', 'Fett', 'Kohlenhydrate' and 'Eiweiß'


def nutritionalInformation(soup):
    nutritionalInformation = nutritional_information()
    info = soup.find('h5', text='Nährwertangaben')

    if info:
        table_rows = info.find_parent('div').table.find_all('tr')

        for td in enumerate(table_rows):

            if 'Portionsgröße' in td[1].text:
                nutritionalInformation.setServingSize(
                    table_rows[td[0]].td.text.strip().replace('\u200e', ''))

            if 'Fett' in td[1].text:
                nutritionalInformation.setFats(
                    table_rows[td[0]].td.text.strip().replace('\u200e', ''))

            if 'Kohlenhydrate' in td[1].text:
                nutritionalInformation.setCarbohydrates(
                    table_rows[td[0]].td.text.strip().replace('\u200e', ''))

            if 'Eiweiß' in td[1].text:
                nutritionalInformation.setProteins(
                    table_rows[td[0]].td.text.strip().replace('\u200e', ''))

    return nutritionalInformation


# Extract the country from a table with the headline 'Allgemeine Produktinformationen'
# In the table row with the content 'Ursprungsland' or 'Herkunftsland'
def country(soup):
    trans = Translator()

    country = 'None'
    info = soup.find('h5', text='Allgemeine Produktinformationen')

    if info:
        table_rows = info.find_parent('div').table.find_all('tr')

        for td in enumerate(table_rows):
            if 'Ursprungsland' in td[1].text or 'Herkunftsland' in td[1].text:
                country = table_rows[td[0]].td.text
                country = country.replace('\u200e', '').strip()

                country = trans.translate(country, dest='de').text

                break

        if country == 'Vereinigte Staaten':
            country = 'USA'
        if country == 'Vereinigte Königreich' or country == 'Vereinigtes Königreich':
            country = 'UK'

    return country


# Extract the brand from a table with the headline 'Allgemeine Produktinformationen'
# In the table row with the content 'Marke'
def brand(soup):
    info = soup.find('h5', text='Allgemeine Produktinformationen')

    if info:
        table_rows = info.find_parent('div').table.find_all('tr')

        for td in enumerate(table_rows):
            if 'Marke' in td[1].text:
                brand = table_rows[td[0]].td.text
                brand = brand.replace('\u200e', '').strip()
    else:
        brand = 'None'

    return brand


# Extract the product's price from the tag span with the class= 'a-offscreen'
def price(soup):
    try:
        price = soup.find(
            'span', attrs={'class': 'a-offscreen'}).text.strip()
        if not('€' in price):
            price = 'None'
    except:
        price = 'None'

    return price


# Extract the product's description from the tag with the id='productTitle'
def description(soup):
    try:
        description = soup.find(id='productTitle').get_text().strip()
    except:
        description = 'None'

    return description


# Extract the product's name from the tag with the id='productTitle'
def name(soup):

    try:
        name = soup.find(id='productTitle').get_text().strip()
        if ',' in name:
            name = name.split(',')[0]
        if '-' in name:
            name = name.split('-')[0]
        if '–' in name:
            name = name.split('–')[0]
        if '(' in name:
            name = name.split('(')[0]
        if '|' in name:
            name = name.split('|')[0]
        if '-' in name:
            name = name.split('-')[0]

    except:
        name = 'None'

    return name


def get_soup(url):

    # Using the chrome webdriver to fetch the HTML code
    driver = webdriver.Chrome(
        executable_path='C:\Program Files (x86)\chromedriver.exe')
    driver.get(url)

    # Store the HTML-Code into a variable
    source = driver.page_source

    # Close the Browser
    driver.quit()

    # Parse the HTML Code in individual parts (or HTML nodes)
    soup = BeautifulSoup(source, 'html.parser')

    return soup


# Extract the ASIN fromt the product's URL
def get_ASIN(url):
    asin = url.split('/dp/')[1]
    asin = asin[:10]
    return asin


# Extract the food product and its information
def get_product(url):

    foodproduct = foodProduct()

    foodproduct.setUrl(url)
    foodproduct.setAsin(get_ASIN(foodproduct.getUrl()))

    soup = get_soup(foodproduct.getUrl())

    foodproduct.setName(name(soup))
    foodproduct.setDecription(description(soup))
    foodproduct.setPrice(price(soup))
    foodproduct.setBrand(brand(soup))
    foodproduct.setCountry(country(soup))
    foodproduct.setNritional_information(nutritionalInformation(soup))
    foodproduct.setCategory(amazon_category(soup))
    foodproduct.setReviewNumber(reviewNumber(soup))
    foodproduct.setRating(rating(soup))
    foodproduct.setIngredients(ingredients(soup))

    # If there aren't ingredients then extraxt the allergens from the allergy table 
    # and add the allergens to the ingredients
    if foodproduct.getIngredients() == 'None':
        foodproduct.setAllergens(allergies_table(soup))
        if foodproduct.getAllergens() != 'None':
            foodproduct.setIngredients(foodproduct.getAllergens())

    # If there are ingredients then extraxt the allergens from the ingredient list and the allergy table
    # and add the allergens to the ingredient list if they are not inside it
    else:
        foodproduct.setAllergens(allergens(soup, foodproduct.getIngredients()))
        for a in foodproduct.getAllergens():
            if not(foodproduct.findIngredient(a)):
                foodproduct.addAllergenToIngredients(a)

    return foodproduct
