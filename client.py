from selenium import webdriver
import pytesseract
import os
from dependencies.cleaning.cleaning import cleaning_data
from dependencies.scraping.scraper import scrape
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


class TenderScraper:
    def __init__(self, driver_path):
        self.driver_path = driver_path

# step - 1 -> setup yhe pytesseract and web driver for scraping and image extracting
    def setup(self):
        os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        self.driver = webdriver.Chrome(self.driver_path)

# step - 2 -> extract the captcha from captcha image and then scrape the text from all the pages
    def scrape_captcha_page(self):
        data_drame = scrape(self)
        return data_drame

# step - 3 -> clean the extracted dataframe
    def clean(self, data_drame):
        clean_data = cleaning_data(self, data_drame)
        return clean_data

# step - 4 -> run all the function and save the df into csv in data folder
    def step_5_run(self):
        self.setup()
        data_frame = self.scrape_captcha_page()
        self.driver.quit()
        data_frame.to_csv(r'C:\Users\sagar\OneDrive\Desktop\code\taiyo_de_assignment\pt-mesh-pipeline\data\before_cleaning.csv',index = False)
        clean_data = self.clean(data_frame)  # Clean the scraped data
        clean_data.to_csv(r'C:\Users\sagar\OneDrive\Desktop\code\taiyo_de_assignment\pt-mesh-pipeline\data\after_cleaning.csv',index = False)


if __name__ == "__main__":
    driver_path = r'C:\Users\sagar\Downloads\chromedriver-win32\chromedriver.exe'

    scraper = TenderScraper(driver_path)
    scraper.step_5_run()

