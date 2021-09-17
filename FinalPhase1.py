import pandas as pd
import requests
from pprint import pprint
import json
from bs4 import BeautifulSoup
import numpy as np


def clean_gov(filename):
	crimes = pd.read_csv(filename, delimiter = ";", index_col = 0, low_memory = False)
	#crimes["where"] = crimes["location_category"] == "TOWN OWNED" #all are Town owned
	count = 0
	y = 0
	drop_cols = ["ucr", "map_reference", "date_from", "date_to", "to_time", "district", "beat_number", "location", "id", "time_to", "time_from", "neighborhd_id", "apartment_complex", "chrgcnt", "activity_date", "phxrecordstatus", "phxstatus"]
	#removing columns with duplicate or irrelevant data

	for x in drop_cols:
		crimes = crimes.drop([x], axis = 1)
	#trial = crimes.iloc[1:400, :]
	#trial.drop(trial[trial["crime_type"] == "ALL OTHER"].index, inplace = True)
	crimes=crimes[crimes["crime_type"] != "ALL OTHER"]
	crimes=crimes[crimes["crime_type"] != "ALL OTHER - ALL TRAFFIC EXCEPT DWI (NON-UCR)"]
	#crimes.drop(crimes[crimes["crime_type"] == "ALL OTHER"].index, inplace = True)
	#return crimes.iloc[0:10000, :]
	crimes.sort_values(by = "year", inplace = True)
	crimes.to_csv("output.csv", index = True)
#clean_gov("cpd-incidents.csv")

def clean_api():
	url = "https://vt.ncsbe.gov/RegStat/Stats?Date=01/01/2004&CountyName=WAKE"
	
	for x in range(4,5):
		url_m = url[0:-18]
		if x < 10:
			url_m += "0" + str(x)
		else:
			url_m += str(x)
		url_m += "&CountyName=WAKE"
		r = requests.get(url_m)
		soup = BeautifulSoup(r.text, "html.parser")
		parser = Parser()
		tree = parser.parse(soup)
		fields = {getattr(node.left, 'value', ''): getattr(node.right, 'value', '')
          for node in nodevisitor.visit(tree)
          if isinstance(node, ast.Assign)}
		
		print(soup)
	
	
#clean_api()

def api(url, output_file):
	all_data = []
	years = []
	for x in range (1996, 2017, 4):
		years.append(x)
		url_year = url[0:30] + str(x) + url[34:]
		r = requests.get(url_year)
		soup = BeautifulSoup(r.text, "html.parser")
		table=soup.find_all('table',attrs={'class':'wikitable sortable'})
		rows=table[0].find_all('tr')
		mylist=[]
		data=[]
		for row in rows:
		    i=row.text.split('\n')
		    for e in i:
		        if e=='':
		            i.remove(e)
		    mylist.append(i)
		for row in mylist:
		    if 'Wake' in row:
		        data=[n for n in row[1:7]]
		all_data.append(data)
	columns = ["Democratic %", "Democratic #", "Republican %", "Republican #", "Independent %", "Independent #"]
	votes = np.array(all_data)
	voter_dataframe = pd.DataFrame(data = votes, columns = columns)
	voter_dataframe.index = years
	for x in range(0,3): #swap rep/dem for first 3 elections included
		dem_per = voter_dataframe.iloc[x,2]
		dem_num = voter_dataframe.iloc[x,3]
		rep_per = voter_dataframe.iloc[x,0]
		rep_num = voter_dataframe.iloc[x,1]
		voter_dataframe.iloc[x,0] = dem_per
		voter_dataframe.iloc[x,1] = dem_num
		voter_dataframe.iloc[x,2] = rep_per
		voter_dataframe.iloc[x,3] = rep_num
	total_votes = []
	for x in range(0, 6): 
		dem_num = str(voter_dataframe.iloc[x,1])
		rep_num = str(voter_dataframe.iloc[x,3])
		ind_num = str(voter_dataframe.iloc[x,5])
		total = int(dem_num.replace(",", "")) + int(rep_num.replace(",", "")) + int(ind_num.replace(",", ""))
		total_votes.append(total)

	voter_dataframe["Total Votes"] = np.array(total_votes)
	voter_dataframe.to_csv(output_file, index = True)
api("https://en.wikipedia.org/wiki/2016_United_States_presidential_election_in_North_Carolina", "Votes.csv")