import csv

from dotenv import dotenv_values
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import re

WEBSITE = "nutritionvalue"
SOURCES = ['https://www.nutritionvalue.org/foods_by_Vitamin+A%2C+RAE_content.html',
           'https://www.nutritionvalue.org/foods_by_Protein_content.html',
           'https://www.nutritionvalue.org/foods_by_Proline_content.html']

# setup
driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))
data = {}

# iterate through sources
for source in SOURCES:
    driver.get(source)
    main_window = driver.current_window_handle

    # no cookie handling needed
    # get products
    products = driver.find_elements(By.CSS_SELECTOR, "table.results tr td.left a")
    for product in products:
        print(product.text)
    while products:
        product = products.pop()
        name = product.text
        # prevent from overwriting data
        if data.get(name):
            continue
        link = product.get_attribute('href')
        # open link in new tab
        driver.switch_to.new_window()
        driver.get(link)
        # get nutrition data
        nutrition_data = driver.find_elements(By.CSS_SELECTOR, "table#nutrition-label tbody tr td table tbody tr td")
        text = "".join([data.text for data in nutrition_data])
        # match nutrition details
        m = re.match(r"^.+Total Fat (\d+\.?\d?).+Total Carbohydrate (\d+\.?\d?).+Protein (\d+\.?\d?).+$", text)
        # add to dict
        data[name] = {'name': name,
                      'protein': m.group(3),
                      'carbohydrates': m.group(2),
                      'fat': m.group(1)}
        driver.close()
        driver.switch_to.window(main_window)

driver.close()

with open(f'products_{WEBSITE}.csv', 'w', newline='') as csv_file:
    field_names = ['name', 'protein', 'carbohydrates', 'fat']
    writer = csv.DictWriter(csv_file, fieldnames=field_names)
    writer.writeheader()
    for entry in data:
        writer.writerow(data[entry])
