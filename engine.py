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
blindPositions = np.random.choice(2, size=2, replace=0)     # 1 = small blind
smallBlindAmount = 4
bigBlindAmount = smallBlindAmount*2

# "Nonstatic" variables
stacks = np.array([121,207])
pot = -1
playerTurn = -1
action = -1
gameStartState = 1
gameEndState = 0
errorInputState = 0


# %%

# Start the round
if(gameStartState):
    gameStartState = 0
    
    # Check that both players have enough money
    if(not np.all(stacks >= bigBlindAmount)):
        print('ERROR')
        # TODO: return error input state
    
    smallBlindIdx = np.argmax(blindPositions)
    bigBlindIdx = np.argmin(blindPositions)
    
    stacks[smallBlindIdx] -= smallBlindAmount
    stacks[bigBlindIdx] -= bigBlindAmount
    
    pot = smallBlindAmount + bigBlindAmount
    
    # Small blind acts first on the preflop in heads up
    playerTurn = smallBlindIdx
    raiseMinMax = np.array([smallBlindAmount,stacks[playerTurn]])   # Max raise is all-in

    # TODO: return stuffs


# %%
    
action = np.array([0,raiseMinMax[0]])   # 1st index is fold, 2nd is raise amount


# %%






















