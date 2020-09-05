import mysql.connector
from datetime import datetime
import json


# CONNECT TO DATABASE
db = mysql.connector.connect(

    host = "localhost",
    user = "root",
    passwd = "8GTf!Rmf1fAC", #input your database password here
    database = "Workout_Database"
)

mycursor = db.cursor()

#Tell version
print("Imported August 19th 2020 version of mysql writer")
#FUNCTIONS

def writesummary(userID,month,year,workoutsummary):
    #this should check for duplicates in a revised version. But ultimately, in the final parsed version of the workout details, duplicates can be easily scanned and deleted.
    mycursor.execute("INSERT INTO WorkoutSummaries (userID, month, year, workoutsummaryjson) VALUES (%s,%s,%s,%s)",(userID,month,year,json.dumps(workoutsummary)))
    db.commit()

def writesummaries(summary_list):
    #this should check for duplicates in a revised version. But ultimately, in the final parsed version of the workout details, duplicates can be easily scanned and deleted.
    mycursor.executemany("INSERT INTO WorkoutSummaries (userID, month, year, workoutsummaryjson) VALUES (%s,%s,%s,%s)",summary_list)
    db.commit()


def writePST(userID,month,year,workoutIDs):

    for workoutID in workoutIDs:
        mycursor.execute("INSERT INTO PSTWorkouts (userID, month, year, workoutID) VALUES (%s,%s,%s,%s)",(userID,month,year,workoutID))
        db.commit()

def getPSTWorkoutIDs():
    mycursor.execute("SELECT pst_key,userID,workoutID FROM PSTWorkouts WHERE workoutJSON IS NULL LIMIT 40") #return first row that hasn't been checked
    return mycursor.fetchall() # list of tuples containing key,userid,workoutid

def write_elevated_links():

    #define this later to identify if points in our DB are within our desired location lat/long
    pass


def canadians_to_parse():
    mycursor.execute("SELECT userID from CanadianUsers WHERE country = 'Canada' and summariesparsed = 0")
    return mycursor.fetchall()

def parsed_canadian(userID):
    mycursor.execute("UPDATE CanadianUsers SET summariesparsed = 1 WHERE userID = %s",(userID,))


def write_user_country(country_list):
    mycursor.executemany("INSERT INTO CanadianUsers (userID, country) VALUES (%s,%s)",country_list)
    db.commit()


#Remove Duplicates
def removePSTduplicates():

    #Get a list of duplicates
    #store to list
    #loop through and drop first instance of the duplicate
    query_duplicates = "SELECT workoutID FROM Workout_Database.PSTWorkouts GROUP BY workoutID HAVING COUNT(workoutID) > 1;"
    mycursor.execute(query_duplicates)
    duplicateworkouts = mycursor.fetchall()

    print(f"duplicates to remove:{duplicateworkouts}")
    for workout in duplicateworkouts:
        q = f"DELETE FROM workout_database.pstworkouts WHERE workoutID = {workout[0]} LIMIT 1;"
        mycursor.execute(q)
        db.commit()
        print(f"removed one instance of {workout[0]}")
    mycursor.execute(query_duplicates)
    duplicateworkouts = mycursor.fetchall()
    print(f"duplicates to remove:{duplicateworkouts}")
    print("If this is not blank, run the removePSTduplicates() again")

    

# PRINTER FUNCTION
def printdatabase(db_name):
    if db_name == 'WorkoutSummaries':
        mycursor.execute("SELECT * FROM WorkoutSummaries")
        for x in mycursor:
            print(x)
    elif db_name == 'PSTWorkouts':
        mycursor.execute("SELECT * FROM PSTWorkouts")
        for x in mycursor:
            print(x)
    elif db_name == 'VancouverGPS':
        mycursor.execute("SELECT * FROM VancouverGPS")
        for x in mycursor:
            print(x)
    else:
        print("blank or incorrect db name given, nothing to print")
