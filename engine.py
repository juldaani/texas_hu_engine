#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 22:26:05 2018

@author: juho
"""

import numpy as np


# %%

# "Static" variables (over single round)
tmpCards = np.random.choice(52, size=9, replace=0)
boardCards = tmpCards[:5]
boardCardsVisible = np.array([0,0,0,0,0])
holeCards = np.array([tmpCards[5:7],tmpCards[7:]])
blindPositions = np.random.choice(2, size=2, replace=0)     # 1st index = small blind player
smallBlindAmount = 4
bigBlindAmount = smallBlindAmount*2

# "Nonstatic" variables, these are modified by the engine
stacks = np.array([bigBlindAmount,bigBlindAmount+0])
#bets = np.array([0,0])
#hasPlayerActed = np.array([0,0])
#pot = -1
#playerTurn = -1
gameStartState = 1
#gameEndState = 0



# %%

# Start the round
if(gameStartState):
    gameStartState = 0
    pot = 0
    bets = np.array([0,0])
    havePlayersActed = np.array([0,0])
    gameEndState = 0
    
    # Check that both players have enough money
    if(not np.all(stacks >= bigBlindAmount)):
        print('ERROR')
        # TODO: return error
    
    smallBlindPlayerIdx = blindPositions[0]
    bigBlindPlayerIdx = blindPositions[1]
    
    stacks[smallBlindPlayerIdx] -= smallBlindAmount
    bets[smallBlindPlayerIdx] += smallBlindAmount
    stacks[bigBlindPlayerIdx] -= bigBlindAmount
    bets[bigBlindPlayerIdx] += bigBlindAmount
    
    # Small blind acts first on the preflop in heads up
    actingPlayerIdx = smallBlindPlayerIdx
    
    # Available actions
    callAmount = smallBlindAmount
    maxRaiseAmount = np.min(stacks) + callAmount
    raiseMinMax = np.array([min(callAmount+bigBlindAmount, maxRaiseAmount), maxRaiseAmount])   # Max raise is all-in
    if(maxRaiseAmount == callAmount): raiseMinMax[:] = -1
    # TODO: return stuffs


# %%

# In 'action' 
#   1st index is fold
#   2nd is call amount
#   3rd is raise amount. 
# Only one action can be declared, for instance, [-1,-1, 25] means raise to 25.
#action = np.array([-1,callAmount,-1])
action = np.array([-1,callAmount,-1])


# %%

# Check that only one action is declared
#action = np.array([1,-1,raiseMinMax[0]])
if(np.sum(action > -1) != 1):
    print('ERROR')
    # TODO: return error

# Check that call and raise amounts are valid
#action = np.array([-1,346,-1])
if( (action[1] > -1) and (action[1] != callAmount) ):
    print('ERROR')
    # TODO: return error
#action = np.array([-1,-1,raiseMinMax[0]-1])
if( (action[2] > -1) and ((action[2] < raiseMinMax[0]) or (action[2] > raiseMinMax[1])) ):
    print('ERROR')
    # TODO: return error
    
# Check that stacks are not negative
#stacks[0] = -1
if(np.any(stacks < 0)):
    print('ERROR')
    # TODO: return error

actionToExecute = np.argmax(action)
secondPlayerIdx = np.abs(actingPlayerIdx-1)

# Player folds
if(actionToExecute == 0): 
    gameEndState = 1
    pot = -1
    havePlayersActed[:] = -1
    playerTurn = -1
    raiseMinMax[:] = -1
    callAmount = -1
    stacks[secondPlayerIdx] += np.sum(bets)
    bets[:] = -1
    
    # TODO: return stuffs


# Player either calls or raises
if(actionToExecute == 1 or actionToExecute == 2):
    amount = action[actionToExecute]
    
    stacks[actingPlayerIdx] -= amount
    bets[actingPlayerIdx] += amount

    # Check that stacks are not negative after the action
    if(np.any(stacks < 0)):
        print('ERROR')
        # TODO: return error

    havePlayersActed[actingPlayerIdx] = 1
    
    # If the acting player is all-in
    if(stacks[actingPlayerIdx] == 0):
        pot += np.sum(bets)
        bets[:] = 0
        
        print('* * * * * * all-in * * * * * * ')
        # TODO: evaluate player's cards to decide the winner
        # TODO: return stuffs
       
        
    # Check if both players have acted and the bets are equal -> next betting round
    if( (np.sum(havePlayersActed) == len(havePlayersActed)) and (np.sum(np.diff(bets)) == 0) ):
        pot += np.sum(bets)
        bets[:] = 0
        
        


























