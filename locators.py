from selenium.webdriver.common.by import By

class NetstoreLocators():
    LOGIN = (By.CSS_SELECTOR, 'body > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > form:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(2) > input:nth-child(1)')
    PASSWD = (By.CSS_SELECTOR, 'body > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > form:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(2) > input:nth-child(1)')
    ENTER_BUTTON = (By.CSS_SELECTOR, '.button')
    GET_ALL_CLIENTS_PAGE = (By.CSS_SELECTOR, 'body > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(2) > a:nth-child(1)')
    GET_ALL_ACTIVE_CLIENTS_LIST = (By.CSS_SELECTOR, '[onmouseout="this.style.backgroundColor=\'white\'"]')
    GET_ALL_TERMINATED_CLIENTS_LIST = (By.CSS_SELECTOR, '[onmouseout="this.style.backgroundColor=\'#16A9A0\'"]')
    GET_INFO_ABOUT_THE_CLIENT = (By.XPATH, '/html/body/table/tbody/tr[2]/td[1]/table/tbody/tr[3]/td/a')
