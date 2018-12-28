#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 25 15:32:22 2018

@author: juho
"""

import unittest
import numpy as np
#import itertools

#from hand_eval.evaluator import evaluate
from texas_hu_engine.engine import initGame, executeAction, getCallAmount, getGameEndState, \
    getStacks, getRaiseAmount, getBets, getPot, getBigBlindAmount, getSmallBlindAmount, \
    getSmallBlindPlayerIdx, getBigBlindPlayerIdx, getBoardCards, getBoardCardsVisible, \
    getPlayerHoleCards, getActingPlayerIdx, getNumPlayersActed, getBettingRound
from hand_eval.params import cardToInt, intToCard

SEED = 123
N_ROUNDS = 1000

"""
* evaluate cards correctly
* pot not negative
* stacks not negative
* bets not negative
* money is not appearing/disappearing out of the blue (pot, stacks, bets)

- game is initialized correctly
    - blinds
    - available actions
    - board
    - cards
    - visible cards
    - 
    

- money is transferred correctly:
    - when betting round is finished money is transferred to pot
    - after raise/call action money is transferred properly to player's bets
    - valid amount of money is transferred to bets/pot after each action/betting round

- available actions are correct (raise amount not lower than call amount..)
- available raise amounts are correct
- available call amount correct

- pre/postflop start player correct
- if player folds:
    - stacks/pot/bets are transferred correctly
    - gameEndState bit is turned on
- if showdown:
    - gameEndState bit is turned on
    - stacks/pot/bets are transferred correctly
- betting rounds are handled correctly:
    - go to next betting round if both players have acted at least once and bets
      are equal
    - visible cards are correct through betting rounds
- check that game goes to showdown if:
    - all-in
    - river
"""


# %%
# Evaluate cards correctly

def convertCardToInt(cards):
    return [cardToInt[card] for card in cards]

def convertIntToCard(ints):
    return [intToCard[intt] for intt in ints]

np.random.seed(SEED)

boardCards = [
        ['2h', '4h', '5h', '6s', '7d'],
        ['Qc', '2c', '3d', '4h', '5s'],
        ['Ks', '2d', '4h', '5s', 'Th'],
        ['Th', '2d', '5h', '8s', '7c'],
        ['6s', '7d', '8h', 'Tc', 'Qh'],
        ['Js', 'Qs', 'Ks', '2d', '4h'],
        ['Tc', 'Th', 'Td', '8h', '9c'],
        ['Kc', 'Ks', 'Kh', '2s', '3s'],
        ['7d', '8d', '9d', 'Jh', 'Qs'],
        ['Qs', 'Ks', 'As', '2d', '6c']
        ]

worseHoleCards = [
        ['9d','Jd'],    # high
        ['9c','Kc'],    # high
        ['Kd','7h'],    # pair
        ['3s','9s'],    # high
        ['6d','7s'],    # two pairs
        ['3d','4s'],    # pair
        ['Jh','Qh'],    # straight
        ['Ts','Td'],    # full house
        ['Tc','Kc'],    # straight
        ['3s','5s']    # flush
        ]
betterHoleCards = [
        ['9s','Kc'],    # high
        ['Qs','Th'],    # pair
        ['Kc','2c'],    # two pairs
        ['Ts','Td'],    # three
        ['4s','5s'],    # straight
        ['3s','5s'],    # flush
        ['7c','7h'],    # full house
        ['Kd','Td'],    # four
        ['5d','6d'],    # straight flush
        ['Ts','Js']    # royal flush
        ]


for worseHole, betterHole, boardC in zip(worseHoleCards,betterHoleCards,boardCards):
    
    # Init game
    boardC = np.array(convertCardToInt(boardC))
    holeCards = np.array([convertCardToInt(betterHole),convertCardToInt(worseHole)])
    smallBlindPlayerIdx = 1     # Which player is small blind?
    smallBlindAmount = 4
    initStackAmount = 100
    stacks = np.array([initStackAmount,initStackAmount])
    board, players, controlVariables, availableActions = initGame(boardC, smallBlindPlayerIdx, 
                                                                  smallBlindAmount, stacks, holeCards)
    # Execute call actions only
    while(1):    
        action = np.array([-1,getCallAmount(availableActions),-1])
        board, players, controlVariables, availableActions = executeAction(board, players, controlVariables, 
                                                                           action, availableActions)
        if(getGameEndState(controlVariables)==1):
            break
    
    stacks = getStacks(players)
    
    # Player index 0 has better cards -> wins big blind
    assert stacks[0] > stacks[1]
    assert (stacks[0] - initStackAmount) == (smallBlindAmount*2)
    assert (initStackAmount - stacks[1]) == (smallBlindAmount*2)
    assert (stacks[0] + stacks[1]) == (initStackAmount*2)


# %%
# Check that the game is initialized correctly
#     - blinds X
#     - board X
#     - players X
#     - available actions
#     - control variables X
#     - cards X
#     - visible cards X
#     - player turns X
    
for i in range(100):
    
    print('\nround: ' + str(i))
    
    tmpCards = np.random.choice(52, size=9, replace=0)
    boardCards = tmpCards[:5]
    holeCards = np.array([tmpCards[5:7],tmpCards[7:]])
    smallBlindPlayerIdx = np.random.randint(0,high=2)
    smallBlindAmount = np.random.randint(1,high=2000)
    initStacks = np.array([smallBlindAmount*np.random.randint(2,high=40),
                           smallBlindAmount*np.random.randint(2,high=40)])
    board, players, controlVariables, availableActions = initGame(boardCards, smallBlindPlayerIdx, 
                                                                  smallBlindAmount, initStacks.copy(), 
                                                                  holeCards)
    
    # Big blind amount correct
    assert getBigBlindAmount(board) == smallBlindAmount*2
    
    # Small blind amount correct 
    assert getSmallBlindAmount(board) == smallBlindAmount
    
    # Board cards correct
    assert np.all(getBoardCards(board) == boardCards)
    
    # No board cards visible
    assert np.sum(getBoardCardsVisible(board)) == 0

    # Pot is zero
    assert getPot(board) == 0


    # Small blind player index is correct
    assert getSmallBlindPlayerIdx(players) == smallBlindPlayerIdx
    
    # Big blind player index is correct
    assert getBigBlindPlayerIdx(players) == (np.abs(smallBlindPlayerIdx-1))
    
    # Player hole cards correct
    assert np.all(getPlayerHoleCards(players,0) == holeCards[0])
    assert np.all(getPlayerHoleCards(players,1) == holeCards[1])
    
    # Small blind is the first player in turn in preflop
    assert getSmallBlindPlayerIdx(players)  == getActingPlayerIdx(players)
    
    # Bets are correct (blind amounts)
    bets = getBets(players)
    smallBlindIdx = getSmallBlindPlayerIdx(players)
    bigBlindIdx = getBigBlindPlayerIdx(players)
    assert bets[smallBlindIdx] == smallBlindAmount
    assert bets[bigBlindIdx] == smallBlindAmount*2
    
    # Stacks are correct (blind amounts are transferred from player's stacks)
    stacks = getStacks(players)
    assert initStacks[smallBlindIdx] - smallBlindAmount == stacks[smallBlindIdx]
    assert initStacks[bigBlindIdx] - smallBlindAmount*2 == stacks[bigBlindIdx]
    
    # Any of the players shouldn't have acted
    assert getNumPlayersActed(players) == 0
    
    
    # Game not terminated
    assert getGameEndState(controlVariables) == 0
    
    # Game is on preflop (bettingRound = 0)
    assert getBettingRound(controlVariables) == 0
    
    
    # Call and raise amounts correct
    callAmount = getCallAmount(availableActions)
    trueRaiseMax = np.min(stacks) + callAmount
    trueRaiseMin = 
    assert callAmount == smallBlindAmount
    
    if(trueRaiseMax > callAmount):
        
    
    bets
    stacks
    
    raiseMin = getRaiseAmount(availableActions)[0]
    trueRaiseMax = smallBlindAmount + smallBlindAmount*2
    
    
    np.min(getStacks(players)
    getBets(players)
    
#    assert raiseMin == trueRaiseMin

#    raiseMax = getRaiseAmount(availableActions)[1]
    
    
    

    
# %%
# Check that 
#   - pot, stacks or bets are not negative
#   - money is not appearing/disappearing out of the blue
    
    
np.random.seed(SEED)
    
for i in range(10000):
    
    print('\nround: ' + str(i))
    
    tmpCards = np.random.choice(52, size=9, replace=0)
    boardCards = tmpCards[:5]
    holeCards = np.array([tmpCards[5:7],tmpCards[7:]])
    smallBlindPlayerIdx = np.random.randint(0,high=2)
    smallBlindAmount = np.random.randint(1,high=2000)
    initStacks = np.array([smallBlindAmount*np.random.randint(2,high=40),
                           smallBlindAmount*np.random.randint(2,high=40)])
    board, players, controlVariables, availableActions = initGame(boardCards, smallBlindPlayerIdx, 
                                                                  smallBlindAmount, initStacks.copy(), 
                                                                  holeCards)

    # Check that not negative        
    assert np.all(getStacks(players) >= 0)
    assert np.all(getBets(players) >= 0)
    assert getPot(board) >= 0
    
    # Check that money is not appearing/disappearing out of the blue
    assert np.sum(initStacks) == (np.sum(getStacks(players)) + getPot(board) + np.sum(getBets(players)))
    
    while(1):
        actions = np.zeros(2, dtype=np.int) - 1
        
        # If raise is available
        raiseAmount = getRaiseAmount(availableActions)
        if(np.any(raiseAmount >= 0)):
            actions = np.zeros(3, dtype=np.int) - 1
            actions[2] = np.random.randint(raiseAmount[0],high=raiseAmount[1]+1)
            
        actions[0] = 1
        actions[1] = getCallAmount(availableActions)
        
        tmp = np.arange(len(actions))   # Decrease fold probability
        tmp = np.concatenate((tmp, np.tile(tmp[1:],6)))
        actionIdx = tmp[np.random.randint(0,high=len(tmp))]

        actionToExec = np.zeros(3, dtype=np.int) - 1
        actionToExec[actionIdx] = actions[actionIdx]
        
        board, players, controlVariables, availableActions = executeAction(board, players, controlVariables, 
                                                                           actionToExec, availableActions)
        # Check that not negative        
        assert np.all(getStacks(players) >= 0)
        assert np.all(getBets(players) >= 0)
        assert getPot(board) >= 0
        
        # Check that money is not appearing/disappearing out of the blue
        assert np.sum(initStacks) == (np.sum(getStacks(players)) + getPot(board) + np.sum(getBets(players)))
        
        if(getGameEndState(controlVariables)==1):
#            print('game end')
            break
    
    
# %%
# Check that
#   - raise amount not lower than call amount
#   - available raise and call amounts are correct according to holdem rules


np.random.seed(SEED)
    
for i in range(1):
    
    print('\nround: ' + str(i))
    
    tmpCards = np.random.choice(52, size=9, replace=0)
    boardCards = tmpCards[:5]
    holeCards = np.array([tmpCards[5:7],tmpCards[7:]])
    smallBlindPlayerIdx = np.random.randint(0,high=2)
    smallBlindAmount = np.random.randint(1,high=2000)
    initStacks = np.array([smallBlindAmount*np.random.randint(2,high=40),
                           smallBlindAmount*np.random.randint(2,high=40)])
    board, players, controlVariables, availableActions = initGame(boardCards, smallBlindPlayerIdx, 
                                                                  smallBlindAmount, initStacks.copy(), 
                                                                  holeCards)
    bigBlindAmount = getBigBlindAmount(board)    
    
    # Check that blinds are correct
    
    
    while(1):
        actions = np.zeros(2, dtype=np.int) - 1
        
        # If raise is available
        raiseAmount = getRaiseAmount(availableActions)
        if(np.any(raiseAmount >= 0)):
            actions = np.zeros(3, dtype=np.int) - 1
            actions[2] = np.random.randint(raiseAmount[0],high=raiseAmount[1]+1)
            
        actions[0] = 1
        actions[1] = getCallAmount(availableActions)
        
        tmp = np.arange(len(actions))   # Decrease fold probability
        tmp = np.concatenate((tmp, np.tile(tmp[1:],6)))
        actionIdx = tmp[np.random.randint(0,high=len(tmp))]

#        print(actionIdx)
        
        actionToExec = np.zeros(3, dtype=np.int) - 1
        actionToExec[actionIdx] = actions[actionIdx]
        
        board, players, controlVariables, availableActions = executeAction(board, players, controlVariables, 
                                                                           actionToExec, availableActions)
        
        raiseAmount = getRaiseAmount(availableActions)
        callAmount = getCallAmount(availableActions)
        
        smallBlindAmount
        getStacks(players)
        getBets(players)
        
        # Calculate correct actions
        trueCallAmount = getBets(players)
        
        
        bigBlindAmount
        
        if((raiseAmount[0] >= 0) and (raiseAmount[1] >= 0)):    # If raise action available
            # Check that raise amount not lower than call amount
            assert np.all(raiseAmount >= callAmount)
            
            # Check that raise min is lower or equal to raise max
            assert raiseAmount[0] <= raiseAmount[1]
        
            # 
            
            
        if(getGameEndState(controlVariables)==1):
#            print('game end')
            break












 











