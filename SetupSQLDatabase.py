import mysql.connector

#INSTRUCTINS:
#0. Setup mysql workbench on windows or mac, create a new schema and write down your host, user, and password into this script the TWO times it appears. Lines ~11-21 and ~24-35
#1. First Time, uncomment all of the code and hit run (it should be uncommented already)
#2. subsequent times, comment out all code except the one sandwiched by #KEEP ME#

dbpass = str(input("Type in the password you used to install your MySQL Database:") or '8GTf!Rmf1fAC') #write your password here if you dont mind storing it plaintext


db = mysql.connector.connect(

    host = "localhost",
    user = "root",
    passwd = dbpass
)

mycursor = db.cursor()
mycursor.execute("CREATE DATABASE Workout_Database")



#KEEP ME#
#never comment this code out, it is simply a connection to ur DB.

db = mysql.connector.connect(

    host = "localhost",
    user = "root",
    passwd = dbpass,
    database = "Workout_Database"
)

mycursor = db.cursor()

#KEEP ME#
# Create the table
mycursor.execute("CREATE TABLE WorkoutSummaries (ws_key bigint UNSIGNED NOT NULL PRIMARY KEY  AUTO_INCREMENT, userID int UNSIGNED, month ENUM('May','June','July','August'), year ENUM('2015','2016','2017','2018','2019','2020'), workoutsummaryJSON JSON)")
mycursor.execute("CREATE TABLE PSTWorkouts (pst_key bigint UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT, userID int UNSIGNED, month ENUM('May','June','July','August'), year ENUM('2015','2016','2017','2018','2019','2020'), workoutID bigint UNSIGNED NOT NULL)")
mycursor.execute("CREATE TABLE VancouverGPS (gps_key bigint UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT, userID int UNSIGNED, month ENUM('May','June','July','August'), year ENUM('2015','2016','2017','2018','2019','2020'),workoutID bigint UNSIGNED NOT NULL, timestamp TIMESTAMP, latitude DECIMAL(15,11), longitude DECIMAL(15,11), altitude DECIMAL (15,10), distance DECIMAL(15,10),speed DECIMAL(15,10),duration DECIMAL(25,12) UNSIGNED, heartrate TINYINT UNSIGNED)") #todo: determine all columns we want from workout data
mycursor.execute("CREATE TABLE CanadianUsers (cad_key int UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT, userID int UNSIGNED, country VARCHAR(50) DEFAULT NULL)")


# ALTERING TABLE to add a few columns
mycursor.execute("ALTER TABLE VancouverGPS ADD COLUMN elevated_link tinyint UNSIGNED DEFAULT NULL")
mycursor.execute("ALTER TABLE VancouverGPS ADD COLUMN sport tinyint UNSIGNED DEFAULT NULL")
mycursor.execute("ALTER TABLE VancouverGPS ADD COLUMN cadence smallint UNSIGNED DEFAULT NULL")
mycursor.execute("ALTER TABLE PSTWorkouts ADD COLUMN detailsparsed BOOL DEFAULT '0'")
mycursor.execute("ALTER TABLE PSTWorkouts ADD COLUMN workoutJSON JSON DEFAULT NULL")


mycursor.execute("UPDATE PSTWorkouts SET detailsparsed = 0")

#June 27 2020: After expanding search from 2015 to 2010, add ENUMs
mycursor.execute("ALTER TABLE WorkoutSummaries MODIFY COLUMN year ENUM('2010','2011','2012','2013','2014','2015','2016','2017','2018','2019','2020')")
mycursor.execute("ALTER TABLE PSTWorkouts MODIFY COLUMN year ENUM('2010','2011','2012','2013','2014','2015','2016','2017','2018','2019','2020')")
mycursor.execute("ALTER TABLE VancouverGPS MODIFY COLUMN year ENUM('2010','2011','2012','2013','2014','2015','2016','2017','2018','2019','2020')")


# July 31 2020: Add Birthday, Sex, height, Favourite Sport column for Fajars paper
mycursor.execute("ALTER TABLE CanadianUsers ADD COLUMN Birthday VARCHAR(13) DEFAULT NULL") # Need 12 characters, made it 13 to be safe ex. Aug 15, 1969
mycursor.execute("ALTER TABLE CanadianUsers ADD COLUMN Sex VARCHAR(7) DEFAULT NULL") # ex. Male/Female have not seen other options
mycursor.execute("ALTER TABLE CanadianUsers ADD COLUMN Height VARCHAR(10) DEFAULT NULL") # ex 173 cm or 5' 6", can also have decimals 173.4 cm
mycursor.execute("ALTER TABLE CanadianUsers ADD COLUMN FavouriteSport VARCHAR(25) DEFAULT NULL") # longest one is "Skiing cross country"
mycursor.execute("ALTER TABLE CanadianUsers ADD COLUMN ProfileParsed BOOL DEFAULT 0") # determine which rows to parse

# August 5 2020: Discovered a user has weight! Added weight column
mycursor.execute("ALTER TABLE CanadianUsers ADD COLUMN Weight VARCHAR(9) DEFAULT NULL") # ex. 89 kg



#KEEP ME#
db.commit()
#KEEP ME#