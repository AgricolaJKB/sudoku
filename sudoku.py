from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import os, time

def openDriver(url):
    chromeOptions = Options()
    chromeOptions.add_experimental_option("detach", True)
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chromeOptions)
    driver.set_window_position(0, 0)
    driver.set_window_size(1300, 800)

    driver.get(url)

    return driver

def waitAndClick(driver, xpath):
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    element = driver.find_element_by_xpath(xpath)
    element.click()

def scrapeInitial(driver, email, password):
    # Datenschutzerklärung zustimmen
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'sp_message_iframe_238176')))
    driver.switch_to.frame('sp_message_iframe_238176')
    waitAndClick(driver, '/html/body/div/div[3]/button')

    # Höllisch-Schwierigkeitsstufe auswählen
    waitAndClick(driver, '//*[@id="content"]/app-nav-bar/div/div[2]/div/div[2]/div/div[5]/button')

    # Einloggen
    waitAndClick(driver, '//*[@id="content"]/app-paywall-layer/div/div/div/div/div/div[3]/a')
    driver.find_element_by_id('login_email').send_keys(email)
    driver.find_element_by_id('login_pass').send_keys(password)
    waitAndClick(driver, '//*[@id="login"]/div[4]/input')
    
    # Spiel starten
    waitAndClick(driver, '//*[@id="content"]/div[2]/app-game-grid/div/button')

    # Startkonstellation scrapen
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'fixed-value')))

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    result = [[0 for _ in range(9)] for _ in range(9)]

    for rowCounter, row in enumerate(soup.find('div', class_='sodokoGrid').children):
        try:
            for columnCounter, column in enumerate(row.find_all('div')):
                try:
                    result[rowCounter][columnCounter] = int(column.get_text())
                except ValueError:
                    pass
        except AttributeError:
            pass

    return result, soup

def insertResult(driver, result, soup):
    for rowCounter, row in enumerate(result):
        for columnCounter, column in enumerate(row):
            try:
                element = driver.find_element_by_id(f'{rowCounter}{columnCounter}')
                element.click()
                element.send_keys(str(column))
            except NoSuchElementException:
                pass

def main():
    url = 'https://sudoku.zeit.de'
    with open('private/email.txt') as file:
        email = file.read()
    with open('private/password.txt') as file:
        password = file.read()

    driver = openDriver(url)
    startingGrid, soup = scrapeInitial(driver, email, password)

    print(startingGrid)
    # Hier fehlt dein Algorithmus. startingGrid enthält die Startaufstellung (als Liste von Listen), das Ergebnis
    # muss dann in result abgespeichert werden.
    #
    # Format für In- und Output:
    # [[0, 0, 0, 0, 5, 4, 0, 0, 8]
    # [0, 6, 0, 0, 0, 0, 0, 1, 7]
    # [0, 0, 0, 9, 0, 0, 0, 0, 0]
    # [6, 0, 5, 0, 0, 7, 0, 0, 0]
    # [0, 0, 0, 0, 0, 0, 1, 0, 0]
    # [0, 0, 0, 0, 9, 0, 0, 7, 3]
    # [4, 0, 0, 0, 0, 9, 0, 0, 0]
    # [0, 8, 0, 3, 0, 0, 0, 2, 0]
    # [7, 1, 0, 0, 8, 0, 0, 3, 5]]



    insertResult(driver, startingGrid, soup)

if __name__ == '__main__':
    main()