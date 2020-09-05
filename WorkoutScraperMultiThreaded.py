import json
import mySQLWriter as sql
from datetime import datetime
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor
from requests_futures.sessions import FuturesSession


# '\x1b[2;32m' regular green
# '\x1b[1;95m' bold pink

'''
#objective
#1. parse through the PST workouts table - done
#2. call the endomondo server and retrieve workout - done
#3. write the json to the table - done
#4. parse workout - x,y,z,speed,heart rate,timestamp - done
#5. save fields to vancouvergps table - done
#6. write to pst table that the workout was parsed (new column needs to be added) - done
#7. later parse through vancouver gps and tick off whether it is in our desired locations (seperate program is best)
'''
#todo: remove month, year
def detailparser_helper(userID,month,year,workoutID,workoutjson):
    # this function unloads JSONS and returns a list of tuples to write to VancouverGPS
    # a different function then writes this output to the DB
    list_of_tuples =[]
    point_timestamp, latitude, longitude, altitude, distance, speed, duration, heart_rate,elevated_link, cadence, sport = [None, None, None, None, None,None, None, None, None, None, None]

    workoutjson = json.loads(workoutjson)
    #print(workoutjson)

    if "sport" in workoutjson:
        sport = workoutjson["sport"]
    if ("points" in workoutjson) and ("points" in workoutjson["points"]): #there are two sets of "points" keys that need to exist
        pointssumarry = workoutjson["points"]

        pointslist = pointssumarry["points"]
        for point in pointslist:
            # removes keys, but also checks that item exists (not all points contain the same sensor data)
            # returns a list of tuples which sql can write in one statement instead of looping
            if "time" in point:
                point_timestamp = point["time"]
                #convert str to timestr
                point_timestamp = datetime.strptime(point_timestamp, '%Y-%m-%dT%H:%M:%S.%f%z')
            if "speed" in point:
                speed = point["speed"]
            if "altitude" in point:
                altitude = point["altitude"]
            if "distance" in point:
                distance = point["distance"]
            if "duration" in point:
                duration = point["duration"]
            if "latitude" in point:
                latitude = point["latitude"]
            if "longitude" in point:
                longitude = point["longitude"]
            if "sensor_data" in point:
                sensor_data = point["sensor_data"]
                if "heart_rate" in sensor_data:
                    heart_rate = sensor_data["heart_rate"]
                if "cadence" in sensor_data:
                    cadence = sensor_data["cadence"]
            # todo: remove month and year here
            list_of_tuples.append((userID,month,year,workoutID,point_timestamp,latitude,longitude,altitude,distance,speed,duration,heart_rate, elevated_link,cadence,sport))

        return list_of_tuples



def getworkoutdetails(PST_rows):

    HEADER = {'User-Agent':UserAgent().random}
    concurrent_urls = []
    concurrent_rows = []
    # Create concurrent URLs
    for row in PST_rows:
        pst_key,userID,workoutID = row
        url = f'https://www.endomondo.com/rest/v1/users/{userID}/workouts/{workoutID}'
        concurrent_urls.append(url)


    #starttime = mytime.time()
    request_contents = []
    with FuturesSession(executor=ThreadPoolExecutor(max_workers=4)) as session:
        session.headers.update(HEADER)
        futures = [session.get(url, headers=HEADER) for url in concurrent_urls]
        for future in futures:
            request_contents.append(future.result().content) #returns in original order
    #endtime = mytime.time()
    for index, item in enumerate(request_contents):
        workoutjson = item
        pst_key = PST_rows[index][0]
        sql.mycursor.execute("UPDATE PSTWorkouts SET workoutJSON = %s WHERE pst_key = %s ", (workoutjson, pst_key))
        sql.db.commit()
        print(f'Stored {PST_rows[index][2]} in PSTWorkouts')
    #print(f"It took {(endtime-starttime)/len(PST_rows)} seconds per workout for {len(PST_rows)} workouts")


def parse_everything():
    failed_writes = []
    # This takes every workout from PSTWorkouts DB where details parsed = False then parses it
    # It  writes the parsed data columns to VancouverGPS DB
    # It updates detailes parsed = True once it has parsed the workout
    # Limited to 100 workouts at a time in case someones computer is slow
    # Just re run the script and it will do the next 100 which have not been parsed

    sql.mycursor.execute("SELECT * FROM PSTWorkouts WHERE detailsparsed = '0' and workoutJSON IS NOT NULL LIMIT 1000") #limited to not explode, use an outer loop to iterate
    parsed_pst_keys = []
    meta_list_of_tuples = []
    for x in sql.mycursor:
        pst_key,userID,month,year,workoutID,detailsparsed,workoutjson = x #month and year are throwaway, we will go by timestamp that each point has
        #calls the helper function to parse it
        list_of_tuples = detailparser_helper(userID,month,year,workoutID,workoutjson) # todo: remove month,year
        # append to list of all the things to write to DB
        parsed_pst_keys.append(pst_key)
        meta_list_of_tuples.append(list_of_tuples)
        #print(f"Parsed Workout {workoutID} into line by line points")


    for list_of_tuples in meta_list_of_tuples:

        try: #todo: remove month and year here
            sql.mycursor.executemany("INSERT INTO VancouverGPS (userID,month,year,workoutID,timestamp,latitude,longitude,altitude,distance,speed,duration,heartrate,elevated_link,cadence,sport) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",list_of_tuples)
            sql.db.commit()
            #last item in the list may be blank
            if list_of_tuples != None: #moderately ghetto, if a list was fully null, it was also written but I cannot print it out properly
                print(f'successfully wrote workout {list_of_tuples[0][3]} into VancouverGPS')
        except:
            failed_writes.append(f"\x1b[1;30;4mcould not write {list_of_tuples[0][3]}\x1b[0m")

    for pst_key in parsed_pst_keys:
        sql.mycursor.execute("UPDATE PSTWorkouts SET detailsparsed = %s WHERE pst_key = %s ", (True, pst_key))
        sql.db.commit()
    #todo: this is sligthly unsafe, if list of tuples stops writing halfway and quits, then the database will not update the keys which were parsed
    # cant update VancouverGPS and detailsparsed (PSTWorkouts) in one loop.
    print(failed_writes)

def warn_duplicates():
    #this function is called when warning needed
    print("\x1b[1;30;41mSTOP!\x1b[0m")
    print("ENSURE YOU HAVE RAN REMOVE DUPLICATE WORKOUTS.SQL TO REMOVE DUPLICATE WORKOUTID's BEFORE RETRIEVING DETAILS")
    print("\x1b[1;30;41mSTOP!\x1b[0m")

    removed_duplicates = input("Have you removed duplicates?(yes/no): ") or False

    if removed_duplicates != 'yes':
        print("Please remove duplicates then re-run. Program quitting")
        quit()



# MAIN FUNCTIONS
def retrieve_workout_details(iterations_of_40):

    #remove the duplicates
    sql.removePSTduplicates()
    #Warn the user to remove duplicates
    warn_duplicates()

    for x in range(iterations_of_40):
        print(f"Starting iteration {x}")
        PSTWorkoutsToRetrieve = sql.getPSTWorkoutIDs() #Gets bundles of 40 to prevent overworking server
        print(PSTWorkoutsToRetrieve)
        getworkoutdetails(PSTWorkoutsToRetrieve) #throttled to four threads


def parse_workout_details(iterations_of_1000):

    #Warn the user to remove duplicates
    warn_duplicates()

    for x in range(iterations_of_1000):
        print(f"Parsing iteration {x}")
        #run the parser
        #starttime = mytime.time()
        parse_everything()
        #endtime = mytime.time()

        #print(f'time to parse out workouts after they have been retrieved {(endtime - starttime) / 382} seconds per workout')


# Call the main functions from python console
retrieve_workout_details(50)
parse_workout_details(1)
