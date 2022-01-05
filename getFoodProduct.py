from bs4 import BeautifulSoup
from selenium import webdriver

import re
from googletrans import Translator

from FoodProduct import foodProduct
from FoodProduct import nutritional_information


def rating(soup):
    try:
        review_score = soup.find(
            'span', attrs={'class': 'a-icon-alt'}).text.strip()
        if 'Sternen' not in review_score:
            review_score = 'None'
    except:
        review_score = 'None'
    return review_score


def reviewNumber(soup):
    try:
        reviewNumber = soup.find(
            'span', attrs={'id': 'acrCustomerReviewText'}).text.strip().replace('.', '')
        reviewNumber = re.findall(r'\d+', reviewNumber)[0]

    except:
        reviewNumber = 'None'

    return reviewNumber


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


def allergens(soup, foodIngredients):
    allergen = list()

    if foodIngredients == 'None':
        allergen = 'None'
        return allergen

    for ingredient in foodIngredients:

        if re.search('.[A-Z][A-Z][A-Z]+.', ingredient.ingredient):
            allergen.append(ingredient.ingredient)

        if ingredient.subingredient:
            for sub in ingredient.subingredient:
                if re.search('.[A-Z][A-Z][A-Z]+.', sub):
                    allergen.append(sub)

   
    
    table = allergies_table(soup)

    if table !='None':
        for a in table:
            notIN = False

            # check if the allergen from the table is included in the ingredient list 
            # is a substring of the ingredient
            for i in foodIngredients:
                if a.lower() in i.ingredient.lower():
                    notIN = True
                    allergen.append(i.ingredient)

            # Check also this in the subingredients 
                if i.subingredient != list():
                    for sub in i.subingredient:
                        if a.lower() in sub.lower():
                            notIN = True
                            allergen.append(sub)
            # if the allergen is not a part of an ingredient, then added to the list 
            if notIN == False:
                allergen.append(a)


    return allergen


# Extract ingredients Bestandteile
def ingredients(soup):

    ingredients = 'None'
    info = soup.find("h4", text="Bestandteile")

    if info:
        contents = info.find_parent('div').find_all('p')[1].text

        # storing an ingredient --> Character by character
        ingredient = ''
        # List for storing the ingredients
        ingredients = list()
        # List for subingredients of an ingredient
        subingredients = list()
        # Variable for counting the brackets
        x = 0

        if 'Kann' in contents:
            contents = contents.replace('(Kann', ',')
            contents = contents.replace('Kann', '')
            contents = contents.replace('enthalten', '')
            contents = contents.replace('andere', '')

        # Removing unneccary words and characters and words
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

        # Removing the percentages
        contents = re.sub(
            r'(\d+%|\d+.\d+%|\d+ %|\d+.\d+ %|\d+Prozent|\d+.\d+Prozent|\d+ Prozent|\d+.\d+ Prozent)', '', contents)
        contents = re.sub(r'[(][)]|[(] [)]', '', contents)

        # Extracting the ingredients by reading character by character
        for index, content in enumerate(contents):

            if content in '*':
                continue

            elif content == ':':
                ingredient = ''

            elif (content != ',' and x <= 1) and (content != '(' and content != ')'):
                ingredient = ingredient+content

            elif content == ',' and x == 0:

                ingredients.append(ingredient.strip())
                ingredient = ''

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

            elif content == '(' and x >= 1:
                x += 1
            elif content == ')' and x > 1:
                x -= 1

        # Adding the last ingredient if is not in the list
        if ingredient not in ingredients:
            ingredients.append(ingredient.strip())

        # Removing the empty entries
        ingredients = [x for x in ingredients if x]

        # Removing empty lists
        for i, x in enumerate(ingredients):
            if type(x) is list and ('' in x or ' ' in x):
                ingredients.remove(x)

    return ingredients


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


def nutritionalInformation(soup):
    nutritionalInformation = nutritional_information()
    info = soup.find('h5', text='Nährwertangaben')

    if info:
        table_rows = info.find_parent('div').table.find_all('tr')

        for td in enumerate(table_rows):

            if 'Portionsgröße' in td[1].text:
                nutritionalInformation.setServingSize(
                    table_rows[td[0]].td.text.strip().replace('\u200e', ''))

            elif 'Fett' in td[1].text:
                nutritionalInformation.setFats(
                    table_rows[td[0]].td.text.strip().replace('\u200e', ''))

            elif 'Kohlenhydrate' in td[1].text:
                nutritionalInformation.setCarbohydrates(
                    table_rows[td[0]].td.text.strip().replace('\u200e', ''))

            elif 'Eiweiß' in td[1].text:
                nutritionalInformation.setProteins(
                    table_rows[td[0]].td.text.strip().replace('\u200e', ''))

    return nutritionalInformation


def country(soup):
    trans = Translator()

    country = 'None'
    info = soup.find('h5', text='Allgemeine Produktinformationen')

    if info:
        country='None'
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


def price(soup):
    try:
        price = soup.find(
            'span', attrs={'class': 'a-offscreen'}).text.strip()
        if not('€' in price):
                price='None'
    except:
        price = 'None'

    return price


def description(soup):
    try:
        description = soup.find(id='productTitle').get_text().strip()
    except:
        description = 'None'

    return description


def name(soup):

    try:
        name = soup.find(id='productTitle').get_text().strip()
        if ',' in name:
            name = name.split(',')[0]
        if '-' in name:
            name = name.split('-')[0]
        if '–' in name:
            name=name.split('–')[0]
        if '(' in name:
            name=name.split('(')[0]
        if '|' in name:
            name = name.split('|')[0]
        if '-' in name:
            name = name.split('-')[0]

    except:
        name = 'None'

    return name


def get_soup(url):
    
    driver = webdriver.Chrome(
        executable_path='C:\Program Files (x86)\chromedriver.exe')
    driver.get(url)

    source = driver.page_source
    driver.quit()

    soup = BeautifulSoup(source, 'html.parser')

    return soup


def get_ASIN(url):
    asin = url.split('/dp/')[1]
    asin = asin[:10]
    return asin


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

    if foodproduct.getIngredients() == 'None':
        foodproduct.setAllergens(allergies_table(soup))
        if foodproduct.getAllergens()!='None':
            foodproduct.setIngredients(foodproduct.getAllergens())
    else:
        foodproduct.setAllergens(allergens(soup, foodproduct.getIngredients()))
        for a in foodproduct.getAllergens():
            if not(foodproduct.findIngredient(a)):
                foodproduct.addAllergenToIngredients(a)

    return foodproduct
