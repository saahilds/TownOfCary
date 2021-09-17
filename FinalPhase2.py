from pprint import pprint
import requests,csv,re
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

def data_parser(filename):
    crimes = pd.read_csv(filename, delimiter = ";", index_col = 0, low_memory = False)
    drop_cols = ["ucr", "map_reference", "date_from", "date_to", "to_time", "district", "beat_number", "location", "id", "time_to", "time_from", "neighborhd_id", "apartment_complex", "chrgcnt", "activity_date", "phxrecordstatus", "phxstatus"]

    #removing columns with duplicate or irrelevant data
    for x in drop_cols:
        crimes = crimes.drop([x], axis = 1)
        crimes=crimes[crimes["crime_type"] != "ALL OTHER"]
        crimes=crimes[crimes["crime_type"] != "ALL OTHER - ALL TRAFFIC EXCEPT DWI (NON-UCR)"]
        crimes.sort_values(by = "year", inplace = True)
    crimes.to_csv("crimes.csv", index = True)

data_parser("cpd-incidents.csv")

def web_parser1(log_file):
    resp=requests.get('https://worldpopulationreview.com/us-cities/cary-nc-population')
    soup=BeautifulSoup(resp.text, "html.parser")
    table=soup.find_all('table',{'class':'jsx-1487038798 table table-striped tp-table-body'})
    by_year=table[len(table)-1].find_all('tr')
    by_race=table[0].find_all('tr')
    by_education=table[3].find_all('tr')
    by_poverty=table[6].find_all('tr')
    pop_year=[]
    pop_race=[]
    pop_education=[]
    pop_poverty=[]

    for row in by_year[1:]:
        data=row.find_all('td')
        year=data[0].text
        population=data[1].text
        growth=data[2].text
        pop_year.append([year,population,growth])
 
    for row in by_race[1:]:
        data=row.find_all('td')
        race=data[0].text
        population=data[1].text
        percentage=data[2].text
        pop_race.append([race,population,percentage])
 
    for row in by_education[1:]:
        data=row.find_all('td')
        edu_level=data[0].text
        count=data[1].text
        percentage=data[2].text
        pop_education.append([edu_level,count,percentage])
 
    for row in by_poverty[1:]:
        data=row.find_all('td')
        race=data[0].text
        total=data[1].text
        num_poverty=data[2].text
        percentage_poverty=data[3].text
        pop_poverty.append([race,total,num_poverty,percentage_poverty])
 
    try:
        open(log_file,newline = "").close()
    except FileNotFoundError:
        with open(log_file,"w",newline = "") as f:
            writer=csv.writer(f)
            writer.writerow(["Year", "Population", "Growth"])
            for i in range (len(pop_year)):
                writer.writerow([pop_year[i][0], pop_year[i][1],pop_year[i][2]])
                writer.writerow('\n\n')
            writer.writerow(["Race", "Population", "Percentage"])
            for i in range (len(pop_race)):
                writer.writerow([pop_race[i][0], pop_race[i][1],pop_race[i][2]])
                writer.writerow('\n\n')
            writer.writerow(["Education Level", "Population", "Percentage"])
            for i in range (len(pop_education)):
                writer.writerow([pop_education[i][0], pop_education[i][1],pop_education[i][2]])
                writer.writerow('\n\n')
            writer.writerow(["Race", "Total", "Poverty", "Percentage"])
            for i in range (len(pop_poverty)):
               writer.writerow([pop_poverty[i][0], pop_poverty[i][1],pop_poverty[i][2],pop_poverty[i][3]])
web_parser1("population.csv")
 
 
def web_parser2(url, output_file):
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
web_parser2("https://en.wikipedia.org/wiki/2016_United_States_presidential_election_in_North_Carolina", "Votes.csv")