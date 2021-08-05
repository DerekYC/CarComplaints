import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import sys
import time 

# from https://carsalesbase.com/car-sales-us-home-main/car-sales-by-brand-us/
# another: https://www.goodcarbadcar.net/2019-us-vehicle-sales-figures-by-model/

#get webpage source code of a particular model and brand
def download_html(brand, model):
	if brand:
		url = 'https://carsalesbase.com/us-'+ brand + '-'+ model+'/'
	else:
		url = 'https://carsalesbase.com/us-'+ model + '/'
	r = requests.get(url, allow_redirects=True)
	if r.content[:35] == b'<!DOCTYPE html>\n<html lang="en-US">':
		return r
	else:
		return False

#identify the sales table source code
#store the information into rows variable

def find_target_table(html_original, brand,  model):
	bs_info = bs(html_original.content, 'html.parser')
	tablehtmls = bs_info.find_all('table', attrs={'class': "model-table"})
	rows = False
	for item in tablehtmls:
		rows = item.find_all('tr')
		first_row = rows[0].find_all('td')
		if len(first_row) !=2:
			continue
		elif len(first_row[1].find_all('h5')) != 2:
			continue
		else:
			try: 
				brand_html, model_html = [tag.contents[0] for tag in first_row[1].find_all('h5')]
			except:
				brand_html, model_html = [tag.contents[0] for tag in first_row[1].find_all('h5')][:2]
				print('have more information')
			if brand != brand_html.lower():
				brand = '-'.join(brand.split(' ')) 
				if brand!= model_html.lower():
					print(['different brand name', brand, brand_html.lower()])
			if model != model_html.lower():
				model = ' '.join(model.split('-')) 
				if model != model_html.lower():
					print(['different model name', model, model_html.lower()])
			break
	return rows

	
#change information to pandas data format	

def table_to_df(html_rows, brand, model):
	output = []
	for row in html_rows[1:]:
		year_html, amount_html = [tag.contents[0] for tag in row.find_all('td')][:2]
		if '.' in amount_html:
			amount_html = float(amount_html) * 1000
		else:
			amount_html = float(amount_html)
		output.append([brand, model, year_html, amount_html])
	return pd.DataFrame(columns=['brand', 'model', 'year', 'amount'], data=output)


def get_model(brand,model, result):
	if model[-1] == "*":
		model = model[:-1]
		html_original = download_html(False, model)
	else:
		html_original = download_html(brand, model)
	if '-' in brand:
		brand = ' '.join(brand.split('-'))
	# if '-' in model:
	# 	model = ' '.join(model.split('-'))
	if html_original:
		rows = find_target_table(html_original, brand, model)
		if rows:
			result.append(table_to_df(rows, brand, model))
		else:
			print('find table error')
	else:
		print('download error')

def main():
	brand = sys.argv[1].lower()
	models = [model.lower() for model in sys.argv[2:]]
	final = []
	for model in models:
		print([brand, model])
		get_model(brand, model, final)
		time.sleep(5)
	final = pd.concat(final)
	final.to_csv(brand+'.csv', index = False)


if __name__ == "__main__":
    main()

