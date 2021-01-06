from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os, time
import pandas as pd

def openDriver(url):
    chromeOptions = webdriver.ChromeOptions()
    #chromeOptions.add_argument("--headless")
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chromeOptions)
    driver.set_window_position(0, 0)
    driver.set_window_size(1200, 700)

    driver.get(url)

    return driver

def scrapeInitial(driver):
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'sp_message_iframe_238176')))
    driver.switch_to.frame('sp_message_iframe_238176')

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div[3]/button')))
    privacyButton = driver.find_element_by_xpath('/html/body/div/div[3]/button')
    privacyButton.click()

    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'fixed-value')))

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    result = [[[] for _ in range(9)] for _ in range(9)]

    for rowCounter, row in enumerate(soup.find('div', class_='sodokoGrid').children):
        try:
            for columnCounter, column in enumerate(row.find_all('div')):
                try:
                    result[rowCounter][columnCounter] = int(column.get_text())
                except ValueError:
                    result[rowCounter][columnCounter] = 0
        except AttributeError:
            pass

    return result

def main():
    url = 'https://sudoku.zeit.de'
    driver = openDriver(url)
    result = scrapeInitial(driver)
    for row in result:
        print(row)
    driver.close()

if __name__ == '__main__':
    main()