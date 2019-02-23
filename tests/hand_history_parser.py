#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  2 13:47:38 2019

@author: juho

Parser for hand histories downloaded from:
http://web.archive.org/web/20110205042259/http://www.outflopped.com/questions/286/
obfuscated-datamined-hand-histories

"""


import os
import numpy as np


def getReturnAmount(lines, lineIdx, playerId, amount, gameDict, stacks):
    returnAmount = 0
    
#    print('\n ---------------------- ')
#    print(lineIdx, playerId, stacks, amount)
#    print(' ')
#    print(lines)
#    print(' ')
#    print(gameDict)
#    
#    lineIdx = 0
#    playerId = 'JJnyL2vrvzAOyNLMMb6gHw'
#    stacks = {'FL4lGd0uLGmUjgC6CYjapQ': 658750, 'JJnyL2vrvzAOyNLMMb6gHw': 1377750}
#    amount = 1370000
#    lines = ['JJnyL2vrvzAOyNLMMb6gHw - Bets $1,370', 'FL4lGd0uLGmUjgC6CYjapQ - Folds', 'JJnyL2vrvzAOyNLMMb6gHw - returned ($1,370) : not called'] 
#    gameDict = {'pocket_cards': [{'FL4lGd0uLGmUjgC6CYjapQ': {'action': ['Calls', 5000], 'totalBets': 20000, 'totalPot': 20000, 'stack': 928750}}, {'JJnyL2vrvzAOyNLMMb6gHw': {'action': ['Checks', 0], 'totalBets': 20000, 'totalPot': 20000, 'stack': 1647750}}], 'flop': [{'JJnyL2vrvzAOyNLMMb6gHw': {'action': ['Bets', 20000], 'totalBets': 20000, 'totalPot': 40000, 'stack': 1627750}}, {'FL4lGd0uLGmUjgC6CYjapQ': {'action': ['Raises', 40000], 'totalBets': 60000, 'totalPot': 80000, 'stack': 888750}}, {'JJnyL2vrvzAOyNLMMb6gHw': {'action': ['Raises', 90000], 'totalBets': 150000, 'totalPot': 170000, 'stack': 1537750}}, {'FL4lGd0uLGmUjgC6CYjapQ': {'action': ['Calls', 70000], 'totalBets': 220000, 'totalPot': 240000, 'stack': 818750}}], 'turn': [{'JJnyL2vrvzAOyNLMMb6gHw': {'action': ['Bets', 160000], 'totalBets': 160000, 'totalPot': 400000, 'stack': 1377750}}, {'FL4lGd0uLGmUjgC6CYjapQ': {'action': ['Calls', 160000], 'totalBets': 320000, 'totalPot': 560000, 'stack': 658750}}], 'river': [], 'win_player': None, 'win_amount': None, 'init_stacks': {'FL4lGd0uLGmUjgC6CYjapQ': 938750, 'JJnyL2vrvzAOyNLMMb6gHw': 1657750}, 'blinds': {'FL4lGd0uLGmUjgC6CYjapQ': 5000, 'JJnyL2vrvzAOyNLMMb6gHw': 10000}}
#    
    
    if( (len(lines)-1 >= lineIdx+2) and ('returned' in lines[lineIdx+2]) and 
           not ('Folds' in lines[lineIdx+1]) ):
        tmpLine = lines[lineIdx+2]
        tmpSplit = tmpLine.split(' - ')
        tmpPlayerId = tmpSplit[0]
        assert playerId == tmpPlayerId
        returnAmount = tmpSplit[1].split(' ($')[1].split(')')[0]
        returnAmount = round(float(returnAmount.replace(',','')) * multiplier)
    elif( (len(lines)-1 >= lineIdx+2) and ('returned' in lines[lineIdx+2]) ):
        
#        if(amount == 1370000 and playerId == 'JJnyL2vrvzAOyNLMMb6gHw'): assert 0
        
        initStacks = gameDict['init_stacks']
        playerIds = list(gameDict['blinds'].keys())
        moneyCurrentlyIn = {playerIds[0]:initStacks[playerIds[0]]-stacks[playerIds[0]],
                            playerIds[1]:initStacks[playerIds[1]]-stacks[playerIds[1]]}
        diff = np.abs(np.diff(np.array(list(moneyCurrentlyIn.values())))[0])
        minStack = np.min(np.array(list(stacks.values())))
        
        if((amount - diff) > minStack):
            returnAmount = amount - diff - minStack
        
    return returnAmount


def parseActions(line, lines, lineIdx, gameDict, stacks):
    split = line.split(' - ')
    playerId = split[0]

    action, amount = -1, -1
    if('Calls' in split[1]):
        action, amount = split[1].split(' $')
        amount = round(float(amount.replace(',','')) * multiplier)
#        print(playerId, action,amount)
    elif('Bets' in split[1]):
        action, amount = split[1].split(' $')
        amount = round(float(amount.replace(',','')) * multiplier)
        returnAmount = getReturnAmount(lines, lineIdx, playerId, amount, gameDict, stacks)
        amount -= returnAmount
#        print(playerId, action,amount)
    elif('Raises' in split[1]):
        action, amount, _ = split[1].split(' $')
        amount = round(float(amount.replace(',','').split(' to')[0]) * multiplier)
        returnAmount = getReturnAmount(lines, lineIdx, playerId, amount, gameDict, stacks)
        amount -= returnAmount     
#        print(playerId, action,amount)
    elif('Checks' in split[1]):
        action, amount = 'Checks', 0
#        print(playerId, action,amount)
    elif('Folds' in split[1]):
        action, amount = 'Folds', 0
#        print(playerId, action,amount)
    elif('All-In(Raise)' in split[1]):
        _, amount, _ = split[1].split(' $')
        action = 'All-In'
        amount = round(float(amount.replace(',','').split(' to')[0]) * multiplier)
        returnAmount = getReturnAmount(lines, lineIdx, playerId, amount, gameDict, stacks)
        amount -= returnAmount     
#        print(playerId, action,amount)          
    elif('All-In' in split[1]):
        action, amount = split[1].split(' $')
        amount = round(float(amount.replace(',','')) * multiplier)
        returnAmount = getReturnAmount(lines, lineIdx, playerId, amount, gameDict, stacks)
        amount -= returnAmount     
#        print(playerId, action, amount)
    
    return playerId, action, amount


def parseBlind(game, playerId, multiplier):
    sttr = game.split(playerId)[2]
    idx = sttr.find('\n')
    sttr = sttr[:idx]
    return round(float(sttr.split('$')[1]) * multiplier)


# %%


PATH = '/home/juho/dev_folder/texas_hu_engine/tests/hand_histories/10/'
multiplier = 1000   # Multiply all amounts to remove decimal parts

gameStateSearchStrings = ['*** POCKET CARDS ***', '*** FLOP ***', '*** TURN ***', 
                          '*** RIVER ***', '*** SHOW DOWN ***', '*** SUMMARY ***']

fNames = os.listdir(PATH)

games = []
for f in fNames:
    with open (PATH + f, "r") as myfile: data = myfile.read()
    games += data.split('Stage')

# %%

parsedGames, originalGameData = [], []
for n,game in enumerate(games):
#    print(n, len(games))
    
#    game = origGame     # TODO: remove
    
    # Only heads up no-limit games & not ante
    if( ('(1 on 1)' in game) & ('No Limit' in game) & ('ante' not in game) ):     
        
#        if(n>281):assert 0
        
        gameDict = {'pocket_cards':[], 'flop':[], 'turn':[], 'river':[], 
                    'win_player':None, 'win_amount':None}
        
        # Player ids
        player1Id = game.split('Seat ')[2].split(' - ')[1].split(' ($')[0]
        player2Id = game.split('Seat ')[3].split(' - ')[1].split(' ($')[0]

        # Stacks
        player1Stack = round(float(game.split(player1Id)[1].split('($')[1].split(' in ')[0].
                                            replace(',','') ) * multiplier)
        player2Stack = round(float(game.split(player2Id)[1].split('($')[1].split(' in ')[0].
                                            replace(',','') ) * multiplier)
        
        gameDict['init_stacks'] = {player1Id:player1Stack, player2Id:player2Stack}
        stacks = {player1Id:player1Stack, player2Id:player2Stack}
        
#        print('*** STACKS ***')
#        print(player1Id, player1Stack)
#        print(player2Id, player2Stack)
    
        # Blind amounts
        player1BlindAmount = parseBlind(game, player1Id, multiplier)
        player2BlindAmount = parseBlind(game, player2Id, multiplier)
        
        gameDict['blinds'] = {player1Id:player1BlindAmount, player2Id:player2BlindAmount}

#        print('*** BLINDS ***')
#        print(player1Id, player1BlindAmount)
#        print(player2Id, player2BlindAmount)
        
        # Remove blinds from stacks
        stacks[player1Id] -= player1BlindAmount
        stacks[player2Id] -= player2BlindAmount
        
        idx1 = game.find('*** POCKET CARDS ***')
        statesData = game[idx1:]
        
        
        
        gameEvents = ['pocket_cards', 'flop', 'turn', 'river', 'show_down', 'summary']
        totalPot = 0
        for stateStr, key in zip(gameStateSearchStrings, gameEvents):
#            print(stateStr)
            totalBets = 0
            if(key == 'pocket_cards'):
                totalBets = player1BlindAmount + player2BlindAmount
            
            if(stateStr in statesData):
                sttr = statesData.split(stateStr)[1]
                sttr = sttr[:sttr.find('***')]
                lines = sttr.splitlines()[1:]
                
                for lineIdx in range(len(lines)):
                    line = lines[lineIdx]
                    
                    if(key == 'pocket_cards' or key == 'flop' or key == 'turn' or key == 'river'):
                        
#                        assert 0    # TODO: remove
                        
                        playerId, action, amount = parseActions(line, lines, lineIdx, gameDict, stacks)
                        if(action == -1): continue
                        stacks[playerId] -= amount
                        totalBets += amount
                        gameDict[key].append({playerId:{'action':[action,amount],
                                                        'totalBets':totalBets,
                                                        'totalPot':totalPot + totalBets,
                                                        'stack':stacks[playerId]}})
                        
                    if(key == 'show_down'):
                        if('Collects $' in line):
                            split = line.split(' Collects $')
                            winPlayerId = split[0]
                            gameDict['win_player'] = winPlayerId
#                            print('Win player: ' + winPlayerId)

                    if(key == 'summary'):
                        if('Total Pot($' in line):
                            winAmount = round(float(line.split('Total Pot($')[1].split(')')[0].
                                                  replace(',','')) * multiplier)
                            gameDict['win_amount'] = winAmount #- \
                                #(gameDict['init_stacks'][winPlayerId] - stacks[winPlayerId])
#                            print('Win amount: ' + str(winAmount))
                                
                
                totalPot += totalBets
    
        parsedGames.append(gameDict)
        originalGameData.append(game)

# %%        
        


np.save(PATH+'parsed_games', parsedGames)
np.save(PATH+'original_games', originalGameData)

















