# Selenium to opne the website, locate the (form fields, and extract the required information)

import json
from selenium import webdriver                                              # webdriver module is used to interact with web browsers(like clicking button, filling forms,navigating through pages)
from selenium.webdriver.chrome.service import Service as ChromeService      # Selenium uses  service to start the driver, communicate with it, and manage it during life cycle
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By                                 # Here By is a locator strategy that helps in finding elements on webpage(e.g By.TAG_NAME)
from webdriver_manager.chrome import ChromeDriverManager                    # Webdriver_manager for automatically install the necessary driver
from webdriver_manager.firefox import GeckoDriverManager                    # //
from webdriver_manager.microsoft import EdgeChromiumDriverManager           # //

def get_driver(browser='chrome'):
    """
    Function to get the appropriate WebDriver based on the browser type.
    Supports Chrome, Firefox, and Edge.
    """
    if browser.lower() == 'chrome':
        service = ChromeService(ChromeDriverManager().install())
        return webdriver.Chrome(service=service)
    elif browser.lower() == 'firefox':
        service = FirefoxService(GeckoDriverManager().install())
        return webdriver.Firefox(service=service)
    elif browser.lower() == 'edge':
        service = EdgeService(EdgeChromiumDriverManager().install())
        return webdriver.Edge(service=service)
    else:
        raise ValueError("Unsupported browser! Choose between 'chrome', 'firefox', or 'edge'.")

def extract_forms_selenium(url, browser='chrome'):
    # Initialize WebDriver for the specified browser
    driver = get_driver(browser)
    
    # Open the given URL
    driver.get(url)
    Forms_found = []
    # Locate all forms
    forms = driver.find_elements(By.TAG_NAME, 'form')
    
    for form_idx, form in enumerate(forms, 1):                              # It extracts forms one by one and also write its index no 
        
        form_info={
        'action' : form.get_attribute('action'),
        'method' : form.get_attribute('method'),
        'input' : [],
        'textarea': []
        }
        
        # Extract input fields (text, password, hidden, etc.)
        input_fields = form.find_elements(By.TAG_NAME, 'input')
        for idx, input_field in enumerate(input_fields, 1):
            input={
            'name':input_field.get_attribute('name'),
            'type': input_field.get_attribute('type'),
            'placeholder': input_field.get_attribute('placeholder'),
            'value': input_field.get_attribute('value'),
            'required': input_field.get_attribute('required')
            }
            form_info['input'].append(input)
        # Extract textarea fields
        
        textareas = form.find_elements(By.TAG_NAME, 'textarea')
        for textarea in textareas:
            textarea={
            "name": textarea.get_attribute('name'),
            "placeholder": textarea.get_attribute('placeholder'),
            "value": textarea.text,
            "required": textarea.get_attribute('required')
            }
            form_info["textarea"].append(textarea)
        data = form_info
        data = json.dumps(data,indent=4)
        
        Forms_found.append(data)
    driver.quit()
    return Forms_found

"""
        # Extract select dropdown fields
        select_fields = form.find_elements(By.TAG_NAME, 'select')
        for idx, select in enumerate(select_fields, 1):
            options = select.find_elements(By.TAG_NAME, 'option')
            print(f"Select #{idx}: Name: {select.get_attribute('name')}")
            for option in options:
                print(f"Option Value: {option.get_attribute('value')}, Option Text: {option.text}")
            print(f"Is Required: {select.get_attribute('required')}")
            print("-" * 40)
        
        # Extract checkboxes and radio buttons
        checkbox_radio_fields = form.find_elements(By.XPATH, "//input[@type='checkbox' or @type='radio']")
        for idx, field in enumerate(checkbox_radio_fields, 1):
            print(f"Checkbox/Radio #{idx}:")
            print(f"Name: {field.get_attribute('name')}")
            print(f"Type: {field.get_attribute('type')}")
            print(f"Checked: {field.get_attribute('checked')}")
            print(f"Value: {field.get_attribute('value')}")
            print("-" * 40)
"""