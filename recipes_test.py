import csv

from selenium import webdriver
from selenium.webdriver.common.by import By
import re

DRIVER = "/home/wiktor/web/geckodriver/geckodriver"
sos = 'https://www.allrecipes.com/gallery/salad-meals/?slide=0a5f9312-8e0a-4f35-8565-4533bbe47df5#0a5f9312-8e0a-4f35-8565-4533bbe47df5'

driver = webdriver.Firefox(executable_path=DRIVER)

driver.get(sos)
nutrition = driver.find_element(By.CSS_SELECTOR, "div.recipeNutritionSectionBlock div.section-body")
