import os 
# import shutil
import pandas as pd


# align brand
os.chdir(r'C:\Users\Derek\Desktop\Python Car Data')
sale_data = pd.read_csv('data/sale_amount.csv', sep=',')
sale_brand = set(sale_data['brand'].tolist())

carcomplain_brand = pd.read_csv('data/brand.csv', sep=',', header =0)['brand'].tolist()

output = []

for brand in carcomplain_brand:
	if brand in sale_brand:
		output.append([brand, brand])
	elif brand.lower() in sale_brand:
		output.append([brand.lower(), brand])
	elif ' '.join(brand.split('-')).lower() in sale_brand:
		output.append([' '.join(brand.split('-')).lower(), brand])
	elif ' '.join(brand.split('_')).lower() in sale_brand:
		output.append([' '.join(brand.split('_')).lower(), brand])
	else:
		print(brand)

pd.DataFrame(columns=['brand', 'brand_carcomplain'], data=output).to_csv('data/brand_map.csv', index=False)








#modify sale data
sale_data = pd.read_csv('data/sale_amount.csv', sep=',')

# sale_data = pd.read_csv('data/sale_partial.csv', sep=',')
def merge_sale_models(df, brand, model_list, new_model):
	# find subset and delete
	sub_df = df[df['brand']==brand][df['model'].isin(model_list)]
	print([df.shape, sub_df.shape])
	print(set(sub_df['model'].tolist()))
	tmp_df = df[~df.index.isin(list(sub_df.index))]
	# merge subset
	sub_df = sub_df.replace(to_replace=model_list, value = new_model)
	aggregation_functions = {'amount': 'sum'}
	sub_df = sub_df.groupby(['brand','model','year']).aggregate(aggregation_functions).reset_index()
	# combine
	df = pd.concat([tmp_df, sub_df]).sort_values(["brand", "model", 'year'], ascending = (True, True, True)).reset_index(drop=True)
	print([sub_df.shape, tmp_df.shape, df.shape])
	print('----')    
	return df

def replace_models(df, brand, map_dict):
	# find subset and delete
	sub_df = df[df['brand']==brand][df['model'].isin(map_dict.keys())]
	print(set(sub_df['model'].tolist()))
	tmp_df = df[~df.index.isin(list(sub_df.index))]
	# replace
	for key,value in map_dict.items():
		sub_df = sub_df.replace(to_replace=key, value = value)
	# combine
	df = pd.concat([tmp_df, sub_df]).sort_values(["brand", "model", 'year'], ascending = (True, True, True)).reset_index(drop=True)
	print(set(sub_df['model'].tolist()))
	print([sub_df.shape, tmp_df.shape, df.shape])
	print('----')  
	return df 


# cadillac s merge escalade-esv escalade 
sale_data = merge_sale_models(sale_data, 'cadillac', ['escalade-esv', 'escalade'], 'escalade')
# chevrolet s 'captiva-sport': 'captiva'  'bolt-ev': 'bolt' 
sale_data = replace_models(sale_data, 'chevrolet', {'captiva-sport': 'captiva', 'bolt-ev': 'bolt'})
# chrysler s 'pacifica-minivan': 'pacifica'
sale_data = replace_models(sale_data, 'chrysler', {'pacifica-minivan': 'pacifica'})
# gmc s merge 'yukon' 'yukon-xl'
sale_data = merge_sale_models(sale_data, 'gmc', ['yukon','yukon-xl'], 'yukon')
# hyundai s 'genesis-sedan': 'genesis' cc merge ioniq
sale_data = replace_models(sale_data, 'hyundai', {'genesis-sedan': 'genesis'})
# land rover s lr2 freelander: lr2 lr4 lr3 discovery: discovery
sale_data = replace_models(sale_data, 'land rover', {'lr2 freelander': 'lr2', 'lr4 lr3 discovery': 'discovery'})
# lincoln s 'continental-new': 'continental' 'corsair-mkc': 'mkc'
sale_data = replace_models(sale_data, 'lincoln', {'continental-new': 'continental', 'corsair-mkc': 'mkc'})
# mini s need delete ','  already done  'roadster': 'cooper_roadster' merge 'hardtop 4 door' and 'cooper'
sale_data = replace_models(sale_data, 'mini', {'roadster': 'cooper_roadster'})
sale_data = merge_sale_models(sale_data, 'mini', ['hardtop 4 door', 'cooper'], 'cooper')
# nissan s 'x-terra': 'xterra'
sale_data = replace_models(sale_data, 'nissan', {'x-terra': 'xterra'})
# ram s 'cargo-van' : 'cargo'
sale_data = replace_models(sale_data, 'ram', {'cargo-van' : 'cargo'})
# toyota s 'corolla-sedan': 'corolla'
sale_data = replace_models(sale_data, 'toyota', {'corolla-sedan': 'corolla'})
# volkswagen s merge 'tiguan' and 'tiguan-l'
sale_data = merge_sale_models(sale_data, 'volkswagen', ['tiguan', 'tiguan-l'], 'tiguan')
# # volvo cc merge s90 v90  s60 v60    s merge 's90' 's90-v90' to s90
# sale_data = merge_sale_models(sale_data, 'volvo', ['s90','s90-v90'], 's90')
# sale_data = merge_sale_models(sale_data, 'volvo', ['s60','s60-v60'], 's60')
sale_data[sale_data['year'] >=2014][sale_data['amount']>=5000].to_csv('data/sale_partial.csv',index=False)






# modify carcomplain data
carcomplain_data = pd.read_csv('data/brand_model_year_problem.csv', sep=',')
carcomplain_data[carcomplain_data['year'] >=2014].to_csv('data/carcomplain_partial.csv',index=False)

carcomplain_data = pd.read_csv('data/carcomplain_partial.csv', sep=',')

def merge_carcomplain_models(df, brand, model_key_list, new_model_list, new_href_list):
	# find subset and delete
	assert len(model_key_list) == len(new_model_list) and len(model_key_list) == len(new_href_list)
	for i in range(len(model_key_list)):
		model_key, new_model, new_href = model_key_list[i], new_model_list[i], new_href_list[i]
		df['model'] = df['model'].astype(str)
		sub_df = df[df['brand']==brand][df['model'].str.startswith(model_key)]
		tmp_df = df[~df.index.isin(list(sub_df.index))]
		print(sub_df)
		# merge subset
		sub_df = df[df['brand']==brand][df['model'].str.startswith(model_key)].reset_index(drop=True)
		sub_df['model'] = pd.Series([new_model] * len(sub_df))
		sub_df['model_href'] = pd.Series([new_href] * len(sub_df))
		aggregation_functions = {'num_1': 'sum', 'num_2':'sum'}
		sub_df = sub_df.groupby(['brand','model', 'model_href','year', 'problem', 'problem_href']).aggregate(aggregation_functions).reset_index()
		# combine
		df = pd.concat([tmp_df, sub_df]).sort_values(["brand", "model", 'year'], ascending = (True, True, True)).reset_index(drop=True)
		print(sub_df)
		print([sub_df.shape, tmp_df.shape, df.shape])
		print('----')  
	return df

# Alfa_Romeo
carcomplain_data = replace_models(carcomplain_data, 'Alfa_Romeo', {'Giulia Quadrifoglio': 'Giulia'})
# bmw cc 2-8 series (8-series) need merge href: 228, 328 435 528 650 750 i8
carcomplain_data = merge_carcomplain_models(carcomplain_data, 'BMW', 
	['2', '3','4','5','6','7'], ['2-series', '3-series', '4-series', '5-series','6-series','7-series'], 
	['228', '328', '435', '528', '650', '750'])
carcomplain_data = replace_models(carcomplain_data, 'BMW', {'i8': '8-series'})
# 'chevrolet' cc Silverado
carcomplain_data = merge_carcomplain_models(carcomplain_data, 'Chevrolet', 
	['Silverado'], ['silverado'], ['Silverado_1500'])
# 'chrysler' cc Town & Country: town country
carcomplain_data = replace_models(carcomplain_data, 'Chrysler', {'Town & Country': 'town country'})
# ford cc merge f-series e-seires
carcomplain_data = merge_carcomplain_models(carcomplain_data, 'Ford', 
	['E-', 'F-'], ['e-series', 'f-series'], ['E-350', 'F-150'])
# GMC cc merge Sierra
carcomplain_data = merge_carcomplain_models(carcomplain_data, 'GMC', 
	['Sierra'], ['sierra'], ['Sierra_1500'])
# hyundai cc merge ioniq
carcomplain_data = merge_carcomplain_models(carcomplain_data, 'Hyundai', 
	['Ioniq'], ['ioniq'], ['Ioniq_Electric'])
# lexus cc merge 'lc', 'es', 'gs', 'is', 'rc', 'ls'
# 'ct': 'ct 200h', 'lx', 'ux', 'rx', 'gx'
carcomplain_data = merge_carcomplain_models(carcomplain_data, 'Lexus', 
	['LC', 'ES', 'GS', 'IS', 'RC', 'LS', 'LX', 'RX', 'GX'], 
	['lc', 'es', 'gs', 'is', 'rc', 'ls', 'lx', 'rx', 'gx'], 
	['LC_500', 'ES_350', 'GS_350', 'IS_350', 'RC_350', 'LS_460', 'LX_570', 'RX_350', 'GX_460'])
carcomplain_data = replace_models(carcomplain_data, 'Lexus', {'CT 200h': 'ct'})
# mercedes benz cc merge 
carcomplain_data = merge_carcomplain_models(carcomplain_data, 'Mercedes-Benz', 
	['CLA', 'CLS', 'GLC', 'GLE', 'GLK', 'ML'], 
	['cla', 'cls', 'glc', 'gle', 'glk',  'm-class'], 
	['CLA250', 'CLS550','GLC350', 'GLE350', 'GLK350', 'ML350'])
carcomplain_data = replace_models(carcomplain_data, 'Mercedes-Benz', 
	{'A220': 'a-class', 'C300': 'c-class', 'E350': 'e-class', 'G550': 'g-class', 'GL450':'gl',
	'GLA250': 'gla' , 'GLB250': 'glb', 'S450': 's-class', 'S550': 's-class', 'S63': 's-class'})
# porsche cc merge 718
carcomplain_data = merge_carcomplain_models(carcomplain_data, 'Porsche', 
	['718'], ['718'], ['718_Cayman'])
# Volvo merge v60s60 


carcomplain_data.to_csv('data/carcomplain_partial.csv',index=False)




# align model
sale_data = pd.read_csv('data/sale_partial.csv', sep=',')[['brand', 'model']]
brand_map = pd.read_csv('data/brand_map.csv', sep=',').to_dict(orient='records')
brand_dict= {}
for item in brand_map:
	brand_dict[item['brand']] = item['brand_carcomplain']

carcomplain_brand = pd.read_csv('data/carcomplain_partial.csv', sep=',', header =0)[['brand', 'model']].drop_duplicates()


brand_list, final = list(brand_dict.keys()), []
for i in range(len(brand_list)):
	brand = brand_list[i]
	table_carcomplain_model = carcomplain_brand[carcomplain_brand['brand']==brand_dict[brand]]['model'].tolist()
	table_sale_model = set(sale_data[sale_data['brand']==brand]['model'].tolist())
	carcomplain_left_list, output = [],  []
	for model in table_carcomplain_model:
		if model in table_sale_model:
			output.append([brand, model, brand_dict[brand], model])
		elif model.lower() in table_sale_model:
			output.append([brand, model.lower(), brand_dict[brand], model])
		elif ' '.join(model.split('-')).lower() in table_sale_model:
			output.append([brand, ' '.join(model.split('-')).lower(), brand_dict[brand], model])
		elif '_'.join(model.split('-')).lower() in table_sale_model:
			output.append([brand, '_'.join(model.split('-')).lower(), brand_dict[brand], model])
		elif ' '.join(model.split('_')).lower() in table_sale_model:
			output.append([brand, ' '.join(model.split('_')).lower(), brand_dict[brand], model])
		elif '-'.join(model.split('_')).lower() in table_sale_model:
			output.append([brand, '-'.join(model.split('_')).lower(), brand_dict[brand], model])
		elif '-'.join(model.split(' ')).lower() in table_sale_model:
			output.append([brand, '-'.join(model.split(' ')).lower(), brand_dict[brand], model])
		elif '_'.join(model.split(' ')).lower() in table_sale_model:
			output.append([brand, '_'.join(model.split(' ')).lower(), brand_dict[brand], model])
		else:
			carcomplain_left_list.append(model)

	tmp, sale_left_list = [item[1] for item in output], []
	for item in table_sale_model:
		if item not in tmp:
			sale_left_list.append(item)
	if sale_left_list != [] and carcomplain_left_list != []:
		print([i,brand])
		print(table_sale_model)
		print(table_carcomplain_model)
		print('-------------')
		print(sale_left_list)
		print(carcomplain_left_list)
		print('-----------------------------------')
	final += output



pd.DataFrame(columns=['brand_sale', 'model_sale','brand_carcomplain', 'model_carcomplain'], data=final).to_csv('data/brand_model_map.csv', index=False)

