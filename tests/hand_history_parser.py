#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  2 13:47:38 2019

@author: juho
"""


PATH = '/home/juho/dev_folder/texas_hu_engine/tests/hand_histories/test_data7.txt'


with open (PATH, "r") as myfile: data = myfile.read()


games = data.split('Stage')


# %%

def getReturnAmount(lines, lineIdx, playerId):
    returnAmount = 0
    
    if( (len(lines)-1 >= lineIdx+2) and ('returned' in lines[lineIdx+2]) and not 
        ('Folds' in lines[lineIdx+1]) ):
        tmpLine = lines[lineIdx+2]
        tmpSplit = tmpLine.split(' - ')
        tmpPlayerId = tmpSplit[0]
        assert playerId == tmpPlayerId
        returnAmount = tmpSplit[1].split(' ($')[1].split(')')[0]
        returnAmount = int(float(returnAmount) * multiplier)
    
    return returnAmount


c = 0

games2 = []
for game in games:
    

    # Only heads up no-limit games & not ante
    if( ('(1 on 1)' in game) & ('No Limit' in game) & ('ante' not in game) ):     
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
        
        print('*** STACKS ***')
        print(player1Id, player1Stack)
        print(player2Id, player2Stack)
    
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
        
        print('*** BLINDS ***')
        print(player1Id, player1BlindAmount)
        print(player2Id, player2BlindAmount)
        
        idx1 = game.find('*** POCKET CARDS ***')
        statesData = game[idx1:]
        
        gameStateSearchStrings = ['*** POCKET CARDS ***', '*** FLOP ***', '*** TURN ***', 
                                  '*** RIVER ***', '*** SHOW DOWN ***', '*** SUMMARY ***']
        
        gameStatesDict = {'pocket_cards':None, 'flop':None, 'turn':None, 'river':None, 
                          'show_down':None, 'summary':None}
        


        for stateStr, key in zip(gameStateSearchStrings, gameStatesDict):
            
            print(stateStr)
            
            if(stateStr in statesData):
                
                sttr = statesData.split(stateStr)[1]
                sttr = sttr[:sttr.find('***')]
                lines = sttr.splitlines()[1:]
                
                for lineIdx in range(len(lines)):
                    line = lines[lineIdx]                    
                    
                    if(key == 'pocket_cards' or key == 'flop' or key == 'turn' or key == 'river'):
                        split = line.split(' - ')
                        playerId = split[0]

                        if('Calls' in split[1]):
                            action, amount = split[1].split(' $')
                            amount = int(float(amount) * multiplier)
                            print(playerId, action,amount)
                        elif('Bets' in split[1]):
                            action, amount = split[1].split(' $')
                            amount = int(float(amount) * multiplier)
                            returnAmount = getReturnAmount(lines, lineIdx, playerId)
                            amount -= returnAmount
                            
#                            if(key == 'river'):
#                                assert 0
                            
                            print(playerId, action,amount)
                        elif('Raises' in split[1]):
                            action, amount, _ = split[1].split(' $')
                            amount = int(float(amount.split(' to')[0]) * multiplier)
                            returnAmount = getReturnAmount(lines, lineIdx, playerId)
                            amount -= returnAmount     
                            print(playerId, action,amount)
                        elif('Checks' in split[1]):
                            action, amount = 'Checks', 0
                            print(playerId, action,amount)
                        elif('Folds' in split[1]):
                            action, amount = 'Folds', 0
                            print(playerId, action,amount)
                        elif('All-In(Raise)' in split[1]):
                            _, amount, _ = split[1].split(' $')
                            action = 'All-In'
                            amount = int(float(amount.split(' to')[0]) * multiplier)
                            returnAmount = getReturnAmount(lines, lineIdx, playerId)
                            amount -= returnAmount     
                            print(playerId, action,amount)          
                        elif('All-In' in split[1]):
                            action, amount = split[1].split(' $')
                            amount = int(float(amount.replace(',','')) * multiplier)
                            returnAmount = getReturnAmount(lines, lineIdx, playerId)
                            amount -= returnAmount     
                            print(playerId, action,amount)
                            

                    
#                gameStatesDict[key] = asdfad
                                        
        
























