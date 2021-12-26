from bs4 import BeautifulSoup
from rdflib.plugin import get
import requests
import re
from googletrans import Translator

from FoodProduct import foodProduct
from FoodProduct import nutritional_information


def get_allergies_table(soup):
    
    allergen = ['None']

    info = soup.find("th", text=" Allergie-Informationen ")
    if info:
        allergen = list()
        content = info.find_parent('tr').select("td")[0].text
        if ":" in content:
            allergen = [x.strip() for x in content.split(":")[1].split(",")]
        else:
            allergen = [x.strip() for x in content.split(",")]

    return allergen


def get_allergens(soup, foodIngredients):
    allergen = list()

    for index, ingredient in enumerate(foodIngredients):

        if ingredient.ingredient[:4].isupper() and not(any(char.isnumeric() for char in ingredient.ingredient[:4])):
            allergen.append(ingredient.ingredient)

        if ingredient.subingredient:
            for sub in ingredient.subingredient:
                if sub[:4].isupper() and not (any(char.isnumeric() for char in sub[:4])):
                    allergen.append(sub)

    if allergen == list():
        table = get_allergies_table(soup)

        for i in foodIngredients:
            for a in table:
                if a in i.ingredient:
                    allergen.append(i.ingredient)
                if i.subingredient:
                    for sub in i.subingredient:
                        if a in sub:
                            allergen.append(sub)

    if allergen == list():
        allergen = ['None']

    return allergen



def get_ingredients(soup):
    # Extract ingredients Bestandteile

    ingredients = 'None'
    ingredient = ''

    info = soup.find("h4", text="Bestandteile")
    if info:
        ingredients = list()
        subingredients = list()
        x = 0

        info = info.find_parent('div')
        contents = info.select("p")[0].select("p")[0].text
        contents = contents[:contents.find('Kann')]

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
        if 'mit ' in contents:
            contents = contents.replace('mit', '')
        if 'aus ' in contents:
            contents = contents.replace('aus ', '')
        if 'enthält ' in contents:
            contents = contents.replace('enthält ', '')
        if 'und ' in contents:
            contents = contents.replace('und', ',')
        if 'mindestens ' in contents:
            contents = contents.replace('mindestens', '')

        # Removing the percentages
        contents = re.sub(
            r'(\d\d,\d\d %|\d\d,\d %|\d,\d\d %|\d,\d %|\d %|\d\d %|\d\d\d %|\d\d,\d\d%|\d\d,\d%|\d,\d\d%|\d,\d%|\d%|\d\d%|\d\d\d%)', '', contents)

        contents = re.sub(r'[(][)]', '', contents)

        # Extracting the ingredients by each character
        for index, content in enumerate(contents):

            if content in '*':
                continue

            if content == ':':
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

        ingredients.append(ingredient.strip())

   
    # removing the empty entries
    ingredients = [x for x in ingredients if x]

    # removing empty lists
    for i, x in enumerate(ingredients):
        if type(x) is list and ('' in x or ' ' in x):
            ingredients.remove(x)

    return ingredients


def get_amazon_category(soup):
    category = 'None'
    info = soup.find('div', attrs={'id': 'showing-breadcrumbs_div'})

    if info:
        list = info.find('ul', attrs={
                         'class': 'a-unordered-list a-horizontal a-size-small'}).find_all('li')

        for x in enumerate(list):

            if 'Lebensmittel & Getränke' in x[1].text:
                # list[i]='Lebensmittel & Getränke', list[i+1]= '>' list[i+2]='Süßigkeiten & Knabbereien'
                category = list[x[0]+2].text.strip()
                break
    return category


def get_nutritional_information(soup):
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


def get_country(soup):
    trans=Translator()

    country = 'None'
    info = soup.find('h5', text='Allgemeine Produktinformationen')

    if info:
        table_rows = info.find_parent('div').table.find_all('tr')

        for td in enumerate(table_rows):
            if 'Ursprungsland' in td[1].text or 'Herkunftsland' in td[1].text:
                country = table_rows[td[0]].td.text
                country = country.replace('\u200e', '').strip()
                break
        
        if country!='None':
          country=trans.translate(country, dest='de').text

        if country=='Vereinigte Staaten':
            country='USA'
        if country=='Vereinigte Königreich' or country=='Vereinigtes Königreich':
            country='UK'

    return country


def get_brand(soup):
    brand = 'None'
    info = soup.find('h5', text='Allgemeine Produktinformationen')

    if info:
        table_rows = info.find_parent('div').table.find_all('tr')

        for td in enumerate(table_rows):
            if 'Marke' in td[1].text:
                brand = table_rows[td[0]].td.text
                brand = brand.replace('\u200e', '').strip()
    return brand


def get_price(soup):
    try:
        price = soup.find(
            'span', attrs={'class': 'a-offscreen'}).text.strip()
    except:
        price = 'None'

    return price


def get_description(soup):

    try:
        description = soup.find(id='productTitle').get_text().strip()
    except:
        description = 'None'

    return description


def get_name(soup):

    try:
        name = soup.find(id='productTitle').get_text().strip()
        if ',' in name:
            name = name.split(',')[0]
        elif '-' in name:
            name = name.split('-')[0]
        elif '|' in name:
            name = name.split('|')[0]
    except:
        name = 'None'

    return name


def get_soup(url):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    }
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    return soup


def get_ASIN(url):
    asin = url.split('/dp/')[1].split('/')[0]
    return asin


def get_product(url):

    foodproduct = foodProduct()

    foodproduct.setUrl(url)
    foodproduct.setAsin(get_ASIN(foodproduct.url))

    soup = get_soup(foodproduct.url)

    foodproduct.setName(get_name(soup))
    foodproduct.setDecription(get_description(soup))
    foodproduct.setPrice(get_price(soup))
    foodproduct.setBrand(get_brand(soup))
    foodproduct.setCountry(get_country(soup))
    foodproduct.set_nutritional_information(get_nutritional_information(soup))
    foodproduct.setCategory(get_amazon_category(soup))
    foodproduct.addIngredient(get_ingredients(soup))
    foodproduct.addAllergen(get_allergens(soup, foodproduct.ingredients))

    return foodproduct

