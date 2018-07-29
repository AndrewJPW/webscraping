# -*- coding: utf-8 -*-
"""
Created on Sun Jul 29 09:53:19 2018

@author: AndrewJPW
"""
#------------------------------------------------------------------------------
import requests
from bs4 import BeautifulSoup

team_code = str(464477)
team_name = 'Phantom Phoenixes'
url_name = 'https://www.virtualmanager.com/'
team_page = requests.get(url_name + "clubs/" + team_code)

team_soup = BeautifulSoup(team_page.content, 'html.parser')

player_list = team_soup.find_all('td',class_='player')

#------------------------------------------------------------------------------
#----------Team Stats----------

#Final Position , Goals For Goals Against
final_pos = ''
goals_for = 0
goals_against = 0
div_ref = team_soup.find('div',class_='league')
league_ref = div_ref.a.attrs['href']
league_page = requests.get(url_name + league_ref)
league_soup = BeautifulSoup(league_page.content, 'html.parser')

table_soup = league_soup.find('div',class_='league')
position_soup = list(table_soup.find_all('tr'))

pos_ctr = 1
while(pos_ctr < len(position_soup)):
    club_ref = position_soup[pos_ctr].find('a')
    club_ref = club_ref.attrs['href']
    if(club_ref == ('/en/clubs/' + team_code)):
        final_pos = position_soup[pos_ctr].find('td',class_='place').get_text()
        goals_for = position_soup[pos_ctr].find('td',class_='goals_for').get_text()
        goals_against = position_soup[pos_ctr].find('td',class_='goals_against').get_text()
        pos_ctr = len(position_soup)
    pos_ctr = pos_ctr + 1

#Number of Clean Sheets

fixtures_url = url_name + 'clubs/' + team_code + '/fixtures'
fixture_page = requests.get(fixtures_url)
fixtures_soup = BeautifulSoup(fixture_page.content,'html.parser')

table_fixtures = fixtures_soup.find('div',class_='fixtures').find('tbody')
all_fixtures = table_fixtures.find_all('tr')

clean_sheets = 0

for fixture in all_fixtures:
    check_result = fixture.find('td',class_='win_lose').get_text()
    check_result = check_result.replace(" ","")[1]
    if(not check_result == 'L'):
        #get scoreline
        scoreline = fixture.find('td',class_='result')
        scoreline = scoreline.find('a').get_text()
        goals = scoreline.split('-')
        if(len(goals) > 1):
            if(int(goals[0]) == 0 or int(goals[1]) == 0):
                clean_sheets = clean_sheets + 1

#------------------------------------------------------------------------------                
#----------Individual Player Stats----------

player_list = team_soup.find_all('td',class_='player')

#Most Goals
top_scorer = player_list[0].get_text()
num_goals = player_list[0].next_sibling.next_sibling.get_text()

#Cut top scorers off the list after getting the #1
player_list = player_list[7:]

#Keep track of most assists, highest average and most MOTM awards
max_assists = [0,'']
highest_average = [0,'']
most_motm = [0,'']

player_links = []
player_names = []

for player in player_list:
    p_data = player.a.attrs['href']
    player_links.append(p_data)
    player_names.append(player.a.get_text())
    
page_list = []

for link in player_links:
    nav_url = url_name + link + '/history'
    player_page = requests.get(nav_url)
    player_soup = BeautifulSoup(player_page.content,'html.parser')
    page_list.append(player_soup)
    
for page in range(0,len(page_list)):
    team_details = page_list[page].find('div',class_='player_history')
    transfer = team_details.find_all('table')
    if(len(transfer) > 1):
        team_hist = transfer[1]
        #Find gets most recent season
        motm = int(team_hist.find('td',class_='moms').get_text())
        assists = int(team_hist.find('td',class_='assists').get_text())
        avg_rating = float(team_hist.find('td',class_='avg_rating').get_text())

        if(motm > most_motm[0]):
            most_motm[0] = motm
            most_motm[1] = player_names[page]
        if(assists > max_assists[0]):
            max_assists[0] = assists
            max_assists[1] = player_names[page]
        if(avg_rating > highest_average[0]):
            highest_average[0] = avg_rating
            highest_average[1] = player_names[page]

squad_motm = most_motm[1]
num_motm = str(most_motm[0]) + ' MOTM'
squad_assists = max_assists[1]
num_assists = str(max_assists[0]) + ' assists'
squad_avg = highest_average[1]
max_avg = str(highest_average[0]) + ' avg'

#------------------------------------------------------------------------------
#-----------Transfers-------------
transfer_url = '/transfers?page=' 
transfer_page = transfer_url + '1'
next_page = True

transfer_page = url_name + 'clubs/' + team_code + transfer_page
transfers = requests.get(transfer_page)
transfer_soup = BeautifulSoup(transfers.content,'html.parser')
transfer_table = transfer_soup.find_all('div',class_='club_transfers')

transfer_list = transfer_table[0].find_all('tr')

transfers_in = []
transfers_out = []

for tf in transfer_list:
    tf_clubs = tf.find_all('td')
    if(len(tf_clubs) > 3):
        tf_player_name = tf_clubs[0].get_text()
        tf_club_to = tf_clubs[1].get_text()
        tf_club_from = tf_clubs[2].get_text()
        tf_fee = tf_clubs[3].get_text()
        
        if(tf_club_to == '-'):
            tf_club_to = 'Dismissed'
        if(tf_club_from == '-'):
            tf_club_from = 'Free Transfer'

        transfer = [tf_player_name,tf_club_to,tf_club_from,tf_fee]

        if(tf_club_to == team_name):
            transfers_in.append(transfer)
        else:
            transfers_out.append(transfer)
            
#------------------------------------------------------------------------------

def get_position_text(pos):
    '''This method returns a string detailing the team position and a little explanation'''
    if(pos == '1'):
        return '1st place, securing the title and promotion'
    if(pos == '2'):
        return '2nd place, securing promotion but missing out on the title'
    if(pos == '3'):
        return '3rd place, missing out on promotion unfortunately this season'
    if(pos == '13' or pos == '14' or pos == '15' or pos == '16'):
        return final_pos + 'th place, falling foul of a difficult relegation battle'
    else:
        return final_pos + 'th place, staying in the same division next season as they will look to improve next season'
    
def get_position(pos):
    '''This method returns a string representation of the team position'''
    if(pos == '1'):
        return '1st place'
    if(pos == '2'):
        return '2nd place'
    if(pos == '3'):
        return '3rd place'
    else:
        return final_pos + 'th place'
    
def select_pots():
    '''This method calculates the player most deserving of player of the season'''
    return 0

def list_as_lined_string(inp):
    list_string = ''
    if(type(inp) == list):
        if(type(inp[0]) == list):
            for item in inp:
                list_string = list_string + item[0] + ' - To ' + item[1] + ' from ' + item[2] + ' for ' + item[3] + ' credits\n'
    return(list_string[0:-2]) #To remove the last 'New Line'
#------------------------------------------------------------------------------
    
#Generate Squad Details

squad_details = 'The Phoenixes finish the season in ' + get_position_text(final_pos) + '\n\n'
squad_details = squad_details + '[b]Player Stats This Season[/b]\n'
squad_details = squad_details + 'Most Goals: ' + top_scorer + " - " + str(num_goals) + '\nMost Assists: ' + squad_assists + " - " + str(num_assists) + '\nMost MOTM: ' + squad_motm + ' - ' + str(num_motm) + '\nHighest Average: ' + squad_avg + ' - ' + str(max_avg) + '\n\n'
squad_details = squad_details + '[b]Team Stats[/b]\n'
squad_details = squad_details + 'Final Position: ' + get_position(final_pos) + '\nGoals For: ' + str(goals_for) + '\nGoals Against: ' + str(goals_against) + '\nClean Sheets: ' + str(clean_sheets) + '\n'
squad_details = squad_details + '\n\n[b]Player of the Season: [/b]\n'
squad_details = squad_details + '\n\n[b]Transfers IN[/b]\n\n\n' 
squad_details = squad_details + list_as_lined_string(transfers_in) + '\n\n'
squad_details = squad_details + '[b]Transfers OUT[/b]\n'
squad_details = squad_details + list_as_lined_string(transfers_out) + '\n'

season_review_file = open('season_review.txt','w')
season_review_file.write(squad_details)
season_review_file.close()
