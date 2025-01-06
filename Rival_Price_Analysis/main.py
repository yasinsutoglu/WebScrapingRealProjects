from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re
import time
import pandas as pd

def main():
	SLEEP_TIME = 0.25
	BASE_URL = "https://books.toscrape.com/"
	def init_driver():
		options = webdriver.ChromeOptions()
		options.add_argument("--start-maximized")
		driver = webdriver.Chrome(options)
		return driver

	my_driver = init_driver()
	def get_categories_urls(driver,url):
		"""
		Get category urls from given homepage
		:param url: main url
		:return: category urls
		"""
		driver.get(url)
		time.sleep(SLEEP_TIME)
		category_elements_xpath = "//a[contains(text(),'Travel') or contains(text(), 'Nonfiction')]"
		# Get category elements by Xpath
		cat_els = driver.find_elements(By.XPATH, category_elements_xpath)
		# Obtain element urls
		cat_urls = [el.get_attribute('href') for el in cat_els]
		return cat_urls

	category_urls = get_categories_urls(my_driver, BASE_URL)
	def get_books_urls(driver, cat_urls):
		"""
		Get books urls from given (category detail) pages' urls
		:param driver:
		:param cat_urls:
		:return:
		"""
		book_elements_xpath = "//div[@class='image_container']//a"
		books_urls = []
		# Glance At Books in Category Pages
		for i in range(0, len(cat_urls)):
			num_pages = 3 # num_pages can be extracted from related page and used

			for k in range(1, num_pages):
				update_url = cat_urls[i] if k == 1 else cat_urls[i].replace("index", f"page-{k}")
				driver.get(update_url)
				book_els = driver.find_elements(By.XPATH, book_elements_xpath)
				if not book_els:
					break
				temp_urls = [book.get_attribute('href') for book in book_els]
				books_urls.extend(temp_urls)
				time.sleep(SLEEP_TIME)
		return books_urls

	books_urls = get_books_urls(my_driver, category_urls)
	def get_books_details(driver, books_urls):
		books_results = []
		for m in range(0, len(books_urls)):
			regex = re.compile("^star-rating")
			driver.get(books_urls[m])
			time.sleep(SLEEP_TIME)
			content_divs = driver.find_elements(By.XPATH, "//div[@class='content']")
			inner_html = content_divs[0].get_attribute('innerHTML')
			soup = BeautifulSoup(inner_html, 'html.parser')
			# get book name
			name_el = soup.find("h1")
			book_name = name_el.text
			# get book price
			price_el = soup.find("p", attrs={"class": "price-color"})
			if price_el:
				book_price = price_el.text
			else:
				book_price = None
			# get book rating
			rating_el = soup.find("p", attrs={"class": regex})
			star_cnt = rating_el["class"][-1]
			# get book description
			desc_el = soup.find("div", attrs={"id": "product_description"}).find_next_sibling()
			book_desc = desc_el.text
			# get book info's
			book_info = {}
			table_rows = soup.find("table").find_all('tr')

			for row in table_rows:
				key = row.find("th").text
				value = row.find("td").text
				book_info[key] = value

			temp_result = {'book_name': book_name,
					  'book_price': book_price,
					  'book_stars': star_cnt,
					  'book_description': book_desc, **book_info}

			books_results.append(temp_result)

		return books_results

	final_results = get_books_details(my_driver, books_urls)
	pd.set_option("display.max_columns", None)
	pd.set_option("display.max_colwidth", 40)
	pd.set_option("display.width", 2000)
	df = pd.DataFrame(final_results)
	return df


main()
df = main()
print(df.head())
print(df.shape)
