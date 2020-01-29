import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as soup

def GetActualDate(Index):
    Dateline = OrbitalTable_Lines[Index]
    DataNoInThisLine=Dateline.findAll("td")
    Actualdate=DataNoInThisLine[0].span.text
    Actualdate = Actualdate.split("[")[0]
    return Actualdate


#Making a BeautifulSoup object from the desired url
url='https://en.wikipedia.org/wiki/2019_in_spaceflight#Orbital_launches'
urlTexts = requests.get(url).text
urlSoup=soup(urlTexts, 'lxml')

#Selecting Orbital launches' table and its records
MainTables=urlSoup.findAll("table", {"class":"wikitable collapsible"})
OrbitalTable=MainTables[0]
OrbitalTable_Lines=OrbitalTable.findAll("tr")

#identifying the records containing date string
#####first record the td number of all lines
td_Nos=np.empty(len(OrbitalTable_Lines),dtype=int)
for lineId, line in enumerate(OrbitalTable_Lines):
    td_Nos[lineId] = len(line.findAll("td"))

#Then identify the line indices of the records with td number=5 (the records containing date string)
FirstRecords_Index = np.where(td_Nos == 5)[0]

#first make a table for launch dates and their outcome status (accepted or not)
LaunchesSummmary=[]
for i in range(len(FirstRecords_Index)):
    OutcomeStatus="Rejected" #by default we assume the status is "Rejected"
    StartIndex=FirstRecords_Index[i]
    Actualdate=GetActualDate(StartIndex)

    if i != len(FirstRecords_Index) - 1:
        EndIndex = FirstRecords_Index[i + 1]
    else:
        EndIndex = len(td_Nos)
    for j in range(EndIndex - StartIndex - 1):
        td_No = OrbitalTable_Lines[StartIndex + j + 1].findAll("td")
        if len(td_No) == 6:
            Outcome=td_No[5].text.strip()
            if Outcome in ['Successful', 'Operational', 'En Route']:
                OutcomeStatus="Accepted"
                break

    LaunchesSummmary.append([Actualdate, OutcomeStatus])
LaunchesSummaryDF=pd.DataFrame(LaunchesSummmary, columns=[ "Date", "OutcomeStatus"])

#select the launches with "Accepted" status
AcceptedLaunchesDF=LaunchesSummaryDF[LaunchesSummaryDF["OutcomeStatus"]=="Accepted"]

#make a pandas groupby for launch dates, so we can easily count the total number of accepted launches for each date
DatesLaunchCount=AcceptedLaunchesDF.groupby("Date").size()

#convert the groupby series to a dictionary, in which keys are the dates values are the number of accepted launches.
DatesLaunchCount_Dict=DatesLaunchCount.to_dict()


#Finally make a table for results for all days of the year
MonthDurDict={"January":31, "February":28, "March":31, "April":30, "May":31, "June":30, "July":31, "August":31, "September":30, "October":31, "November":30, "December":31 }
FinalSummary=[]
for month , monthDays in MonthDurDict.items():
    for dayNo in range(1,monthDays+1):
        This_Day=str(dayNo)+" "+ month
        if This_Day in DatesLaunchCount_Dict:
            FinalSummary.append([This_Day, DatesLaunchCount_Dict[This_Day]])
        else:
            FinalSummary.append([This_Day,0])

FinalSummaryDF=pd.DataFrame(FinalSummary, columns=["Date", "Value"])
FinalSummaryDF.to_csv("../output/SAGE_Results.csv", index=False)

