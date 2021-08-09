import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import sys, os, re, time

# first step, get all models of brand by brand
def get_brand_model(input_list, driver):
	brand_model = []
	for brand in input_list:
		print(brand)
		url = "https://www.carcomplaints.com/"+brand+"/"
		# open webpage
		driver.get(url)
		# get html information for model
		# I open source code of webpage by control-shift-c, pinpoint desire pieces manually then copy xpath here
		element = driver.find_element_by_xpath('//*[@id="primary"]/div[3]/div[1]')
		model_info = bs(element.get_attribute('innerHTML'), 'html.parser')
		# based on copied html, find some pattern to pinpoint exact information, here, i first get all tag contains 'li', for those tag, find their first tag that contains 'a'
		model_info = [item.find_all('a')[0] for item in model_info.find_all('li')]
		for item in model_info:
			# 'brand', 'model', 'model_href'
			brand_model.append([brand]+item.contents+[item['href'].split('/')[2]])
		# have to ask program to stop for a while otherwise if I move on too quick the ip will be forbidden by the website
		time.sleep(5)
	pd.DataFrame(columns=['brand', 'model', 'model_href'], data=brand_model).to_csv('data/brand_model.csv', index=False)
	# return brand_model


# second step, get all years of each model based on brand, model
def get_brand_model_year(input_list, driver, partial = []):
	brand_model_year, last_brand = partial, False
	# brand_model_year, last_brand = [], False
	for item in input_list:
		brand, model, model_href = item
		print([brand, model])
		if brand != last_brand:
			# print(brand)
			last_brand = brand
			pd.DataFrame(columns=['brand', 'model', 'model_href', 'year'], data=brand_model_year).to_csv('data/brand_model_year.csv', index=False)
		url = "https://www.carcomplaints.com/"+brand+"/"+model_href+'/'
		# open page
		driver.get(url)
		try:
			# get html information for year
			# similar as code in function get_brand_model
			element = driver.find_element_by_xpath('//*[@id="primary"]/div[3]')
			print('success')
			year_info = bs(element.get_attribute('innerHTML'), 'html.parser')
			# similar as code in function get_brand_model
			year_info = [item.find_all('a')[0] for item in year_info.find_all('li')]
			for item in year_info:
				# 'brand', 'model', 'model_href' 'year'
				brand_model_year.append([brand, model, model_href, item['href'].split('/')[3]])
			time.sleep(8)
		except:
			# some page can not open or no complain for every years thus no complain so we can not get any our desire information, report error on 
			# driver.find_element_by_xpath('//*[@id="primary"]/div[3]')
			time.sleep(8)
			false_list.append(item)
			pd.DataFrame(columns=['brand', 'model', 'model_href'], data=false_list).to_csv('data/brand_model_year_false.csv', index=False)
			print('failed')
			continue
	pd.DataFrame(columns=['brand', 'model', 'model_href', 'year'], data=brand_model_year).to_csv('data/brand_model_year.csv', index=False)
	# return brand_model_year



# the third step, get all problems based on brand, model, year
def get_brand_model_year_problem(input_list, driver, partial = [], partial_false = False):
	# brand_model_year, last_brand = partial, False
	# brand_model_year_problem, last_brand, last_model = [], False, False
	false_list = pd.read_csv('data/brand_model_year_false.csv', sep=',').values.tolist()
	empty_list = pd.read_csv('data/brand_model_year_empty.csv', sep=',').values.tolist()
	yes_list = pd.read_csv('data/brand_model_year_problem.csv', sep=',')[['brand', 'model', 'model_href', 'year']].drop_duplicates().values.tolist()
	brand_model_year_problem, last_brand, last_model = partial, False, False
	for item in input_list:
		if item in false_list or item in yes_list or item in empty_list:
			continue
		# print(item)
		brand, model, model_href, year = item
		year = int(year)
		print([brand, model, year])
		if brand != last_brand or model != last_model:
			print([brand, model])
			last_brand, last_model = brand, model
			pd.DataFrame(columns=['brand', 'model', 'model_href', 'year', 'problem', 'problem_href', 'num_1', 'num_2'], data=brand_model_year_problem).to_csv('data/brand_model_year_problem.csv', index=False)
			pd.DataFrame(columns=['brand', 'model', 'model_href', 'year'], data=false_list).to_csv('data/brand_model_year_false.csv', index=False)
			pd.DataFrame(columns=['brand', 'model', 'model_href', 'year'], data=empty_list).to_csv('data/brand_model_year_empty.csv', index=False)
			pd.DataFrame(columns=['brand', 'model', 'model_href', 'year'], data=yes_list).to_csv('data/brand_model_year_true.csv', index=False)
		url = "https://www.carcomplaints.com/"+brand+"/"+model_href+'/'+str(year)+'/'
		driver.get(url)
		try:
			# get html information for problem
			element = driver.find_element_by_xpath('//*[@id="prbNav"]/a')
			summary_info = bs(element.get_attribute('innerHTML'), 'html.parser')
			judge_str = [item.contents for item in summary_info.find_all('span')][0][0]
			if judge_str == '0':
				time.sleep(10)
				empty_list.append([brand, model, model_href, year])
				print('no complain')
				continue
			else:
				element = driver.find_element_by_xpath('//*[@id="graph"]/ul')
				problem_info = bs(element.get_attribute('innerHTML'), 'html.parser')
				problem_info = [item.find_all('a')[0] for item in problem_info.find_all('li')]
				for item in problem_info:
					# 'brand', 'model', 'model_href' 'year' 'problem'  'problem_href' 'num'
					item_content = [item.findAll(text=True)][0]
					# only have one type of complain
					if len(item_content) == 2:
						# complain all from another website
						if ':' in item_content[1]:
							num2 = int(item_content[1].split(':')[1])
							num1 = 0
						# complain all from this website
						else:
							num1 = int(item_content[1])
							num2 = 0
					elif len(item_content) == 3:
					# have two type of complain
						if ':' in item_content[1] and ':' not in item_content[2]:
							num1, num2 = int(item_content[2]), int(item_content[1].split(':')[1])
						elif ':' in item_content[2] and ':' not in item_content[1]:
							num1, num2 = int(item_content[1]), int(item_content[2].split(':')[1])
						else:
							sys.exit('different data')
					else:
						sys.exit('different data')
					brand_model_year_problem.append([brand, model, model_href, year, item_content[0], item['href'].split('/')[0], num1, num2])
				time.sleep(10)
				yes_list.append([brand, model, model_href, year])
				print('success')
		except:
			time.sleep(10)
			false_list.append([brand, model, model_href, year])
			print('failed')
			continue
	pd.DataFrame(columns=['brand', 'model', 'model_href', 'year'], data=yes_list).to_csv('data/brand_model_year_true.csv', index=False)
	pd.DataFrame(columns=['brand', 'model', 'model_href', 'year', 'problem', 'problem_href', 'num_1', 'num_2'], data=brand_model_year_problem).to_csv('data/brand_model_year_problem.csv', index=False)
	pd.DataFrame(columns=['brand', 'model', 'model_href', 'year'], data=false_list).to_csv('data/brand_model_year_false.csv', index=False)
	pd.DataFrame(columns=['brand', 'model', 'model_href', 'year'], data=empty_list).to_csv('data/brand_model_year_empty.csv', index=False)
	# return brand_model_year_problem



def main():
	# brand_list = ["Acura","Audi","BMW","Buick","Cadillac","Chevrolet","Chrysler","Dodge","Ford","Genesis","GMC","Honda","Hyundai","Infiniti","Jeep","Kia","Lexus","Lincoln","Mazda","Mercedes-Benz","Mercury","Mini","Mitsubishi","Nissan","Oldsmobile","Plymouth","Pontiac","Porsche","Ram","Saturn","Scion","Subaru","Tesla","Toyota","Volvo","Volkswagen","Alfa_Romeo","AMC","Bentley","Chery","Daewoo","Datsun","Daihatsu","Eagle","Ferrari","Fiat","Geo","Holden","HSV","Hummer","Isuzu","Jaguar","Kenworth","Lamborghini","Land_Rover","Lotus","Mahindra","Maruti","Maserati","Opel","Peugeot","Renault","Rover","Saab","Seat","Skoda","Smart","Ssangyong","Suzuki","Tata","Vauxhall","Yugo","Zimmer"]
	# brand_list.sort()
	options = webdriver.ChromeOptions()
	options.add_argument('--ignore-certificate-errors')
	options.add_argument("--test-type")
	driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
	time.sleep(10)
	####### I got brand manually, actually we can get this automatically, you can try
	brand_list = pd.read_csv('data/brand.csv', header = 0, sep = ',')['brand'].tolist()
	get_brand_model(brand_list)

	# this step tooks long..... time 
	brand_model_list = pd.read_csv('data/brand_model.csv', sep = ',').values.tolist()
	brand_model_year_list = pd.read_csv('data/brand_model_year.csv', sep = ',', header= 0).values.tolist()
	get_brand_model_year(brand_model_list, driver, brand_model_year_list)

	brand_model_year_list = pd.read_csv('data/brand_model_year.csv', sep = ',').values.tolist()
	# I use other names because sometime internet will disconnect, so I have to run code based on last stored result, this step tooks long.  long .... long ...... time
	# # brand_model_year_false_list = pd.read_csv('data/brand_model_year_false.csv', sep=',').values.tolist()
	brand_model_year_problem_list = pd.read_csv('data/brand_model_year_problem.csv', sep = ',').values.tolist()
	get_brand_model_year_problem(brand_model_year_list, driver, partial =brand_model_year_problem_list)


if __name__ == "__main__":
    main()
