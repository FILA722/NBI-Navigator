from start_browser import driver
from parsers.confidential import CactiLoginData
from parsers.locators import CactiLocators
from selenium.common.exceptions import StaleElementReferenceException
from PIL import Image
import json
import re
import time

def get_to_the_switches_page():
    browser = driver(CactiLoginData.cacti_url)

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
        # cacti_browser = driver(CactiLoginData.cacti_url)
        cacti_browser = get_to_the_switches_page()

        switches = cacti_browser.find_elements(*CactiLocators.SWITCH_NAME_AND_IP)

        switch_ip_name_dict = {}
        for switch in switches:
            switch_text = switch.text

            if 'Host' in switch_text:
                switch_ip = re.findall(r'\d+\.\d+\.\d+\.\d+', switch_text)
                switch_name = switch_text[6:(switch_text.index(switch_ip[0]) - 2)]
                switch_ip_name_dict[switch_name] = switch_ip[0]

    finally:
        cacti_browser.quit()
    return switch_ip_name_dict


def update_clients_cacti_image_db(update_times=0):
    if update_times > 3:
        return
    try:
        # cacti_browser = driver(CactiLoginData.cacti_url)
        cacti_browser = get_to_the_switches_page()

        switches = cacti_browser.find_elements(*CactiLocators.SWITCH_NAME_AND_IP)
        switch_ip_port_url_dict = {}
        for switch in switches:
            switch_text = switch.text
            switch_ip = re.findall(r'\d+\.\d+\.\d+\.\d+', switch_text)
            if switch_ip:
                switch_ip = switch_ip[0]
                switch.click()

                image_objects = cacti_browser.find_element(*CactiLocators.CLIENT_IMAGE)
                image = image_objects.find_elements_by_tag_name('img')
                port_url_dict = {}

                for object in image:
                    alt_image = object.get_attribute('alt')

                    if re.findall('[Uu]plink', alt_image):
                        port = ['Port Uplink']
                    else:
                        port = re.findall('Port \d\d', alt_image)

                    if port:
                        client_image_url = object.get_attribute('src')
                        port_url_dict[port[0]] = client_image_url

                switch_ip_port_url_dict[switch_ip] = port_url_dict

        with open('../search_engine/cacti_urls.json', 'w') as cacti_urls:
            json.dump(switch_ip_port_url_dict, cacti_urls, indent=2, sort_keys=True, ensure_ascii=False)

    except StaleElementReferenceException:
        #Происходит из-за регулярной перезагрузки страницы
        cacti_browser.quit()
        update_times += 1
        update_clients_cacti_image_db(update_times)
    finally:
        cacti_browser.quit()


def save_cacti_client_image_to_file(client_ip_address, switch_ip, client_port):
    browser = driver(CactiLoginData.cacti_url)

    login = browser.find_element(*CactiLocators.LOGIN)
    login.send_keys(CactiLoginData.cacti_login)

    passwd = browser.find_element(*CactiLocators.PASSWD)
    passwd.send_keys(CactiLoginData.cacti_passwd)

    enter_button = browser.find_element(*CactiLocators.ENTER_BUTTON)
    enter_button.click()

    with open('search_engine/cacti_urls.json', 'r') as cacti_urls:
        client_image_dict = json.load(cacti_urls)
    client_image_url = client_image_dict[switch_ip][client_port]
    client_image_uplink = client_image_dict[switch_ip]['Port Uplink']

    save_image(browser, client_ip_address, client_image_url, 'client')
    save_image(browser, client_ip_address, client_image_uplink)

    browser.quit()

def save_image(browser, client_ip_address, image_url, object='uplink'):
    browser.get(image_url)

    if object == 'client':
        image_path = f'static/images/{client_ip_address}_image_url.png'
    else:
        image_path = f'static/images/{client_ip_address}_image_uplink.png'

    browser.save_screenshot(image_path)

    im = Image.open(image_path)
    im_crop = im.crop((383, 223, 978, 469))
    im_crop.save(image_path, quality=95)


