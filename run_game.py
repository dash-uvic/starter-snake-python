#!/usr/bin/env python3

import argparse as ap
import requests
import time
import numpy as np
import sys 
import json

ENGINE='http://localhost:3005'
synopsis = []

#Send a HTTP call to validate the engine can ping the snakes
def validate_snake(url):
    req = requests.get(f'{ENGINE}/validateSnake', params = {'url': url})
    rc = req.json()['EndStatus']['statusCode']
    if rc == 200:
        return True
    return False

#Create and start the game, return the game id
def start_game(height, width, food, snakes):
    data = {'height': height,
            'width' : width,
            'food'  : food,
            "snakes" : snakes}  
    
    req = requests.post(f'{ENGINE}/games', json = data)
    game_id = req.json()['ID']
    
    req = requests.post(f"{ENGINE}/games/{game_id}/start")
    return game_id 

#Check if the game is still running, once done return response dictionary
def check_game(snakes):
    who_won = []
    for snake in snakes:
        url = f'{snake["url"]}/status' 
        req = requests.post(url)
        rc = req.json()["status"]
        if rc == 200: return True, [] 
        who_won.append(req.json())

    return False, who_won

#Start the game and wait for it to finish. 
#Returned the stats from the game 
#NOTE: if you kill the game engine the game will be lost
def run_game(config):
    snakes = config["snakes"]
    gid = start_game(config["height"], config["width"], config["food"], snakes)
    game_url = f"http://localhost:3009/?engine={ENGINE}&game={gid}"

    still_running = True
    who_won = []
    while still_running:
        time.sleep(0.5)
        still_running, who_won = check_game(snakes)  
    
    synopsis.append([ game_url , [ {snakes[i]['name'] : who_won[i]['state']} for i in range(0, len(snakes)) ]] )

    #NOTE: with two snakes, turns will always be the same for both 
    return [ x['status'] for x in who_won ], who_won[0]['turns']
    

if __name__ == '__main__':
    parser = ap.ArgumentParser('Test game runner for Battlesnake') 
    parser.add_argument('-c', '--config', default='config.json', help='config file')
    parser.add_argument('-n', '--num-games', default=5, type=int, help='no. of games to run')
    args = parser.parse_args()

    #Load the config file that describes the snakes we want to run  
    with open(args.config, 'r') as f:
        config = json.load(f)

    #Verify that the snakes are active
    for snake in config["snakes"]: 
        if validate_snake(snake['url']):
            print(f"Snake {snake['name']} is active.")
        else:
            print(f"Snake {snake['name']} is inactive.")
            sys.exit(1)

    #Keep track of the number of times each snake wins  
    winners = np.array([0]*len(config["snakes"]))
    #Keep track of how each snake losses (4 possible states)
    results = np.array([0]*4)
    average_turns = 0
    #Run a bunch of games
    for i in range(0, args.num_games):
        print(f"Running test {i}")
        who_won, turns = run_game(config)
        
        average_turns += turns
        results[who_won] += 1
        winners[np.argmin(who_won)] += 1
        
        sys.stdout.write('\a')
        sys.stdout.flush()
  
    #Output the results
    print("average no. of turns: ", average_turns / float(args.num_games))
    print("results:", list(zip(['won', 'suicide', 'starved', 'crashed'],results)))
    print("wins:", list(zip([ x['name'] for x in config['snakes']], winners)))
    print() 
    for game in synopsis:
        print(f"{game[1]}:\n\t{game[0]}\n")
