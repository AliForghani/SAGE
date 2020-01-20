# SAGE
## A web scraping tool to get the number of orbital launches from Wikipedia
### Source:
'Orbital launches' table in Wikipedia Orbital Launches:
[Wikipedia Orbital Launches](https://en.wikipedia.org/wiki/2019_in_spaceflight#Orbital_launches)

### Objective:
We need a tool to find the number of orbital launches in the source above, if at least one of its
payloads is reported as 'Successful', 'Operational', or 'En Route'. For each launch, listed by date,
the first line is the launch vehicle and any lines below it correspond to the payloads, of which
there could be more than one.
Please refer to the "SAGE Project - Web Scraping Assignment.pdf" for more details.


### Python solution
Herein, we describe the use of Python packages, requests, beautifulsoup, Pandas and Numpy for this project.

#### Packages import:

```python
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as soup

```

#### Making a BeautifulSoup object from the desired url

```python
url='https://en.wikipedia.org/wiki/2019_in_spaceflight#Orbital_launches'
urlTexts = requests.get(url).text
urlSoup=soup(urlTexts, 'lxml')
```

#### Selecting Orbital launches' table and its records
Inspecting the url (with a browser) shows that there are two main tables with tags containing a class of "wikitable collapsible".
The first table is our desired table "Orbital launches" and the second table is "Suborbital flights".

```python
MainTables=urlSoup.findAll("table", {"class":"wikitable collapsible"})
OrbitalTable=MainTables[0]
OrbitalTable_Lines=OrbitalTable.findAll("tr")
```

#### Identifying the records containing date info versus payloads
Inspecting the table lines shows that we can categorize the lines based on the number of "td" tags in each line. The lines with 5 td
are actually the first record of each date launches (alco containing the actual date), and the records with 6 td contain payloads info.

```python
td_Nos=np.empty(len(OrbitalTable_Lines),dtype=int)
for lineId, line in enumerate(OrbitalTable_Lines):
    td_Nos[lineId] = len(line.findAll("td"))

#here, we identify the line indices of the fist record of each date launches
FirstRecords_Index = np.where(td_Nos == 5)[0]

```


#### Making a dictionary for dates and their outcomes

```python
def GetDateData(Index):
    Dateline = OrbitalTable_Lines[Index]
    DataNoInThisLine=Dateline.findAll("td")
    Actualdate=DataNoInThisLine[0].span.text
    Actualdate = Actualdate.split("[")[0]
    return Actualdate

Date_Outcome={}
for i in range(len(FirstRecords_Index)):
    StartIndex=FirstRecords_Index[i]
    if i!=len(FirstRecords_Index)-1:
        EndIndex=FirstRecords_Index[i+1]
    else:
        EndIndex=len(td_Nos)

    Actualdate=GetDateData(StartIndex)
    ThisDateOutcomes=[]
    for j in range(EndIndex-StartIndex-1):
        td_No = OrbitalTable_Lines[StartIndex+j+1].findAll("td")
        if len(td_No)==6:
            ThisDateOutcomes.append( td_No[5].text.strip())
    Date_Outcome[Actualdate]=ThisDateOutcomes
```


#### Finally make a table for results for all days of the year

```python
MonthDurDict={"January":31, "February":28, "March":31, "April":30, "May":31, "June":30, "July":31, "August":31, "September":30, "October":31, "November":30, "December":31 }
FinalSummary=[]
for month , monthDays in MonthDurDict.items():
    for dayNo in range(1,monthDays+1):
        This_Day=str(dayNo)+" "+ month
        if This_Day in Date_Outcome:
            ThisDateValue=0
            ThisKeyStatuss=Date_Outcome[This_Day]
            for status in ThisKeyStatuss:
                if status in ['Successful', 'Operational', 'En Route']:
                    ThisDateValue=ThisDateValue+1

            # pd.Series(ThisKeyStatuss).isin(['Successful', 'Operational', 'En Route']).any()
            FinalSummary.append([This_Day, ThisDateValue])
        else:
            FinalSummary.append([This_Day,0])

FinalSummaryDF=pd.DataFrame(FinalSummary, columns=["Date", "Value"])
FinalSummaryDF.to_csv("SAGE_Results.csv", index=False)
```




