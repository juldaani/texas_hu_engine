#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 25 15:32:22 2018

@author: juho

Tests for evaluating the engine.

"""

import numpy as np

from texas_hu_engine.engine import initGame, executeAction, getCallAmount, getGameEndState, \
    getStacks, getRaiseAmount, getBets, getPot, getBigBlindAmount, getSmallBlindAmount, \
    getSmallBlindPlayerIdx, getBigBlindPlayerIdx, getBoardCards, getBoardCardsVisible, \
    getPlayerHoleCards, getActingPlayerIdx, getNumPlayersActed, getBettingRound, getWinningPlayerIdx
from hand_eval.params import cardToInt, intToCard
from hand_eval.evaluator import evaluate

SEED = 123
N_ROUNDS = 50000


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
#     - blinds
#     - board
#     - players
#     - available actions
#     - control variables
#     - cards
#     - visible cards
#     - player turns
    
for i in range(N_ROUNDS):
    if(i % 1000 == 0): print(i, N_ROUNDS)
    
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
    
    
    # Call amount correct
    actingPlayerIdx = smallBlindPlayerIdx
    trueCallAmount = np.abs(bets[0]-bets[1])
    callAmount = getCallAmount(availableActions)
    assert trueCallAmount == callAmount
    assert stacks[actingPlayerIdx] - callAmount >= 0      # enough money for call action
    
    # Raise amount correct
    tmpStacks = stacks.copy()
    tmpStacks[actingPlayerIdx] -= trueCallAmount
    trueRaiseMax = np.min(tmpStacks) + trueCallAmount
    trueRaiseMin = min(max(trueCallAmount + smallBlindAmount*2, trueCallAmount*2), trueRaiseMax)
    assert np.all( (stacks - (trueRaiseMin - trueCallAmount)) >= 0)
    assert np.all( (stacks - (trueRaiseMax - trueCallAmount)) >= 0)
    assert np.any( (stacks - trueRaiseMax) == 0) or \
        np.any( (stacks - trueRaiseMax) == -trueCallAmount)
    raiseMinMax = getRaiseAmount(availableActions)
    if(trueRaiseMax == trueCallAmount):
        assert raiseMinMax[0] == -1
        assert raiseMinMax[1] == -1
    else:
        assert raiseMinMax[0] > trueCallAmount
        assert raiseMinMax[1] > trueCallAmount
        assert raiseMinMax[0] <= raiseMinMax[1]
        assert np.all( (stacks - (raiseMinMax[0] - trueCallAmount)) >= 0)
        assert np.all( (stacks - (raiseMinMax[1] - trueCallAmount)) >= 0)
        assert np.any( (stacks - raiseMinMax[1]) == 0) or \
            np.any( (stacks - raiseMinMax[1]) == -trueCallAmount)
        assert raiseMinMax[0] == trueRaiseMin
        assert raiseMinMax[1] == trueRaiseMax
        
        
    
# %%
# Check that 
#   - pot, stacks or bets are not negative
#   - money is not appearing/disappearing out of the blue
    

np.random.seed(SEED)
    
for i in range(N_ROUNDS):
    if(i % 1000 == 0): print(i, N_ROUNDS)
    
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
# Check that:
#   - available actions are correct (raise amount not lower than call amount etc..)
#   - available raise amounts are correct
#   - available call amount correct
#   - after raise/call action money is transferred properly to certain player's bets
# If showdown:
#    * gameEndState bit is turned on
#    * if tie the pot is splitted
#    * stacks/pot/bets are transferred correctly
#    * correct winning player idx
# If player folds:
#    * stacks/pot/bets are transferred correctly
#    * gameEndState bit is turned on
#    * correct winning player idx

np.random.seed(SEED)

for i in range(N_ROUNDS):
    if(i % 1000 == 0): print(i, N_ROUNDS)
    
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
    
    while(1):
        raiseMinMax = getRaiseAmount(availableActions)
        callAmount = getCallAmount(availableActions)
        stacks = getStacks(players)
        bets = getBets(players)

        # Call amount correct
        actingPlayerIdx = getActingPlayerIdx(players)
        trueCallAmount = np.abs(bets[0]-bets[1])
        callAmount = getCallAmount(availableActions)
        assert trueCallAmount == callAmount
        assert stacks[actingPlayerIdx] - callAmount >= 0      # enough money for call action
        
        # Raise amount correct
        tmpStacks = stacks.copy()
        tmpStacks[actingPlayerIdx] -= trueCallAmount
        trueRaiseMax = np.min(tmpStacks) + trueCallAmount
        trueRaiseMin = min(max(trueCallAmount + smallBlindAmount*2, trueCallAmount*2), trueRaiseMax)
        assert np.all( (stacks - (trueRaiseMin - trueCallAmount)) >= 0)
        assert np.all( (stacks - (trueRaiseMax - trueCallAmount)) >= 0)
        assert np.any( (stacks - trueRaiseMax) == 0) or \
            np.any( (stacks - trueRaiseMax) == -trueCallAmount)
        if(trueRaiseMax == trueCallAmount):
            assert raiseMinMax[0] == -1
            assert raiseMinMax[1] == -1
        else:
            assert raiseMinMax[0] > trueCallAmount
            assert raiseMinMax[1] > trueCallAmount
            assert raiseMinMax[0] <= raiseMinMax[1]
            assert np.all( (stacks - (raiseMinMax[0] - trueCallAmount)) >= 0)
            assert np.all( (stacks - (raiseMinMax[1] - trueCallAmount)) >= 0)
            assert np.any( (stacks - raiseMinMax[1]) == 0) or \
                np.any( (stacks - raiseMinMax[1]) == -trueCallAmount)
            assert raiseMinMax[0] == trueRaiseMin
            assert raiseMinMax[1] == trueRaiseMax
        
        # Pick randomly action to execute
        actions = np.zeros(2, dtype=np.int) - 1
        if(np.any(raiseMinMax >= 0)):   # If raise is available
            actions = np.zeros(3, dtype=np.int) - 1
            actions[2] = np.random.randint(raiseMinMax[0],high=raiseMinMax[1]+1)
        actions[0] = 1
        actions[1] = callAmount
        tmp = np.arange(len(actions))   # Decrease fold probability
        tmp = np.concatenate((tmp, np.tile(tmp[1:],6)))
        actionIdx = tmp[np.random.randint(0,high=len(tmp))]
        actionToExec = np.zeros(3, dtype=np.int) - 1
        actionToExec[actionIdx] = actions[actionIdx]
        
        # Get stacks, bets and pot before the action
        stacksBeforeAction = getStacks(players).copy()
        betsBeforeAction = getBets(players).copy()
        potBeforeAction = getPot(board).copy()
        numPlayersActed = getNumPlayersActed(players).copy()
        moneyTotBeforeAction = np.sum(stacksBeforeAction) + np.sum(betsBeforeAction) + potBeforeAction
        actingPlayerIdx = getActingPlayerIdx(players).copy()
        otherPlayerIdx = np.abs(actingPlayerIdx-1)
        isRiver = np.sum(getBoardCardsVisible(board)) == 5
        
        board, players, controlVariables, availableActions = executeAction(board, players, controlVariables, 
                                                                           actionToExec, availableActions)
        
        stacksAfterAction = getStacks(players)
        betsAfterAction = getBets(players)
        potAfterAction = getPot(board)
        moneyTotAfterAction = np.sum(stacksAfterAction) + np.sum(betsAfterAction) + potAfterAction
        
        
        # Check money balances after the action
        assert moneyTotAfterAction == moneyTotBeforeAction
        
        # If the fold action was declared
        if(np.argmax(actionToExec) == 0):
            assert getGameEndState(controlVariables) == 1
            assert np.all(availableActions == -1)
            assert np.all(betsAfterAction == 0)
            assert potAfterAction == 0
            assert getWinningPlayerIdx(controlVariables) == otherPlayerIdx
            
            # Correct amount transferred to player's stack
            moneyOnTable = np.sum(betsBeforeAction) + potBeforeAction
            assert (stacksBeforeAction[otherPlayerIdx] + moneyOnTable) == stacksAfterAction[otherPlayerIdx]
            assert stacksBeforeAction[actingPlayerIdx] == stacksAfterAction[actingPlayerIdx]
        
        # If call or raise action was declared
        if( np.argmax(actionToExec) == 1 or np.argmax(actionToExec) == 2 ):
            amount = np.max(actionToExec)
            
            tmpStackAmount = stacksBeforeAction[actingPlayerIdx] - amount
            trueStacksAfterAction = stacksBeforeAction.copy()
            trueStacksAfterAction[actingPlayerIdx] = tmpStackAmount
            
            trueBetsAfterAction = betsBeforeAction.copy()
            trueBetsAfterAction[actingPlayerIdx] += amount
            
            truePotAfterAction = potBeforeAction
            
            # If next betting round (money is transferred to pot instead of player bets)
            areBetsEqual = (betsBeforeAction[actingPlayerIdx] + amount) == betsBeforeAction[otherPlayerIdx]
            if(numPlayersActed >= 1 and areBetsEqual):
                truePotAfterAction = np.sum(betsBeforeAction) + amount + potBeforeAction
                trueBetsAfterAction = np.array([0,0])
                
            # If all-in or river showdown (money is transferred to stacks instead of pot or bets)
            isAllInShowdown = areBetsEqual and np.any(trueStacksAfterAction == 0) and (numPlayersActed >= 1)
            isRiverShowdown = areBetsEqual and isRiver and (numPlayersActed >= 1)
            if(isAllInShowdown or isRiverShowdown):
                truePotAfterAction = 0
                trueBetsAfterAction = np.array([0,0])
                
                cardsBoard = getBoardCards(board)
                cardsPlayer0 = np.concatenate((getPlayerHoleCards(players,0), cardsBoard))
                cardsPlayer1 = np.concatenate((getPlayerHoleCards(players,1), cardsBoard))
                rankPlayer0 = evaluate(cardsPlayer0)
                rankPlayer1 = evaluate(cardsPlayer1)
                trueWinningPlayerIdx = np.argmin([rankPlayer0[0], rankPlayer1[0]])
                if(rankPlayer0[0] == rankPlayer1[0]):   # Tie
                    trueWinningPlayerIdx = -1
                    tmpStacks = stacksBeforeAction.copy()
                    tmpStacks[actingPlayerIdx] -= amount
                    moneyOnTable = np.sum(betsBeforeAction) + potBeforeAction + amount
                    halfMoney = moneyOnTable / 2
                    trueStacksAfterAction = tmpStacks.copy()
                    trueStacksAfterAction[0] += halfMoney
                    trueStacksAfterAction[1] += halfMoney
                else:
                    tmpStacks = stacksBeforeAction.copy()
                    tmpStacks[actingPlayerIdx] -= amount
                    moneyOnTable = np.sum(betsBeforeAction) + potBeforeAction + amount
                    trueStacksAfterAction = tmpStacks.copy()
                    trueStacksAfterAction[trueWinningPlayerIdx] += moneyOnTable
                
                assert getWinningPlayerIdx(controlVariables) == trueWinningPlayerIdx
                assert getGameEndState(controlVariables) == 1
                assert np.all(availableActions == -1)
                assert np.all(betsAfterAction == 0)
                assert potAfterAction == 0
                
            assert truePotAfterAction == potAfterAction
            assert np.all(trueBetsAfterAction == betsAfterAction)
            assert np.all(trueStacksAfterAction == stacksAfterAction)
                
            
        if(getGameEndState(controlVariables)==1):
            break
        






 











