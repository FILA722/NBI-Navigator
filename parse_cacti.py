import time

from start_browser import driver
from confidential import CactiLoginData
from locators import CactiLocators

def get_to_the_switches_page(browser):
    login = browser.find_element(*CactiLocators.LOGIN)
    login.send_keys(CactiLoginData.cacti_login)

    passwd = browser.find_element(*CactiLocators.PASSWD)
    passwd.send_keys(CactiLoginData.cacti_passwd)

    enter_button = browser.find_element(*CactiLocators.ENTER_BUTTON)
    enter_button.click()

    graphs_button = browser.find_element(*CactiLocators.GRAPHS_BUTTON)
    graphs_button.click()

    nbi_dropdown_button = browser.find_element(*CactiLocators.NBI_DROPDOWN_BUTTON)
    nbi_dropdown_button.click()

    nbi_dropdown_dsl_concentrators_button = browser.find_element(*CactiLocators.NBI_DROPDOWN_Dsl_concentrators_BUTTON)
    nbi_dropdown_dsl_concentrators_button.click()

    nbi_dropdown_bc_button = browser.find_element(*CactiLocators.NBI_DROPDOWN_BC_BUTTON)
    nbi_dropdown_bc_button.click()

    nbi_dropdown_bg_button = browser.find_element(*CactiLocators.NBI_DROPDOWN_BG_BUTTON)
    nbi_dropdown_bg_button.click()

    nbi_dropdown_routers_button = browser.find_element(*CactiLocators.NBI_DROPDOWN_Routers_BUTTON)
    nbi_dropdown_routers_button.click()

    nbi_dropdown_switch_bc_button = browser.find_element(*CactiLocators.NBI_DROPDOWN_Switch_BC_BUTTON)
    nbi_dropdown_switch_bc_button.click()

    return browser

def main():
    try:
        browser = driver(CactiLoginData.cacti_url)

        get_to_the_switches_page(browser)

        switches = browser.find_elements(*CactiLocators.SWITCH_NAME_AND_IP)
        print(tuple(switch.text for switch in switches))
        print(len(switches))


    finally:
        browser.quit()

main()
