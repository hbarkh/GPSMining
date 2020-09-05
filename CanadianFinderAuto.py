# This script sequentially scans endomondo profiles and stores the userID and country of origin
# https://www.endomondo.com/profile/4585 #the last digits in the url are the userID

import mySQLWriter as sql #this is a file which connects to your local mySQL instance and where I have abstracted some queries for easy calling
import datetime
from bs4 import BeautifulSoup #html parser
import re #string parser
from concurrent.futures import ThreadPoolExecutor #mult-threading
from requests_futures.sessions import FuturesSession #concurrent url sending
from fake_useragent import UserAgent #generating browser headers


def RunCanadianFinder():
    # INSTRUCTIONS
    # determine how many threads your processor has (just google your processor)
    # change max_workers = to the number of threads your processor has
    # change itersize = an integer multiple of your max_workers, the higher the better but <100 suggested. Higher itersize = more RAM required.
    # If the program is interrupted, you will loose the last "itersize" number of URLs, but everything else will be intact
    # Hard code your cookie below in the format it appears

    # CONSTANTS
    # PLEASE HARD CODE YOUR COOKIE HERE in ezcookie
    ezcookie = '_pxvid=1f8aab50-b7f4-11ea-a523-0242ac12000a; _ga=GA1.2.1261756879.1593206975; acceptCookies=1; __gads=ID=b8dc712be355f947:T=1593207011:S=ALNI_MZwdFmfpWZnA5rtkUucJ2LveKGM_g; __utma=162144232.1261756879.1593206975.1597198541.1597198541.1; __utmz=162144232.1597198541.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); INGRESSCOOKIE=1598371152.898.2320.533481; CSRF_TOKEN=79f93se196n8geb2cp4mcd1miv; _pxff_rf=1; _pxff_fp=1; _pxff_bsco=1; EndomondoApplication_AUTO=; USER_TOKEN=67B4A55EECA76CBCF19CBD35A4421E9CGyxz9emgNgmjl32rFl67suaaKam%2FEGCF21g2lQNvIRGqV470AWguMsq9kDB%2F9ppVHRpgkpRwBAh3e%2BnMMmFdJFi0k8SHb8Pb5mGuFpjJk6s%3D; JSESSIONID=67FBA074393587C6AB0020874013AF20; _px3=b6bbdaa847313e28e1d4cb749759c55cbde47fba09827dfe5b82634faaadbd12:LTJUrqqYRmHmeUrXjPoTfuFb+JgPPd2saFnAcv831mT9NLXf0zRH9GTKyL4sgBalcEA7fMswtQ+xPfxvxjvkCw==:1000:znc8EIEnAGCP/tBlU0RywzLXco8uG3ESCSsagmI5OcSMr6CV2opJ1Kdzweagl60+Q4ryahx48ZXomXkm0wEWkZuOklJ0Ja3xUAz9wjY1Bghsohe/eYjmUwC3U75TDuuosSXrKwkTPq/bSCKE4hRCQL5Vuw05yF54sY2SEuF9A2w='
    COOKIE = {'Cookie': ezcookie}
    HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}

    # Tell user where they left off
    sql.mycursor.execute("SELECT userID from CanadianUsers ORDER BY userID DESC LIMIT 1")
    last_id = sql.mycursor.fetchall()[0][0]

    # CONSTANTS
    minID = last_id
    ID_RANGE = 10000
    maxID = minID + ID_RANGE
    ITERSIZE = 80 #80 works well

    #TELL USER PROGRAM STARTING
    print(f"\033[0;34;94mProgram is now starting at userID: {minID}\x1b[0m")

    for x in range(minID, maxID, ITERSIZE):

        #Generate random header
        HEADER['User-Agent'] = UserAgent().random
        #starttime = mytime.time()

        # Create the URLS that we will search for concurrently
        concurrent_urls = []
        for userID in range(x, x + ITERSIZE):
            concurrent_urls.append(f'https://www.endomondo.com/profile/{userID}')

        #Initialize empty lists that will hold our results
        request_contents = []
        request_urls = []

        #Create a browsing session, add the generated headers, create threads
        with FuturesSession(executor= ThreadPoolExecutor(max_workers = 20)) as session:
            session.headers.update(HEADER)
            #concurrently request all of the URLs we prevoiusly made in this iteration
            futures = [session.get(url,cookies = COOKIE,headers=HEADER) for url in concurrent_urls]
            for future in futures:
                request_contents.append(future.result().content) #The returned contents of the page
                request_urls.append(future.result().url) #The URLs associated with the page in case pages come back in a different order than we sent them


        #Initialize list of which countries our users belong to
        countries_list = []

        #Loop through the results by index. Remember, our results are stored in a list. Now we loop through the list by index.
        for index, content in enumerate(request_contents):
            #Initialize our parsing object as soup
            soup = BeautifulSoup(content, 'lxml')

            # GET USERURL
            userurl = request_urls[index]
            userID = int(re.split('profile/', userurl)[1])

            # Check page for error
            innercontent = soup.find('div', class_="innerContent internalErrorPanel")
            #Check if country is private
            if innercontent != None:
                country = 'private'
            #Check if other errors
            else:

                innercontent2 = soup.find('div', {'class': "innerContent accessDeniedPanel"})

                if innercontent2 != None:
                    innercontent2 = innercontent2.find('h1').text

                if innercontent2 == 'Page Not Found':

                    country = innercontent2 #In case its something other than page not found

                else:
                    #If no other errors, then find the text which countains country.
                    country = soup.find('td').text #the first html tag that is 'td' after the page has no errors will be the country

            #Create a list containing tuples of (userID, country)
            #Adding our parsed results to a list allows us to make one query to SQL and write every item in the list instead of doing 1 user at a time.
            countries_list.append((userID, country))

        #Inform user iteration is done
        print("done one iteration")

        #DEBUG PRINT STATEMENTS
        #print(countries_list)
        #print(request_urls)

        #WRITE TO DATABASE
        sql.write_user_country(countries_list) #writes the entire iteration in one pass instead of user by user. Huge speedup.
