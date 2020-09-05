#This program assists in solving the captcha by moving your mouse to a plugin which solves the captcha
#The chrome plugin is called Buster: Captcha for humans
#The chrome plugin once activated requests an accessible captcha (audio)
#The audio is sent to a speech to text engine and returns the solved captcha

#This mousemover program gets called when "Wrapper.py" detects that we have hit a captcha.

#VERY IMPORTANT:
# You MUST adjust the coordinates your mouse moves to depending on your screen
# After initializing mouse = Controller() then use mouse.position to get the position of your mouse
# Place your mouse where your refresh button is, then call mouse.position and voila, you have your X,Y
# Plug in your X,Y into the correct location for refresh
# Plug in your X,Y into the correct location for Buster: Captcha for humans
# Plug in your X,Y into the correct position for Buster: Captcha for humans's second button

import time as mytime
import numpy as np
from pynput.mouse import Button, Controller

def move_my_mouse():
    #Waits 0-2seconds before activating script to give user time to know the mouse will be moved.
    #You can increase the wait time if your internet is slow
    randomwait = np.random.uniform(0,2)
    #initialize mouse
    mouse = Controller()
    mouse.position
    #Refresh page
    x = 89 #REFRESH BUTTON LOCATION X
    y = 66 #REFRESH BUTTON LOCATION Y
    mouse.position = (x, y)
    mouse.click(Button.left,1) #click
    mytime.sleep(0.003) #micro pause
    mouse.release(Button.left) #release click
    mytime.sleep(2.5 + randomwait) #wait for page to re-load
    #move to a random location on page
    #click to start captcha
    x = 98-x+np.random.uniform(0,90) #CAPTCHA LOCATION X MINUS REFRESH LOCATION X PLUS RANDOM MOVEMENT
    y = 266-y+np.random.uniform(0,30) #CAPTCHA LOCATION Y MINUS REFRESH LOCATION Y PLUS RANDOM MOVEMENT
    mouse.move(x,y)
    x,y = mouse.position
    mouse.click(Button.left,1)
    mytime.sleep(0.01)
    mouse.release(Button.left)
    mytime.sleep(2.5+randomwait)
    #move to solver
    x = 244 - x # SOLVER LOCATION X MINUS CAPTCHA LOCATION X
    y = 638 - y # SOLVER LOCATION Y MINUS CAPTCHA LOCATION Y
    mouse.move(x,y)
    mytime.sleep(1.5+randomwait)
    mouse.click(Button.left,1)
    mytime.sleep(0.01)
    mouse.release(Button.left)
    #wait for page to reload
    mytime.sleep(7+randomwait)
