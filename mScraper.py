from bs4 import BeautifulSoup
import requests
import pandas as pd
from mVariables import team_dictionary, month_list, month_dictionary

def get_data(start_url):
    base_url = 'https://www.basketball-reference.com'
    month_link_array = []
    response = requests.get(start_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    season = soup.find('h1').text
    season = season.strip().split(' ')
    season = season[0]
    body = soup.findAll('body')
    months = body[0].findAll('a', href = True)
    for i in months:
        if i.text.lower() in month_list:
            i = (i.text, f'{base_url}{i["hhref"]}')
            month_link_array.append(i)
    page_tocheck_dict = {'Month': [], 'Url': [], 'Index': []}
    box_link_array = []
    all_dates = []

    for month, page in month_link_array:
        page_link_array = []
        page_date_array = []
        response = requests.get(page)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.findAll('tbody')
        box_scores = table[0].findAll('a', href=True)
        for i in box_scores:
            if i.text.strip() == 'Box Score':
                page_link_array.append(f'{base_url}{i["href"]}')
            if ',' in i.text.strip():
                date = i.text.strip()
                date = date.split(', ')
                year = date[2]
                date = date[1].split(' ')
                day = f'0{date[1]}' if len(date[1]) == 1 else date[1]

                mon = month_dictionary[date[0]]
                date = f'{year}{mon}{day}'
                page_date_array.append(date)
            if len(page_link_array) == 0 or len(box_scores)/len(page_link_array) != 4:
                page_tocheck_dict['Url'].append(page)
                page_tocheck_dict['Month'].append(month)
                page_tocheck_dict['Index'].append(len(page_link_array))
            else:
                page_tocheck_dict['Url'].append(page)
                page_tocheck_dict['Month'].append(month)
                page_tocheck_dict['Index'].append(None)
            box_link_array.append(page_link_array)
            all_dates.append(page_date_array)

    df_columns = ['Date', 'Name', 'Team', 'MP', 'FG', 'FGA', 'FG%', '3P', '3PA',
                  '3P%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL',
                  'BLK', 'TOV', 'PF', 'PTS', '+-']
    stat_df = pd.DataFrame(columns = df_columns)
    for l, d in zip(box_link_array, all_dates):
        for link, date in zip(l, d):
            print(f'{link}\n{date}')
            print(f'Currently Scraping {link}')
            response = requests.get(link)
            soup = BeautifulSoup(response.text, 'html.parser')

            table1 = soup.find('table', {'class': "sortable stats_table"})
            team = table1.text.split('\n')[0]
            parenthesis = team.find('(')
            team = team[:parenthesis - 1]
            print(team)
            table1 = table1.find('tbody')
            table1 = table1.find_all('tr')
            rows = []
            for row in table1:
                name = row.findAll('th')[0].text
                cols = row.findAll('td')
                cols = [i.text.strip() for i in cols]
                cols.append(name)
                rows.append(cols)
            for player in rows:
                if len(player) < 21:
                    continue
                else:
                    player = [0 if i == '' else i for i in player]
                    colon = player[0].find(':')
                    time = f'{player[0][:colon]}.{player[0][colon + 1::]}'
                    print(player, len(player))
                    player_dic = {'Date': date, 'Name': player[-1], 'Team': team_dictionary[team], 
                                'MP': time,'FG': player[1], 'FGA': player[2], 
                                'FG%': player[3], '3P': player[4], '3PA': player[5],
                                '3P%': player[6], 'FT': player[7], 'FTA': player[8], 
                                'FT%': player[9],'ORB': player[10], 
                                'DRB': player[11], 'TRB': player[12], 
                                'AST': player[13], 'STL': player[14], 
                                'BLK': player[15], 'TOV': player[16], 'PF': player[17],
                                'PTS': player[18], '+-': player[19]}
                    stat_df = stat_df.append(player_dic, ignore_index=True)
                    continue

            table2 = soup.findAll('table', {'class': "sortable stats_table"})
            team = table2[9].text.split('\n')[0]
            parenthesis = team.find('(')
            team = team[:parenthesis - 1]
            table2 = table2[9].find('tbody')
            table2 = table2.find_all('tr')
            rows = []
            for row in table2:
                name = row.findAll('th')[0].text
                cols = row.findAll('td')
                cols = [i.text.strip() for i in cols]
                cols.append(name)
                rows.append(cols)
                for player in rows:
                    if len(player) < 21:
                        print(player)
                        continue
                    else:
                        player = [0 if i == '' else i for i in player]
                        colon = player[0].find(':')
                        time = f'{player[0][:colon]}.{player[0][colon + 1::]}'
                        print(player, len(player))
                        player_dic = {'Date': date, 'Name': player[-1], 'Team': team_dictionary[team], 
                                      'MP': time,'FG': player[1],'FGA': player[2], 
                                      'FG%': player[3], '3P': player[4], 
                                      '3PA': player[5],'3P%': player[6], 'FT': player[7], 
                                      'FTA': player[8], 'FT%': player[9],
                                      'ORB': player[10], 'DRB': player[11], 
                                      'TRB': player[12], 'AST': player[13],
                                      'STL': player[14], 'BLK': player[15], 
                                      'TOV': player[16], 'PF': player[17],
                                      'PTS': player[18], '+-': player[19]}
                        stat_df = stat_df.append(player_dic, ignore_index=True)
                        continue  
                            
                print(f'Finished Scraping: {link}')
                # stat_df.to_csv(f'Season{{season}).csv', line_terminator = '\n', index=False)

    stat_df.to_csv(f'Season({season}).csv', line_terminator='\n', index=False)
    print(f'Saved game stats for the {season} season to a csv')