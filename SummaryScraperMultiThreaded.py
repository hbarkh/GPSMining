import mySQLWriter as sql
from concurrent.futures import ThreadPoolExecutor
from requests_futures.sessions import FuturesSession
from fake_useragent import UserAgent
import pandas as pd
import requests
from requests import Session



# CONSTANTS

HEADER = {}
COOKIE = {}
DESIRED_UTCOFFSET = '-07:00' # -07:00 from Mar-Nov in Vancouver.

SEARCHING_MONTHS = ['May','June','July','August']
SEARCHING_YEARS = ['2010','2011','2012','2013','2014','2015','2016','2017','2018','2019','2020']
month_year = []

# Initialize

DF_DATEPARAMS = pd.DataFrame(
    columns= SEARCHING_MONTHS,
    index= SEARCHING_YEARS,
    data = [[('2010-06-10T06:59:59.999Z','2010-04-23T07:00:00.000Z'),('2010-07-15T06:59:59.999Z','2010-05-28T07:00:00.000Z'),('2010-08-12T06:59:59.999Z','2010-06-25T07:00:00.000Z'),('2010-09-09T06:59:59.999Z','2010-07-23T07:00:00.000Z')],
            [('2011-06-09T06:59:59.999Z','2011-04-22T07:00:00.000Z'),('2011-07-14T06:59:59.999Z','2011-05-27T07:00:00.000Z'),('2011-08-11T06:59:59.999Z','2011-06-24T07:00:00.000Z'),('2011-09-15T06:59:59.999Z','2011-07-29T07:00:00.000Z')],
            [('2012-06-14T06:59:59.999Z','2012-04-27T07:00:00.000Z'),('2012-07-12T06:59:59.999Z','2012-05-25T07:00:00.000Z'),('2012-08-09T06:59:59.999Z','2012-06-22T07:00:00.000Z'),('2012-09-13T06:59:59.999Z','2012-07-27T07:00:00.000Z')],
            [('2013-06-13T06:59:59.999Z','2013-04-26T07:00:00.000Z'),('2013-07-11T06:59:59.999Z','2013-05-24T07:00:00.000Z'),('2013-08-15T06:59:59.999Z','2013-06-28T07:00:00.000Z'),('2013-09-12T06:59:59.999Z','2013-07-26T07:00:00.000Z')],
            [('2014-06-12T06:59:59.999Z','2014-04-25T07:00:00.000Z'),('2014-07-10T06:59:59.999Z','2014-05-23T07:00:00.000Z'),('2014-08-14T06:59:59.999Z','2014-06-27T07:00:00.000Z'),('2014-09-11T06:59:59.999Z','2014-07-25T07:00:00.000Z')],
            [('2015-06-11T06:59:59.999Z','2015-04-24T07:00:00.000Z'),('2015-07-16T06:59:59.999Z','2015-05-29T07:00:00.000Z'),('2015-08-13T06:59:59.999Z','2015-06-26T07:00:00.000Z'),('2015-09-10T06:59:59.999Z','2015-07-24T07:00:00.000Z')],
            [('2016-06-09T06:59:59.999Z','2016-04-22T07:00:00.000Z'),('2016-07-14T06:59:59.999Z','2016-05-27T07:00:00.000Z'),('2016-08-11T06:59:59.999Z','2016-06-24T07:00:00.000Z'),('2016-09-15T06:59:59.999Z','2016-07-29T07:00:00.000Z')],
            [('2017-06-15T06:59:59.999Z','2017-04-28T07:00:00.000Z'),('2017-07-13T06:59:59.999Z','2017-05-26T07:00:00.000Z'),('2017-08-10T06:59:59.999Z','2017-06-23T07:00:00.000Z'),('2017-09-14T06:59:59.999Z','2017-07-28T07:00:00.000Z')],
            [('2018-06-14T06:59:59.999Z','2018-04-27T07:00:00.000Z'),('2018-07-12T06:59:59.999Z','2018-05-25T07:00:00.000Z'),('2018-08-09T06:59:59.999Z','2018-06-22T07:00:00.000Z'),('2018-09-13T06:59:59.999Z','2018-07-27T07:00:00.000Z')],
            [('2019-06-13T06:59:59.999Z','2019-04-26T07:00:00.000Z'),('2019-07-11T06:59:59.999Z','2019-05-24T07:00:00.000Z'),('2019-08-15T06:59:59.999Z','2019-06-28T07:00:00.000Z'),('2019-09-12T06:59:59.999Z','2019-07-26T07:00:00.000Z')],
            [('2020-06-11T06:59:59.999Z','2020-04-24T07:00:00.000Z'),('2020-07-16T06:59:59.999Z','2020-05-29T07:00:00.000Z'),('2020-08-13T06:59:59.999Z','2020-06-26T07:00:00.000Z'),('2020-09-10T06:59:59.999Z','2020-07-24T07:00:00.000Z')]])

for year in SEARCHING_YEARS:
    for month in SEARCHING_MONTHS:
        month_year.append((month,year))


# Helper function
def summaryparser(workoutsummary):

    workoutIDs_intimezone =[]

    if workoutsummary and ("local_start_time" in workoutsummary[0]): #if summary is not blank and ...
        UTCoffset = workoutsummary[0]["local_start_time"][-6:]
        if UTCoffset == DESIRED_UTCOFFSET: #if first workout is in Pacific Time Zone during summer months
            for workout in range(0,len(workoutsummary)): #check every workout for PST during summer months
                UTCoffset = workoutsummary[workout]["local_start_time"][-6:]
                if UTCoffset == DESIRED_UTCOFFSET:
                    workoutIDs_intimezone.append(workoutsummary[workout]["id"]) #append workoutIDs matching our criteria
        else:
            workoutIDs = False

    return workoutIDs_intimezone



#Main function
def ParseSummariesOfUser(passed_userID):

    #Assign local variable
    userID = passed_userID

    # Generate random header
    HEADER['User-Agent'] = UserAgent().random

    #Prepare the requests that we will search for concurrently
    concurrent_requests = []

    for year in SEARCHING_YEARS:
        for month in SEARCHING_MONTHS:
            before = DF_DATEPARAMS.loc[year][month][0]
            after = DF_DATEPARAMS.loc[year][month][1]

            payload = {'before': before, 'after': after}

            therequest = requests.Request('GET',f'https://www.endomondo.com/rest/v1/users/{userID}/workouts',params=payload,headers=HEADER)
            prepared_request = Session().prepare_request(therequest)
            concurrent_requests.append(prepared_request)


    #Retrieve the requests
    request_contents = []

    #start = mytime.time()
    with FuturesSession(executor=ThreadPoolExecutor(max_workers=8)) as session:
        session.headers.update(HEADER)
        futures = [session.send(prepared_request) for prepared_request in concurrent_requests]
        for future in futures:
            request_contents.append(future.json()) #preserves original order

    #end = mytime.time()
    #print(f'took: {(end-start)/40} per URL')


    # Parse & Write
    last_month = []

    for index,workoutsummary in enumerate(request_contents):
        month = month_year[index][0]
        year = month_year[index][1]

        #Determine PST workouts
        workouts_in_timezone = summaryparser(workoutsummary)

        #Remove duplicates from new month (all duplicates will belong to last month)
        for x in workouts_in_timezone:
            for z in last_month:
                if x == z:
                    workouts_in_timezone.remove(x)
                    print("removed duplicate:",x)


        #Write workouts
        sql.writesummary(userID, month, year, workoutsummary)
        if workouts_in_timezone: #if its not empty, write to PSTWorkouts
            sql.writePST(userID, month, year, workouts_in_timezone)
            print('\x1b[0;32;32m','PST:',workouts_in_timezone,'\x1b[0m')

        #Re-assign last month
        last_month = workouts_in_timezone

    #mark as parsed
    sql.parsed_canadian(userID)




#CALLING THE FUNCTION

#List of users to parse
canadians_list = sql.canadians_to_parse()

print(len(canadians_list),'users to parse summaries for')


for userID in canadians_list:
    print(userID[0])
    ParseSummariesOfUser(userID[0])
