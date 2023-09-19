from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from io import BytesIO
import pytesseract
import cv2
import numpy as np
import pandas as pd
import time
import os
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

class TenderScraper:
    def __init__(self, driver_path):
        self.driver_path = driver_path


    def setup(self):
        os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        self.driver = webdriver.Chrome(self.driver_path)

    def extract_captcha_text(self):
        element = self.driver.find_element_by_id('captchaImage')
        location = element.location
        size = element.size
        screenshot = self.driver.get_screenshot_as_png()
        image = Image.open(BytesIO(screenshot))
        left = location['x'] + 150
        top = location['y'] + 80
        right = location['x'] + size['width'] + 200
        bottom = location['y'] + size['height'] + 100
        cropped_image = image.crop((left, top, right, bottom))
        cropped_np_image = np.array(cropped_image)

        gray_image = cv2.cvtColor(cropped_np_image, cv2.COLOR_RGB2GRAY)
        _, threshold_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        kernel = np.ones((3, 3), np.uint8)
        cleaned_image = cv2.morphologyEx(threshold_image, cv2.MORPH_OPEN, kernel)
        extracted_text = pytesseract.image_to_string(cleaned_image)
        return extracted_text

    def scrape(self):
        # Create an empty DataFrame to store the scraped data
        columns = ["S.No", "e-publish Date", "Bid Submission Closing Date", "Tender Opening Date", "Title and Ref.No./Tender ID", "Organisation Chain", "Reference Link"]
        data_frame = pd.DataFrame(columns=columns)
        self.driver.get("https://etenders.gov.in/eprocure/app")
        tender_class = self.driver.find_element_by_xpath('//*[@id="PageLink_1"]')
        tender_class.click()
        dropdown_element = self.driver.find_element_by_id("FormOfContractName")
        dropdown = Select(dropdown_element)
        for desired_index in range(1, len(dropdown.options)):
            self.driver.get("https://etenders.gov.in/eprocure/app")
            # Loop through dropdown options
            tender_class = self.driver.find_element_by_xpath('//*[@id="PageLink_1"]')
            tender_class.click()
            dropdown_element = self.driver.find_element_by_id("FormOfContractName")
            dropdown = Select(dropdown_element)
            dropdown.select_by_index(desired_index)
            time.sleep(2)
            #call extracted captcha text function
            extracted_text = self.extract_captcha_text()
            #input the extracted captcha text
            captcha_input = self.driver.find_element_by_id("captchaText")
            captcha_input.send_keys(extracted_text)

            while True:
                try:
                    # Locate the tbody element containing the data
                    tbody = self.driver.find_element_by_xpath('//*[@id="table"]/tbody')
                    rows = tbody.find_elements_by_tag_name("tr")
                    
                    for row in rows[1:]:  # Start from the second row to skip the header
                        row_data = row.find_elements_by_tag_name("td")
                        if len(row_data) == len(columns) - 1:  # Adjusted length due to the new column
                            row_values = [element.text for element in row_data]

                            # Find the reference link element and extract its href attribute
                            reference_link_element = row.find_element_by_tag_name("a")
                            reference_link = reference_link_element.get_attribute("href")

                            row_values.append(reference_link)  # Append the reference link

                            data_frame = data_frame.append(dict(zip(columns, row_values)), ignore_index=True)

                    # Click the "Next" button
                    next_button = self.driver.find_element_by_xpath('//*[@id="linkFwd"]')
                    next_button.click()
                    
                    # Wait for the next page to load (adjust timeout as needed)
                    WebDriverWait(self.driver, 10).until(
                        EC.staleness_of(tbody)
                    )

                except Exception as e:
                    # If the "Next" button is unresponsive or there are no more pages, exit the loop
                    try:
                        error_element = self.driver.find_element_by_xpath('//*[@id="content"]/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr/td/table/tbody/tr[6]/td/table/tbody/tr/td/span/b')
                        if error_element.text == "Invalid Captcha! Please Enter Correct Captcha." :

                            extracted_text = self.extract_captcha_text()
                                                    
                            captcha_input = self.driver.find_element_by_id("captchaText")
                            captcha_input.send_keys(extracted_text)
                            
                            while True:
                                try:
                                    # Locate the tbody element containing the data
                                    tbody = self.driver.find_element_by_xpath('//*[@id="table"]/tbody')
                                    rows = tbody.find_elements_by_tag_name("tr")
                                    
                                    for row in rows[1:]:  # Start from the second row to skip the header
                                        row_data = row.find_elements_by_tag_name("td")
                                        if len(row_data) == len(columns) - 1:  # Adjusted length due to the new column
                                            row_values = [element.text for element in row_data]

                                            # Find the reference link element and extract its href attribute
                                            reference_link_element = row.find_element_by_tag_name("a")
                                            reference_link = reference_link_element.get_attribute("href")

                                            row_values.append(reference_link)  # Append the reference link

                                            data_frame = data_frame.append(dict(zip(columns, row_values)), ignore_index=True)

                                    # Click the "Next" button
                                    next_button = self.driver.find_element_by_xpath('//*[@id="linkFwd"]')
                                    next_button.click()
                                    
                                    # Wait for the next page to load (adjust timeout as needed)
                                    WebDriverWait(self.driver, 10).until(
                                        EC.staleness_of(tbody)
                                    )
                                except:
                                    print("no table")
                                    break

                    except:
                        print("no table")
                        break

        data_frame[['Title', 'reference_number', 'tender_id']] = data_frame['Title and Ref.No./Tender ID'].str.extract(r'\[(.*?)\]\s*\[(.*?)\]\s*\[(.*?)\]')
        data_frame.drop(columns=["S.No",'Title'], inplace=True)
        data_frame.drop_duplicates()
        columns = data_frame.columns.tolist()
        reordered_columns = columns[-2:] + columns[:-2]
        data_frame = data_frame[reordered_columns]
        data_frame.to_csv("final.csv",index = False)

    def run(self):
        self.setup()
        self.scrape()
        self.driver.quit()

if __name__ == "__main__":
    driver_path = r'C:\Users\sagar\Downloads\chromedriver-win32\chromedriver.exe'


    scraper = TenderScraper(driver_path)
    scraper.run()
