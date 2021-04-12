from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json
from time import *
from pandas import *
global data
global report_data
data={}
report_data={"Test Case":[],
             "Result":[],
             "Error":[]

}

def load_datafile():
    global data
    with open('configuration_selectors.json') as f:
        data = json.load(f)

    setup_chrome_binary()


def setup_chrome_binary():
    options=webdriver.ChromeOptions()
    options.binary_location=data['chrome_binary_path']
    options.add_argument('--start-maximized')
    options.add_argument('--disable-gpu')
    desired_capabilites=DesiredCapabilities.CHROME.copy()
    driver=webdriver.Chrome(executable_path=data['chrome_driver_path'],chrome_options=options,desired_capabilities=desired_capabilites)
    driver.get(data['site_url'])
    sleep(10)
    test_case_search_bar(driver)
    sleep(2)
    test_case_creative_count(driver)
    test_case_random_brand_link(driver)
    test_case_share_brand_ad(driver)

def report_data_fn(test_case_name,result,error):
    global report_data
    report_data['Test Case'].append(test_case_name)
    report_data['Result'].append(result)
    report_data['Error'].append(error)

    report_df=DataFrame(report_data)
    print (report_df)
    report_df.to_excel(data['excel_report_path'],index=False)
    report_df.to_html(data['html_report_path'],index=False)


def search_bar_operation(driver,main_element,brand):
    try:
        search_bar_main_element = driver.find_element_by_class_name(main_element)
        search_bar_row_element = search_bar_main_element.find_elements_by_class_name(data['search_bar_row_element'])

        for elem in search_bar_row_element:
            if str(brand).lower() == str(elem.find_element_by_tag_name('span').text).strip().lower():
                elem.find_element_by_tag_name('span').click()
                sleep(10)
                driver.save_screenshot(str(data['screenshot_dir']) + "search_bar_result_page"+str(brand)+".png")
                break
        return "Success","None"
    except Exception as e:
        return "Failed",e

def test_case_search_bar(driver):
    try:
        wait = WebDriverWait(driver, 30)
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, data['search_bar'])))
        search_bar_element=driver.find_element_by_css_selector(data['search_bar'])
        driver.execute_script("arguments[0].scrollIntoView();", search_bar_element)
        sleep(1)
        search_bar_element.click()
        search_bar_element.send_keys(data['search_word'][0])
        sleep(5)
        driver.save_screenshot(str(data['screenshot_dir'])+"search_bar.png")
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, data['search_bar_main_element'])))
        status,error=search_bar_operation(driver, data['search_bar_main_element'],data['search_word'][0])
        if status=="Success":

            report_data_fn('Test Case- Search Bar', 'Successful', "None")
            driver.save_screenshot(str(data['screenshot_dir']) + "search_bar_success.png")
            return ""
        else:
            report_data_fn('Test Case- Search Bar', 'Failed', error)
            driver.save_screenshot(str(data['screenshot_dir']) + "search_bar_failed.png")
            return ""

    except Exception as e:
        print (e)
        report_data_fn('Test Case- Search Bar', "Failed", str(e))
        driver.save_screenshot(str(data['screenshot_dir']) + "search_bar_eror.png")

def get_creative_count(driver):
    global data
    print(data['creative_count'])
    try:
        creative_header_count=driver.find_element_by_css_selector(data['creative_count'])
        print(creative_header_count.text)
        creative_header_count=str(creative_header_count.text).split(' ')
        creative_header_count=creative_header_count[0]
        return creative_header_count,"Success"
    except Exception as e:
        print (e)
        return e,"Failed"

def count_creative_ads(driver):
    global data
    try:
        creative_container=driver.find_element_by_class_name(data['creative_container'])
        individual_creative=creative_container.find_elements_by_class_name(data['individual_creative'])
        print(len(individual_creative))
        return (len(individual_creative)),"Success"
    except Exception as e:
        print(e)
        return e,"Failed"

def elem_exists(driver,selector,counter):

    try:
        load_more=driver.find_element_by_css_selector(selector)
        load_more.click()
        sleep(7)
        driver.save_screenshot(str(data['screenshot_dir']) + "search_bar_result_page_load_more_"+str(counter)+".png")
        return True
    except Exception as e:
        return False
def test_case_creative_count(driver):
    global data
    wait = WebDriverWait(driver, 30)
    for brand in data['search_word']:
        print(brand)
        try:
            driver.execute_script("window.scroll(0, 0);")
            driver.refresh()
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, data['search_bar_search_result_page'])))
            search_bar=driver.find_element_by_class_name(data['search_bar_search_result_page'])
            ActionChains(driver).move_to_element(search_bar).click(search_bar).perform()
            search_bar.send_keys(brand)
            driver.save_screenshot(str(data['screenshot_dir']) + "search_bar_result_page_"+str(brand)+".png")
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, data['search_bar_result_result_page'])))
            status,error=search_bar_operation(driver, data['search_bar_result_result_page'],brand)
            if status=="Success":
                pass
            else:
                report_data_fn('Test Case- Creative Count for ' + str(brand), "Failed", error)
                return ""
        except Exception as e:
            report_data_fn('Test Case- Creative Count for '+str(brand), "Failed", e)
            return ""
        count_creative_header,msg=get_creative_count(driver)
        flag=True
        counter=0
        while flag:

            flag=elem_exists(driver, data['load_more'],counter)
            counter=counter+1
        if msg=="Failed":
            print("in If")
            report_data_fn('Test Case- Creative Count for '+str(brand), "Failed", count_creative_header)
            pass
        else:
            print("in else")
            count_creative_page,status=count_creative_ads(driver)
            if status=="Failed":
                report_data_fn('Test Case- Creative Count for '+str(brand), "Failed", str(count_creative_page))
                pass
            else:
                if int(count_creative_header)==int(count_creative_page):
                    print("Success")
                    report_data_fn('Test Case- Creative Count for '+str(brand), "Successul", "None")
                else:
                    report_data_fn('Test Case- Creative Count for '+str(brand), "Failed", "Creative Count not Matched")


def test_case_random_brand_link(driver):
    wait = WebDriverWait(driver, 30)
    try :
        counter=0
        driver.execute_script("window.scroll(0, 0);")
        driver.refresh()
        brand_list = []
        while counter<5:
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, data['random_brand'])))
            random_brand=driver.find_element_by_class_name(data['random_brand'])
            random_brand.click()
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, data['brand_header'])))
            driver.save_screenshot(str(data['screenshot_dir']) + "random_brand_"+str(counter)+".png")
            brand_header=driver.find_elements_by_css_selector(data['brand_header'])[0]
            brand_list.append(brand_header.text)
            counter+=1
        print (brand_list)
        if (len(set(brand_list)) == len(brand_list)):
            report_data_fn('Test Case- Randdom Brand Check', "Successful", "None")
        else:
            report_data_fn('Test Case- Randdom Brand Check', "Failed", "Random Brand Link not Opening Random Links")
    except Exception as e:
        report_data_fn('Test Case- Randdom Brand Check', "Failed", e)

def test_case_share_brand_ad(driver):
    brand=data['search_word'][0]
    wait = WebDriverWait(driver, 30)
    try:
        driver.refresh()
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, data['search_bar_search_result_page'])))
        search_bar = driver.find_element_by_class_name(data['search_bar_search_result_page'])
        ActionChains(driver).move_to_element(search_bar).click(search_bar).perform()
        search_bar.send_keys(brand)
        driver.save_screenshot(str(data['screenshot_dir']) + "testcase_ad_share_" + str(brand) + ".png")
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, data['search_bar_result_result_page'])))
        status, error = search_bar_operation(driver, data['search_bar_result_result_page'], brand)
        if status=="Success":
            pass
        else:
            report_data_fn('Test Case- Share Brand Ad', "Failed", error)
            return ""
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, data['creative_container'])))
        creative_container=driver.find_element_by_class_name(data['creative_container'])
        individual_creative=creative_container.find_elements_by_class_name(data['individual_creative'])[0]
        ActionChains(driver).move_to_element(individual_creative).perform()
        sleep(2)
        driver.save_screenshot(str(data['screenshot_dir']) + "testcase_ad_share_hover" + str(brand) + ".png")
        driver.find_element_by_link_text('Share').click()
        sleep(3)
        driver.save_screenshot(str(data['screenshot_dir']) + "testcase_ad_share_click" + str(brand) + ".png")
        driver.find_element_by_css_selector(data['close_share_window']).click()
        sleep(2)
        report_data_fn('Test Case- Share Brand Ad', "Successfull", "None")
    except Exception as e:
        report_data_fn('Test Case- Share Brand Ad', "Failed", e)
        pass


load_datafile()
print(report_data)
