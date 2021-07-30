from selenium.webdriver.common.by import By

class NetstoreLocators():
    LOGIN = (By.CSS_SELECTOR, 'body > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > form:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(2) > input:nth-child(1)')
    PASSWD = (By.CSS_SELECTOR, 'body > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > form:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(2) > input:nth-child(1)')
    ENTER_BUTTON = (By.CSS_SELECTOR, '.button')
    GET_ALL_CLIENTS_PAGE = (By.CSS_SELECTOR, 'body > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(2) > a:nth-child(1)')
    GET_ALL_ACTIVE_CLIENTS_LIST = (By.CSS_SELECTOR, '[onmouseout="this.style.backgroundColor=\'white\'"]')
    GET_ALL_TERMINATED_CLIENTS_LIST = (By.CSS_SELECTOR, '[onmouseout="this.style.backgroundColor=\'#16A9A0\'"]')
    GET_INFO_ABOUT_THE_CLIENT = (By.XPATH, '/html/body/table/tbody/tr[2]/td[1]/table/tbody/tr[3]/td/a')

class NetstoreClientPageLocators():
    TEL = (By.CSS_SELECTOR, 'body > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(4) > td:nth-child(2) > input:nth-child(1)')
    EMAIL = (By.CSS_SELECTOR, 'body > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(5) > td:nth-child(2) > input:nth-child(1)')
    PHYSICAL_ADDRESS = (By.CSS_SELECTOR, 'body > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(3) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(3) > select:nth-child(1) > option:nth-child(14)')
    PHYSICAL_ADDRESS_NOTES = (By.CSS_SELECTOR, 'body > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(3) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > table:nth-child(1) > tbody:nth-child(2) > tr:nth-child(5) > td:nth-child(2) > textarea:nth-child(1)')
    IS_ACTIVE = (By.CSS_SELECTOR, 'body > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(9) > td:nth-child(2)')
    IS_CONVERTER = (By.CSS_SELECTOR, 'body > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(13) > td:nth-child(2) > input:nth-child(1)')
    SPEED = (By.CSS_SELECTOR, 'body > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(14) > td:nth-child(2) > input:nth-child(1)')
    NOTES = (By.CSS_SELECTOR, 'body > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(10) > td:nth-child(2) > textarea:nth-child(1)')
    IP_ADDRESSES = (By.CSS_SELECTOR, 'body > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(4) > td:nth-child(1) > table:nth-child(1) > tbody:nth-child(2) > tr > td:nth-child(2)')
