"""
A script for scraping product data from Tabele Kalorii.
"""
import csv

from dotenv import dotenv_values
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

WEBSITE = "tabele-kalorii"

# setup
env_config = dotenv_values(".env")
DRIVER = env_config["DRIVER"]
SOURCES = ["https://www.tabele-kalorii.pl/mieso.html"]

driver = webdriver.Firefox(executable_path=DRIVER)
data = {}

# iterate through sources
for source in SOURCES:
    driver.get(source)
    main_window = driver.current_window_handle

    # handle cookies popup for first source
    if source == "https://www.tabele-kalorii.pl/mieso.html":
        driver.implicitly_wait(2)
        driver.switch_to.frame("cmp-iframe")
        driver.find_element(By.CSS_SELECTOR, "button.MuiButton-containedPrimary").click()
        driver.switch_to.window(main_window)

    products = driver.find_elements(By.CSS_SELECTOR, "tr td a")
    while products:
        product = products.pop()
        name = product.text
        link = product.get_attribute('href')
        # open link
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + 't')
        driver.get(link)
        # get table data
        table_data = driver.find_elements(By.CSS_SELECTOR, 'tr.tr-gorna-kreska td')
        fat, carb, protein = "", "", ""
        for i in range(len(table_data)):
            if table_data[i].text == 'Tłuszcz':
                fat = table_data[i+1].text
                fat = fat.replace(",", ".").split(" ")[0]
            elif table_data[i].text == 'Węglowodany':
                carb = table_data[i+1].text
                carb = carb.replace(",", ".").split(" ")[0]
            elif table_data[i].text == 'Białko':
                protein = table_data[i+1].text
                protein = protein.replace(",", ".").split(" ")[0]
        data[name] = {'name': name,
                      'protein': protein,
                      'carbohydrates': carb,
                      'fat': fat}
        # close tab
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + 'w')

driver.close()

with open(f'products_{WEBSITE}.csv', 'w', newline='') as csv_file:
    field_names = ['name', 'protein', 'carbohydrates', 'fat']
    writer = csv.DictWriter(csv_file, fieldnames=field_names)
    writer.writeheader()

    for entry in data:
        writer.writerow(data[entry])
