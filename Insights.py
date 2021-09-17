from pprint import pprint
import requests,csv,re
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

 

def insight1(filename,votes,population):
    outcomelist=[]
    poplist=[]
    with open(votes) as v:
        outcome=csv.reader(v)
        outcomelist=[i for i in outcome]
    with open(population) as p:
        pop=csv.reader(p)
        poplist=[i for i in pop]
 
    years=[row[0] for row in outcomelist[1:]]
    columns=["Year", "Population", "Growth","Total Votes","Winning Party"]
    data=[]
    for year in outcomelist[1:]:
        if year[2]>year[4]:
            winner='Democratic Party'
        else:
            winner='Republican Party'
        row=[year[0],0,0,year[-1],winner]
        data.append(row)
        row=[]
    for pop in poplist[1:]:
        for row in data:
            try:
                if int(pop[0])==int(row[0]):
                    row[1]=pop[1]
                    row[2]=pop[2]
            except:
                continue
    df=pd.DataFrame(data = data, columns = columns)
    #fixing 1996 with 1990
    df.loc[0][1] = poplist[25][1]
    df.loc[0][2] = poplist[25][2]
    print(poplist[23][1])
    first = int(poplist[23][1].replace(",","")) + (int(poplist[23][1].replace(",","")) - int(poplist[25][1].replace(",","")))/2
    first_g = int(poplist[23][2].replace(",","")) + (int(poplist[23][2].replace(",","")) - int(poplist[25][2].replace(",","")))/2
    df.loc[2][1] = str(first)[0:3] + "," + str(first)[3:-2]
    df.loc[2][2] = str(first_g)[0:2] + "," + str(first_g)[2:-2]
    df.loc[3][1] = poplist[21][1]
    df.loc[3][2] = poplist[21][2]

    df.to_csv(filename, index = False)


insight1("Insight1.csv","Votes.csv","population.csv")
 

def insight2(filename,votes,crimes):
    outcomelist=[]
    crimelist=[]
    with open(votes) as v:
        outcome=csv.reader(v)
        outcomelist=[i for i in outcome]
    with open(crimes) as c:
        crime=csv.reader(c)
        crimelist=[i for i in crime]
    years=[row[0] for row in outcomelist[1:]]
    columns=["Year", "Number of Crimes","Winning Party"]
    data=[]
    for year in outcomelist[1:]:
        if year[2]>year[4]:
            winner='Democratic Party'
        else:
            winner='Republican Party'
        row=[year[0],0,winner]
        data.append(row)
        row=[]
    for crime in crimelist[1:]:
        for row in data:
            try:
                if int(crime[-1][:4]) >= int(row[0]) and int(crime[-1][:4]) < int(row[0]) + 4:
                    row[1]+=1
            except:
                continue
    df=pd.DataFrame(data = data, columns = columns)
    
    df.to_csv(filename, index = False)
    return df
insight2("Insight2.csv","Votes.csv","crimes.csv")

def insight3(filename, crimes):
    crimelist=[]
    with open(crimes) as c:
        crime=csv.reader(c)
        crimelist=[i for i in crime]
    years=[]
    for row in crimelist[1:]:
        if row[-1] not in years and row[-1]!="":
            years.append(row[-1])
    Category={}
    for row in crimelist[1:]:
        if row[14] not in Category and row[14]!="":
            Category[row[14]]=0
    columns=['Year']
    for i in Category:
        columns.append(i)
    columns.append('Number of Domestic')
    columns.append('Total Number')
    data=[]
    for year in years:
        row=[0 for i in range(len(columns))]
        row[0]=int(year[:4])
        data.append(row)
        row=[]
    for crime in crimelist[1:]:
        for row in data:
            try:
                if int(crime[-1][:4])==row[0]:
                    row[-1]+=1
                    if crime[17]=="Y":
                        row[-2]+=1
                    for i in range(1,len(columns)-2):
                        if columns[i]==crime[14]:
                            row[i]+=1
            except:
                continue
    crimes_df = pd.DataFrame(data = data, columns = columns)
    crimes_df.to_csv(filename, index = False)
    return crimes_df
insight3("Insight3.csv","crimes.csv")

#This insight shows proportions of each crime category committed in each election year
def insight4(output_file):
    crimes_df = insight3("Insight3.csv","crimes.csv")
    crimes_df.set_index("Year", inplace = True)
    #return type(crimes_df.loc[1997])
    #return crimes_df.loc[1997][2]
    election_years = [1996]
    for x in range(2000,2017,4):
        election_years.append(x)
    #return crimes_df
    crimes_perc = pd.DataFrame(columns = ["Infraction(%)", "Misdemeanor(%)", "Felony(%)", "Election Year"])
    crimes_perc["Election Year"] = election_years
    crimes_perc.set_index("Election Year", inplace = True)
    infraction_list = [0,12,16,23,25,26]
    misdemeanor_list = [1,2,3,6,7,8,12,13,14,15,19,20,21]
    felony_list = [4,5,9,10,11,17,18,19,22,24]
    for year in election_years:
        infractions = 0
        midemeanors = 0
        felonies = 0
        for x in infraction_list:
            if year == 1996:
                infractions += crimes_df.loc[1997][x]
            else:
                infractions += crimes_df.loc[year][x]
        for x in misdemeanor_list:
            if year == 1996:
                midemeanors += crimes_df.loc[1997][x]
            else:
                midemeanors += crimes_df.loc[year][x]
        for x in felony_list:
            if year == 1996:
                felonies += crimes_df.loc[1997][x]
            else:
                felonies += crimes_df.loc[year][x]

        if year == 1996:
            crimes_perc.loc[year]["Infraction(%)"] = round(infractions/crimes_df.loc[1997][28] * 100, 2)
            crimes_perc.loc[year]["Misdemeanor(%)"] = round(midemeanors/crimes_df.loc[1997][28] * 100, 2)
            crimes_perc.loc[year]["Felony(%)"] = round(felonies/crimes_df.loc[1997][28] * 100, 2)
        else:
            crimes_perc.loc[year]["Infraction(%)"] = round(infractions/crimes_df.loc[year][28] * 100, 2)
            crimes_perc.loc[year]["Misdemeanor(%)"] = round(midemeanors/crimes_df.loc[year][28] * 100, 2)
            crimes_perc.loc[year]["Felony(%)"] = round(felonies/crimes_df.loc[year][28] * 100, 2)
        crimes_perc.to_csv(output_file, index = True)
    return crimes_perc
insight4("Insight4.csv")
def insight5(afilename,bfilename,population):
    with open(population) as p:
        pop=csv.reader(p)
        poplist=[i for i in pop]
    acount=-1
    bcount=-1
    ccount=-1
    for row in poplist:
        acount+=1
        if 'Race' in row:
            break
    for row in poplist:
        bcount+=1
        if 'Education Level' in row:
            break
    for row in poplist:
        ccount+=1
        if 'Poverty' in row:
            break
    data1=poplist[acount:bcount]
    for row in data1:
        if '\n' in row:
            data1.remove(row)
    data2=poplist[ccount:]
    for row in data2:
        if '\n' in row:
            data2.remove(row)
    df1=pd.DataFrame(data = data1[1:], columns = data1[0])
    df2=pd.DataFrame(data = data2[1:], columns = data2[0])
    df1.set_index("Race", inplace = True)
    df2.set_index("Race", inplace = True)
    df1.to_csv(afilename, index = True)
    df2.to_csv(bfilename, index = True)
insight5("Insight5-1.csv","Insight5-2.csv","population.csv")
 

def visualization1(filename):
    data=pd.read_csv(filename)
    #data['Growth']=data["Growth"].astype(int)
    count=0
    col=[]
    for i in data['Growth']:
        col.append(int(i.replace(',',"")))
    data['Growth']=col
    pprint(data)
    plt.plot(data['Year'], data['Growth'], color = 'blue')
    plt.xlabel('Year')
    plt.ylabel('Population Growth')
    plt.title('Population Growth Each Year')
    plt.savefig('visualization1.png')
    plt.show()
#visualization1('Insight1.csv')

 
def visualization2(filename):
    data=pd.read_csv(filename)
    data=data.iloc[5:]
    plt.bar(data['Year'], data['Total Number'], color = 'maroon')
    plt.xlabel('Year')
    plt.ylabel('Total Number of Cases')
    plt.title('Number of Crimes in Each Year')
    plt.savefig('visualization2.png')
    plt.show()
#visualization2('Insight3.csv')


def visualization3(input_file):
    yearly_crimes = insight4(input_file)
    years = []
    for year in yearly_crimes.index:
        total_case_sum = yearly_crimes.loc[year]
        crime_pie = total_case_sum.plot.pie(labels = None, autopct='%1.0f%%',  pctdistance=1.2)
        crime_pie.axis('equal')
        crime_pie.set_title("Crimes Committed in " + str(year) + " Grouped By Severity")
        crime_pie.legend(labels=["Infraction(%)", "Misdemeanor(%)", "Felony(%)"], frameon=True,  bbox_to_anchor=(0.2,0.2))
        plt.show()



#visualization3("Insight4.csv")

