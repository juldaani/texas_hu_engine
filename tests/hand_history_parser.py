#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  2 13:47:38 2019

@author: juho
"""


PATH = '/home/juho/dev_folder/texas_hu_engine/tests/hand_histories/10/abs NLH handhq_1-OBFUSCATED.txt'


with open (PATH, "r") as myfile: data = myfile.read()


games = data.split('Stage')


# %%

c = 0

games2 = []
for game in games:
    

    # Only heads up no-limit games & not ante
    if( ('(1 on 1)' in game) & ('No Limit' in game) & ('ante' not in game) ):     
        
        c += 1
        if(c > 1): break
    
        # Multiply all amounts to remove decimal parts
        multiplier = 1000
        
        # Player ids
        player1Id = game.split('Seat ')[2].split(' - ')[1].split(' ($')[0]
        player2Id = game.split('Seat ')[3].split(' - ')[1].split(' ($')[0]

        # Stacks
        player1Stack = int(float(game.split(player1Id)[1].split('($')[1].split(' in ')[0].
                                            replace(',','') ) * multiplier)
        player2Stack = int(float(game.split(player2Id)[1].split('($')[1].split(' in ')[0].
                                            replace(',','') ) * multiplier)
    
        # Player 1 blind amount & is small blind
        sttr = game.split(player1Id)[2]
        idx = sttr.find('\n')
        sttr = sttr[:idx]
        isPlayer1SmallBlind = 'Posts small blind' in sttr
        player1BlindAmount = int(float(sttr.split('$')[1]) * multiplier)
        
        # Player 2 blind amount
        sttr = game.split(player2Id)[2]
        idx = sttr.find('\n')
        sttr = sttr[:idx]
        player2BlindAmount = int(float(sttr.split('$')[1]) * multiplier)
        
        
        idx1 = game.find('*** POCKET CARDS ***')
        statesData = game[idx1:]
        
        gameStateSearchStrings = ['*** POCKET CARDS ***', '*** FLOP ***', '*** TURN ***', 
                                  '*** RIVER ***', '*** SHOW DOWN ***', '*** SUMMARY ***']
        
        gameStatesDict = {'pocket_cards':None, 'flop':None, 'turn':None, 'river':None, 
                          'show_down':None, 'summary':None}
        
        for stateStr, key in zip(gameStateSearchStrings, gameStatesDict):
            
            print(stateStr, key)
            
            if(stateStr in statesData):
                
                assert 0
                
                
                sttr = statesData.split(stateStr)[1]
                sttr = sttr[:sttr.find('***')]
                lines = sttr.splitlines()[1:]
                
                for line in lines:
                    split = line.split(' - ')
                    playerId = split[0]
                    action, amount = split[1].split(' $')
                    amount = int(float(amount) * multiplier)
                    
                
                gameStatesDict[key] = asdfad
                                        
        
        
        [state in sttr for state in gameStates]
        
        sttr.split('*#* AAD *')
        
        sttr.splitlines()
























