from start_browser import driver
from parsers.confidential import CactiLoginData
from parsers.locators import CactiLocators
import json
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


def main(switch_ip_addr=None, port='0'):
    try:
        cacti_browser = driver(CactiLoginData.cacti_url)
        get_to_the_switches_page(cacti_browser)

        switches = cacti_browser.find_elements(*CactiLocators.SWITCH_NAME_AND_IP)

        switch_ip_name_dict = {}
        for switch in switches:
            switch_text = switch.text

            if 'Host' in switch_text:
                if switch_ip_addr == None:
                    switch_ip = re.findall(r'\d+\.\d+\.\d+\.\d+', switch_text)
                    switch_name = switch_text[6:(switch_text.index(switch_ip[0]) - 2)]
                    switch_ip_name_dict[switch_name] = switch_ip[0]

                else:
                    switch_ip = re.findall(switch_ip_addr, switch_text)

                    if switch_ip:
                        switch.click()
                        image_objects = cacti_browser.find_element(*CactiLocators.CLIENT_IMAGE)
                        image = image_objects.find_elements_by_tag_name('img')

                        if int(port) < 10:
                            client_port = f'Port 0{port}'
                        else:
                            client_port = f'Port {port}'

                        client_image_url = False
                        uplink_image_url = False
                        counter = 0
                        while not (client_image_url and uplink_image_url):

                            alt_image = image[counter].get_attribute('alt')
                            if client_port in alt_image:
                                client_image_url = image[counter].get_attribute('src')
                            elif 'Uplink' in alt_image:
                                uplink_image_url = image[counter].get_attribute('src')
                            counter += 1

                        return client_image_url, uplink_image_url
    finally:
        cacti_browser.quit()
    return switch_ip_name_dict


def update_clients_cacti_image_db():
    try:
        cacti_browser = driver(CactiLoginData.cacti_url)
        get_to_the_switches_page(cacti_browser)

        switches = cacti_browser.find_elements(*CactiLocators.SWITCH_NAME_AND_IP)
        switch_ip_port_url_dict = {}
        for switch in switches:
            switch_text = switch.text
            switch_ip = re.findall(r'\d+\.\d+\.\d+\.\d+', switch_text)[0]

            switch.click()

            image_objects = cacti_browser.find_element(*CactiLocators.CLIENT_IMAGE)
            image = image_objects.find_elements_by_tag_name('img')
            port_url_dict = {}

            for object in image:
                alt_image = object.get_attribute('alt')
                port = re.findall('Port \d\d', alt_image)

                if port:
                    client_image_url = object.get_attribute('src')
                    port_url_dict[port[0]] = client_image_url

            switch_ip_port_url_dict[switch_ip] = port_url_dict

        with open('search_engine/cacti_urls.json', 'w') as cacti_urls:
            json.dump(switch_ip_port_url_dict, cacti_urls, indent=2, sort_keys=True, ensure_ascii=False)

    finally:
        cacti_browser.quit()


start = time.time()
update_clients_cacti_image_db()
end = time.time() - start
print(end)


