# -*- coding: utf-8 -*-
"""
Created on Sat Jul 28 14:25:35 2018

@author: AndrewJPW
"""

import requests
from bs4 import BeautifulSoup

team_code = str(464477) #Get team code
team_page = requests.get("https://www.virtualmanager.com/clubs/" + team_code) #Take page of selected team

team_soup = BeautifulSoup(team_page.content, 'html.parser')
child_list = list(team_soup.children)

#Find all players on the team page
player_list = team_soup.find_all('td',class_='player')
#remove top scorers
player_list = player_list[7:]

player_links = [] #Player URLs
player_names = [] #Player Names

for player in player_list:
    p_data = player.a.attrs['href']
    player_links.append(p_data)
    player_names.append(player.a.get_text())
    
initial_url = 'https://www.virtualmanager.com/'
page_list = [] #Player history pages

#Get the player history pages for each player
for link in player_links:
    nav_url = initial_url + link + '/history'
    player_page = requests.get(nav_url)
    player_soup = BeautifulSoup(player_page.content,'html.parser')
    page_list.append(player_soup)
    
player_stats = []
stat_names = ['Matches','Goals','Assists']

#Get the statistics of the current players
for page in page_list:
    stat_list = [0,0,0]
    team_details = page.find('div',class_='player_history')
    transfer = team_details.find_all('table')
    if(len(transfer) > 1):
        team_hist = transfer[1] #The first transfer is the player's most recent club 
        #Count Matches
        matches = team_hist.find_all('td',class_='matches')
        goals = team_hist.find_all('td',class_='goals')
        assists = team_hist.find_all('td',class_='assists')
        
        match_count = 0
        for m in matches:
            match_count = match_count + int(m.get_text())
        goal_count = 0
        for g in goals:
            goal_count = goal_count + int(g.get_text())
        assist_count = 0
        for a in assists:
            assist_count = assist_count + int(a.get_text())
        
        stat_list = [match_count,goal_count,assist_count]
    player_stats.append(stat_list)
    
squad = []
for p in range(0,len(player_names)):
    playerDetails = player_names[p] + ": PLAYED - " + str(player_stats[p][0]) + ", GOALS - " + str(player_stats[p][1]) + ", ASSISTS - " + str(player_stats[p][2])
    squad.append(playerDetails)

#Write Squad to TXT File and Open it
squadFile = open('squad.txt','w')

for item in squad:
    squadFile.write("%s\n" % item)
    
squadFile.close