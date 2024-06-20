import os, re, json
import pdfplumber

date_pattern = "^[0-9]{1,2}\\/[0-9]{1,2}\\/[0-9]{4}$"

path = 'D:/Data/Conduit Reports'

conduit_records = []
 
for folder in os.scandir(path):
	folder_path = os.path.join(path, folder)
	for filename in os.listdir(folder_path):
		f = os.path.join(folder_path, filename)
		if os.path.isfile(f):
			print(f)

		with pdfplumber.open(f) as pdf:
			current_table_type = 'id' # other options are 'transfers', 'RRS', 'CCS', RCS'
			current_receiver = None
			receiver_list = []

			conduit = {}
			conduit['transfers'] = []
			conduit['receivers'] = []
			conduit['donations'] = []
			conduit['redirects'] = []

			for page in pdf.pages:
				tables = page.extract_tables(table_settings={})
				for table in tables:
					if table[0][0] == 'S.No':
						current_table_type = 'transfers'
					elif table[0][0] == 'Receiving Registrant Name and Address':
						current_table_type = 'RRS'
					elif table[0][0] == 'Date':
						current_table_type = 'CCS'
					elif table[0][0] == 'Date of Redirection':
						current_table_type = 'RCS'
					elif table[0][0] == 'Date of\nRedirection':
						current_table_type = 'RCS'

					for row in table:
						if current_table_type == 'id':
							if row[0] == 'Filing Period Name:':
								conduit['filing_period'] = row[1]
								year = int(re.search(r'\d+', row[1]).group())
								if 'Janurary Continuing' in row[1]:
									year -= 1
								conduit['year'] = year
							elif row[0] == 'Name of Conduit Fund:':
								conduit['name'] = row[1]
							elif row[0] == 'Street Address:':
								conduit['address'] = row[1]
							elif row[0] == 'City, State and Zip Code:':
								conduit['address'] += ' ' + row[1]
							elif row[0] == 'Email:':
								conduit['email'] = row[1]
						elif current_table_type == 'transfers':
							if len(row) < 4:
								pass
							elif row[0] == 'S.No':
								pass
							elif row[0] == 'CONTRIBUTIONS GIVEN THIS REPORT PERIOD':
								conduit['total'] = int(float(row[-1].strip('$').replace(',','')))
							else:
								transfer = {}
								transfer['date'] = row[1]
								text = row[2].split(',')
								transfer['receiver_name'] = text[0]
								receiver_list.append(text[0])
								transfer['address'] = ' '.join(text[1:])
								transfer['amount'] = int(float(row[3].strip('$').replace(',','')))
								conduit['transfers'].append(transfer)
						elif current_table_type == 'RRS':
							if len(row) < 2:
								pass
							
							elif row[0] == 'Receiving Registrant Name and Address':
								pass
							elif row[1] == None:
								pass
							elif row[0] == 'Sub Total':
								pass
							elif row[0] == 'Total Conduit Contributions':
								pass
							elif row[0] == 'Total Redirected Contributions':
								pass
							elif row[0] == 'Grand Total':
								pass
							else:
								receiver = {}
								text = row[0].split(',')
								receiver['receiver_name'] = text[0]
								receiver['address'] = ' '.join(text[1:])
								receiver['amount'] = int(float(row[1].strip('$').replace(',','')))
								conduit['receivers'].append(receiver)
						elif current_table_type == 'CCS':
							if len(row) < 5:
								pass
							elif row[0] == 'Date':
								pass
							elif row[3] == None:
								if row[0] in receiver_list:
									current_receiver = row[0]
								pass
							else:
								donation = {}
								donation['date'] = row[0]
								donation['donor_name'] = row[1]
								donation['address'] = row[2]
								donation['occupation'] = row[3]
								donation['amount'] = int(float(row[4].strip('$').replace(',','')))
								donation['receiver_name'] = current_receiver
								conduit['donations'].append(donation)
						elif current_table_type == 'RCS':
							if len(row) < 6:
								pass
							elif row[0] == 'Date of Redirection' or row[0] == 'Date of\nRedirection':
								pass
							elif row[3] == None:
								pass
							else:
								redirect = {}
								redirect['date_of_redirect'] = row[0]
								redirect['date_of_contribution'] = row[1]
								redirect['donor_name'] = row[2]
								redirect['address'] = row[3]
								donation['occupation'] = row[4]
								donation['amount'] = int(float(row[5].strip('$').replace(',','')))
								conduit['redirects'].append(redirect)
			conduit_records.append(conduit)

conduits = {}

for record in conduit_records:
	if not record['name'] in conduits:
		conduits[record['name']] = {}
		conduit = conduits[record['name']]
		conduit['name'] = record['name']
		conduit['address'] = record['address']
		conduit['email'] = record['email']
		
		conduit['transfers'] = []
		conduit['receivers'] = []
		conduit['donations'] = []
		conduit['redirects'] = []

		conduit['lifetime_total'] = 0
		conduit['2020_cycle_total'] = 0
		conduit['2022_cycle_total'] = 0
		conduit['2024_cycle_total'] = 0

	conduit = conduits[record['name']]
	conduit['transfers'].extend(record['transfers'])
	conduit['receivers'].extend(record['receivers'])
	conduit['donations'].extend(record['donations'])
	conduit['redirects'].extend(record['redirects'])

	conduit['lifetime_total'] += record['total']
	if record['year'] == 2019 or record['year'] == 2020:
		conduit['2020_cycle_total'] += record['total']
	if record['year'] == 2021 or record['year'] == 2022:
		conduit['2022_cycle_total'] += record['total']
	if record['year'] == 2023 or record['year'] == 2024:
		conduit['2024_cycle_total'] += record['total']

with open("conduit_data.json", "w") as f:
	json.dump(conduits, f)