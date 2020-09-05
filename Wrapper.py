import CanadianFinderAuto
import MouseMover_Windows
from winsound import Beep
#import ProfileScrape

runs = 0
while runs < 12:
    try:
        CanadianFinderAuto.RunCanadianFinder()
        #ProfileScraper.parse_profiles()
        runs+=1
    except:
        Beep(440,400)
        print("The mouse is being moved")
        MouseMover_Windows.move_my_mouse()
        


#CanadianFinderAuto.Ru
# nCanadianFinder()