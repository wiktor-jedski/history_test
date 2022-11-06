"""
A script for scraping recipe data from AllRecipes.
As of 2022-11-06, script is not working - AllRecipes changed class names.
"""
import csv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By
import re
from dotenv import dotenv_values

WEBSITE = "allrecipes"

# setup
env_config = dotenv_values(".env")
DRIVER = env_config["DRIVER"]
SOURCES = ["https://www.allrecipes.com/recipes/15334/healthy-recipes/breakfast-and-brunch/",
           "https://www.allrecipes.com/recipes/16376/healthy-recipes/lunches/",
           "https://www.allrecipes.com/recipes/1320/healthy-recipes/main-dishes/",
           "https://www.allrecipes.com/recipes/1321/healthy-recipes/side-dishes/",
           "https://www.allrecipes.com/recipes/1346/healthy-recipes/salads/",
           "https://www.allrecipes.com/recipes/17700/healthy-recipes/soups-and-stews/",
           "https://www.allrecipes.com/recipes/2818/healthy-recipes/super-foods/",
           "https://www.allrecipes.com/recipes/17587/healthy-recipes/clean-eating/",
           "https://www.allrecipes.com/recipes/16704/healthy-recipes/mediterranean-diet/",
           "https://www.allrecipes.com/recipes/22607/healthy-recipes/weight-loss/",
           "https://www.allrecipes.com/recipes/22590/healthy-recipes/whole30/"]

driver = webdriver.Firefox(executable_path=DRIVER)
data = {}

# get data
# iterate through sources
for source in SOURCES:
    driver.get(source)
    main_window = driver.current_window_handle

    # handle cookies popup
    try:
        cookie = driver.find_element(By.ID, "onetrust-reject-all-handler")
    except ElementNotInteractableException:
        pass
    else:
        cookie.click()

    recipes = driver.find_elements(By.CSS_SELECTOR, "a.comp")
    print(recipes)

    for recipe in recipes:
        try:
            new_recipe = recipe.text not in data
        except NoSuchElementException:
            continue
        if new_recipe:
            # switch to new window with recipe data
            name = recipe.text
            link = recipe.get_attribute('href')
            driver.switch_to.new_window('new_recipe')
            driver.get(link)
            # error handling - no nutrition value
            try:
                nutrition = driver.find_element(By.CSS_SELECTOR, "div.recipeNutritionSectionBlock div.section-body")
            except NoSuchElementException:
                continue
            # find nutrition data and match with regular expression to find macros
            m = re.match(r"(\d+)\D+(\d+\.?\d?)\D+(\d+\.?\d?)\D+(\d+\.?\d?)", nutrition.text)  # probably can improve
            data[name] = {'name': name,
                          'calories': m.group(1),
                          'protein': m.group(2),
                          'carbohydrates': m.group(3),
                          'fat': m.group(4),
                          'link': link}
            # go back to get access to links for recipes
            driver.close()
            driver.switch_to.window(main_window)

driver.close()

# write into csv
with open(f'recipes_{WEBSITE}.csv', 'w', newline='') as csv_file:
    field_names = ['name', 'calories', 'protein', 'carbohydrates', 'fat', 'link']
    writer = csv.DictWriter(csv_file, fieldnames=field_names)

    writer.writeheader()
    for entry in data:
        writer.writerow(data[entry])
