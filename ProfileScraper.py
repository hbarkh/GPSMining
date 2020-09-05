import mySQLWriter as sql
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor
from requests_futures.sessions import FuturesSession
from requests import get


#Set the initial params cookie
ezcookie = '_pxvid=1f8aab50-b7f4-11ea-a523-0242ac12000a; _ga=GA1.2.1261756879.1593206975; acceptCookies=1; __gads=ID=b8dc712be355f947:T=1593207011:S=ALNI_MZwdFmfpWZnA5rtkUucJ2LveKGM_g; __utma=162144232.1261756879.1593206975.1597198541.1597198541.1; __utmz=162144232.1597198541.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); INGRESSCOOKIE=1598371152.898.2320.533481; CSRF_TOKEN=79f93se196n8geb2cp4mcd1miv; _pxff_rf=1; _pxff_fp=1; _pxff_bsco=1; EndomondoApplication_AUTO=; USER_TOKEN=67B4A55EECA76CBCF19CBD35A4421E9CGyxz9emgNgmjl32rFl67suaaKam%2FEGCF21g2lQNvIRGqV470AWguMsq9kDB%2F9ppVHRpgkpRwBAh3e%2BnMMmFdJFi0k8SHb8Pb5mGuFpjJk6s%3D; JSESSIONID=67FBA074393587C6AB0020874013AF20; _px3=b6bbdaa847313e28e1d4cb749759c55cbde47fba09827dfe5b82634faaadbd12:LTJUrqqYRmHmeUrXjPoTfuFb+JgPPd2saFnAcv831mT9NLXf0zRH9GTKyL4sgBalcEA7fMswtQ+xPfxvxjvkCw==:1000:znc8EIEnAGCP/tBlU0RywzLXco8uG3ESCSsagmI5OcSMr6CV2opJ1Kdzweagl60+Q4ryahx48ZXomXkm0wEWkZuOklJ0Ja3xUAz9wjY1Bghsohe/eYjmUwC3U75TDuuosSXrKwkTPq/bSCKE4hRCQL5Vuw05yF54sY2SEuF9A2w='
COOKIE = {'Cookie': ezcookie}
HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
HEADER['User-Agent'] = UserAgent().random



#DEFINE PARSER FUNCTION
def parse_profile_helper(userID,content):

    #set local variable
    userID = userID

    #Initialize Nulls
    Sex, Birthday, Height, Weight, FavouriteSport = [None,None,None,None,None]
    #Sex is always not null, set it to false, if it is not changed from false to something else then program will break

    #get the xml page
    soup = BeautifulSoup(content,'lxml')
    #check the frame to see if error
    innercontent = soup.find('div', class_="innerContent internalErrorPanel")

    if innercontent is not None:
        print("Inner content had internalErrorPanel, program quit.")
        quit()
    else:
        pass

    #get all labels and data
    field_labels = soup.findAll('th')
    field_datas = soup.findAll('td')

    #to match them exactly since not every user will have the same number of fields
    for index in range(1,len(field_labels)): #range starts at 1 to avoid country, which is always the first label, which we already have
        # -1 removes colon at the end
        field_label = field_labels[index].text[:-1]
        field_data = field_datas[index].text

        #print(field_label)
        #print(field_data)
        if field_label == 'Sex': #ordered in the way they appear on page to stop the if search as soon as possible, except weight which comes before height but is more rare than height
            Sex = field_data
        elif field_label == 'Birthday':
            Birthday = field_data
        elif field_label == 'Height':
            Height = field_data
        elif field_label == 'Weight':
            Weight = field_data
        elif field_label == 'Favorite Sport':
            FavouriteSport = field_data
        else:
            print("A field was found other than sex,birthday,height,weight,favourite sport.")
            print(f"The field is {field_label}: {field_data}")


    #write and execute that field and its data
    q = f"UPDATE workout_database.CanadianUsers SET Birthday = %s, Sex = %s, Height = %s, Weight = %s, FavouriteSport = %s, profileparsed = 1 WHERE userID = %s"
    sql.mycursor.execute(q,(Birthday,Sex,Height,Weight,FavouriteSport,userID,))
    sql.db.commit()
    print(f"done {userID}")

#CALL THIS FUNCTION AND IT WILL DO THE REST
def parse_profiles():

    #count unparsed
    sql.mycursor.execute("SELECT count(*) FROM workout_database.canadianusers WHERE country = 'Canada' and profileparsed = 0;")
    unparsed_canadians = sql.mycursor.fetchall()[0][0]
    #ask user for how many iterations
    print(f"There are {unparsed_canadians} canadians with their profiles not parsed")
    iterations = int(round(unparsed_canadians/40,0))
    print(f"Doing {iterations} iterations of 40")

    #start
    for iter in range(0,iterations):
        sql.mycursor.execute("SELECT userID from CanadianUsers WHERE country = 'Canada' AND profileparsed = 0 LIMIT 40")
        users_to_parse = sql.mycursor.fetchall()
        #print(users_to_parse)
        concurrent_urls = []

        for user in users_to_parse:

            userID = user[0]
            concurrent_urls.append(f'https://www.endomondo.com/profile/{userID}')

        request_contents = []
        request_urls = []

        #print(concurrent_urls)
        with FuturesSession(executor=ThreadPoolExecutor(max_workers=20)) as session:
            session.headers.update(HEADER)
            futures = [session.get(url, cookies=COOKIE, headers=HEADER) for url in concurrent_urls]
            for future in futures:
                request_contents.append(future.result().content)
                request_urls.append(future.result().url)


        for index, content in enumerate(request_contents):
            #to make sure we are matching the right user and their content
            #retrieve their userID from the URL we got back instead of what we passed forward

            userID = request_urls[index].split('/')[-1]
            content = request_contents[index]
            parse_profile_helper(userID,content)
            #print(content)


#calling function
def parse_single_profiles():
    sql.mycursor.execute("SELECT userID FROM workout_database.canadianusers WHERE country = 'Canada' and profileparsed = 0;")
    users_to_parse = sql.mycursor.fetchall()

    for user in users_to_parse:
        userID = user[0]
        url = f'https://www.endomondo.com/profile/{userID}'
        content = get(url, cookies=COOKIE, headers=HEADER).content
        print(content)
        parse_profile_helper(userID,content)


#Call singles or multi-threaded version of program
#parse_single_profiles()
parse_profiles()