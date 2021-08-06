from start_browser import driver
from parsers.confidential import CactiLoginData
from parsers.locators import CactiLocators
import re
import time

def get_to_the_switches_page(browser):
    login = browser.find_element(*CactiLocators.LOGIN)
    login.send_keys(CactiLoginData.cacti_login)

    passwd = browser.find_element(*CactiLocators.PASSWD)
    passwd.send_keys(CactiLoginData.cacti_passwd)

    enter_button = browser.find_element(*CactiLocators.ENTER_BUTTON)
    enter_button.click()

    graphs_button = browser.find_element(*CactiLocators.GRAPHS_BUTTON)
    graphs_button.click()
    time.sleep(1)
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
        cacti_browser = driver(CactiLoginData.cacti_url)

        get_to_the_switches_page(cacti_browser)

        switches = cacti_browser.find_elements(*CactiLocators.SWITCH_NAME_AND_IP)
        switch_ip_name_dict = {}
        for switch in switches:
            switch = switch.text
            if 'Host' in switch:
                switch_ip = re.findall(r'\d+\.\d+\.\d+\.\d+', switch)
                switch_name = switch[6:(switch.index(switch_ip[0]) - 2)]
                switch_ip_name_dict[switch_name] = switch_ip[0]
    finally:
        cacti_browser.quit()
    return switch_ip_name_dict





