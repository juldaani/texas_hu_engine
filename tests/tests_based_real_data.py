#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 23 21:08:35 2019

@author: juho

Tests are using hand history data which can be downloaded from:
    https://drive.google.com/open?id=1jIvFuoJAus2_Z5mhRO5SDIFuyr0Mt7se

Data is also available on (ABS-2009-07-01_2009-07-23...):
    http://web.archive.org/web/20110205042259/http://www.outflopped.com/questions/286/
    obfuscated-datamined-hand-histories
    
In order to run these tests, the data must be first parsed with 'hand_history_parser.py'.

"""


import numpy as np

from texas_hu_engine.engine import initGame, executeAction, getCallAmount, getGameEndState, \
    getStacks, getRaiseAmount, getBets, getPot, getBigBlindAmount, getSmallBlindAmount, \
    getSmallBlindPlayerIdx, getBigBlindPlayerIdx, getBoardCards, getBoardCardsVisible, \
    getPlayerHoleCards, getActingPlayerIdx, getNumPlayersActed, getBettingRound, getWinningPlayerIdx
from hand_eval.params import cardToInt, intToCard
from hand_eval.evaluator import evaluate


def getGameVariables(game):
    stacks = game['init_stacks']
    playerIds = [playerId for playerId in stacks]
    stacks = np.array([stacks[playerIds[0]], stacks[playerIds[1]]])
    
    blinds = game['blinds']
    blinds = np.array([blinds[playerIds[0]], blinds[playerIds[1]]])
    smallBlindPlayerIdx = np.argmin(blinds)
    smallBlindAmount = blinds[smallBlindPlayerIdx]
    
    hashToPlayerIdx = {playerId:i for i,playerId in enumerate(playerIds)}
    playerIdxToHash = {i:playerId for i,playerId in enumerate(playerIds)}
    
    winPlayerIdx = hashToPlayerIdx[game['win_player']]
    losePlayerIdx = np.abs(1-winPlayerIdx)
    losePlayerHash = playerIdxToHash[losePlayerIdx]
    
    actionsList = game['pocket_cards'] + game['flop'] + game['turn'] + game['river']
    for action in actionsList:
        if(losePlayerHash in action):
            loserPlayerFinalStack = action[losePlayerHash]['stack']
    winAmount = game['init_stacks'][losePlayerHash] - loserPlayerFinalStack
    
    # Generate cards so that the correct player wins
    holeCards = np.zeros((2,2), dtype=np.int)
    holeCards[winPlayerIdx] = [cardToInt['As'], cardToInt['Ah']]
    holeCards[losePlayerIdx] = [cardToInt['2s'], cardToInt['4h']]
    boardCards = np.zeros(5, dtype=np.int)
    boardCards[0], boardCards[1], boardCards[2], boardCards[3], boardCards[4] = \
        cardToInt['Ac'], cardToInt['Ad'], cardToInt['6s'], cardToInt['8c'], cardToInt['Tc']

    return boardCards, holeCards, smallBlindPlayerIdx, smallBlindAmount, stacks, winPlayerIdx, \
        winAmount, hashToPlayerIdx, playerIdxToHash


def getTruePlayerIdx(action, hashToPlayerIdx):
    playerHash = list(action.keys())[0]
    return hashToPlayerIdx[playerHash]


def getTrueActionAndAmount(action):
    actionToNumeric = {'Folds':0, 'Calls':1, 'Checks':1, 'Bets':1, 'Raises':1,
                       'All-In(Raise)':1, 'All-In':1}
    
    tmp = list(action.values())[0]
    act = tmp['action'][0]
    amnt = tmp['action'][1]
    totalBets = tmp['totalBets']
    totalPot = tmp['totalPot']
    stack = tmp['stack']
    bets = tmp['bets']
    
    if(act == 'Folds'): amnt = 1
    
    return actionToNumeric[act], amnt, totalBets, totalPot, stack, bets
    

def getActionToExecute(action):
    # In 'action' 
    #   1st index is fold
    #   2nd is call/raise/bet amount
    # Only one action can be declared, for instance, [-1, 25] means raise/call etc. 25.
    
    trueActionIdx, trueActionAmount, trueTotalBets, trueTotalPot, trueStack, trueBets = \
        getTrueActionAndAmount(action)
    actionToExec = np.zeros(2, dtype=np.int) - 1
    actionToExec[trueActionIdx] = trueActionAmount
    
    return actionToExec, trueActionAmount, trueTotalBets, trueTotalPot, trueStack, trueBets



path = '/home/juho/dev_folder/texas_hu_engine/tests/hand_histories/0.5/'

games = np.load(path + 'parsed_games.npy')
orig = np.load(path + 'original_games.npy')

SEED = 123
states = ['pocket_cards', 'flop', 'turn', 'river']
np.random.seed(SEED)



# %%
# Test:
#   - players are acting in the correct order
#   - the action amount is inside the limits given by the game engine
#   - stacks are handled correctly
#   - pot is correct

for game, origGame, i in zip(games, orig, np.arange(len(games))):
    if(i % 1000 == 0): print(i, len(games))
    
    boardCards, holeCards, smallBlindPlayerIdx, smallBlindAmount, initStacks, trueWinPlayerIdx, \
        trueWinAmount, hashToPlayerIdx, playerIdxToHash = getGameVariables(game)
    trueLoserPlayerIdx = np.abs(trueWinPlayerIdx-1)
        
    board, players, controlVariables, availableActions = initGame(boardCards, smallBlindPlayerIdx, 
                                                                  smallBlindAmount, initStacks.copy(), 
                                                                  holeCards)
    for state in states:
        actions = game[state]
        
        for action in actions:
            truePlayerIdx = getTruePlayerIdx(action, hashToPlayerIdx)
            playerIdx = getActingPlayerIdx(players)
            otherPlayerIdx = np.abs(truePlayerIdx-1)
            actionToExec, amount, trueTotalBets, trueTotalPot, trueStack, trueBets = \
                getActionToExecute(action)

            # Limits given by the game engine
            raiseMinMax = getRaiseAmount(availableActions)
            callAmount = getCallAmount(availableActions)
            
            # Test players are acting in the correct order
            assert truePlayerIdx == playerIdx
            
            # Test that the action amount is inside the limits given by the game engine 
            if(actionToExec[1] >= 0):    # If not fold
                assert (amount == callAmount) or (amount >= raiseMinMax[0] and amount <= raiseMinMax[1])
            
            stacksBeforeAction = getStacks(players).copy()
            
            # Execute the action
            board, players, \
                controlVariables, availableActions = executeAction(board, players, controlVariables, 
                                                                   actionToExec, availableActions)
            
            stacksAfterAction = getStacks(players).copy()
            
            # Skip if the game has ended because after finishing the game the pot and stacks behave 
            # differently (winning player's stack is increased and losing player's decreased...)
            if(getGameEndState(controlVariables) != 1):     
                # Test that stacks are handled correctly
                assert stacksBeforeAction[truePlayerIdx]-amount == stacksAfterAction[truePlayerIdx]
                assert stacksBeforeAction[otherPlayerIdx] == stacksAfterAction[otherPlayerIdx]
                assert getStacks(players)[playerIdx] == trueStack
                
                # Test pot correct
                assert np.sum(getBets(players))+getPot(board) == trueTotalPot
                    

# %%
# Test betting rounds are handled correctly:
#    * correct visible cards during the betting rounds
#    * correct betting round number
#    * when betting round is finished money is transferred into pot and bets are set to zero
#    * after the action the money is transferred properly to player's bets


tmpVisibleCards = [np.array([0,0,0,0,0]), np.array([1,1,1,0,0]), np.array([1,1,1,1,0]), 
                   np.array([1,1,1,1,1])]
trueVisibleCards = {state:i for state,i in zip(states,tmpVisibleCards)}
trueBettingRoundNumber = {state:i for state,i in zip(states,[0,1,2,3])}

for game, origGame, i in zip(games, orig, np.arange(len(games))):
    if(i % 1000 == 0): print(i, len(games))
    
    boardCards, holeCards, smallBlindPlayerIdx, smallBlindAmount, initStacks, trueWinPlayerIdx, \
        trueWinAmount, hashToPlayerIdx, playerIdxToHash = getGameVariables(game)
    trueLoserPlayerIdx = np.abs(trueWinPlayerIdx-1)
        
    board, players, controlVariables, availableActions = initGame(boardCards, smallBlindPlayerIdx, 
                                                                  smallBlindAmount, initStacks.copy(), 
                                                                  holeCards)
    for state in states:
        actions = game[state]
        trueCards = trueVisibleCards[state]
        trueBettingRoundNum = trueBettingRoundNumber[state]
        
        nActions = len(actions)
        for i,action in enumerate(actions):
            truePlayerIdx = getTruePlayerIdx(action, hashToPlayerIdx)
            playerIdx = getActingPlayerIdx(players)
            otherPlayerIdx = np.abs(truePlayerIdx-1)
            actionToExec, amount, trueTotalBets, trueTotalPot, trueStack, trueBets = \
                getActionToExecute(action)

            # Correct visible cards
            assert np.all(trueCards == getBoardCardsVisible(board))
            
            # Correct betting round number
            if(getGameEndState(controlVariables) != 1):     # if the game hasn't yet ended
                assert trueBettingRoundNum == getBettingRound(controlVariables)
            
            # Execute the action
            board, players, \
                controlVariables, availableActions = executeAction(board, players, controlVariables, 
                                                                   actionToExec, availableActions)
            
            # Skip last because the engine has already transferred bets into pot but 'trueTotalBets'
            # still contains that amount.
            if(i < nActions-1):     
                assert np.sum(getBets(players)) == trueTotalBets
                assert getBets(players)[playerIdx] == trueBets

        # When betting round is finished money is transferred into pot and bets are set to zero
        assert np.all(getBets(players) == [0,0])
        if(getGameEndState(controlVariables) != 1):     # if the game hasn't yet ended
            assert getPot(board) == trueTotalPot
        

# %%
# Tests when player folds or the game goes to showdown:
#   * game ends
#   * correct winning player idx
#   * stacks are correct (money in winner's stack has increased by correct amount...)

for game, origGame, i in zip(games, orig, np.arange(len(games))):
    if(i % 1000 == 0): print(i, len(games))
    
    boardCards, holeCards, smallBlindPlayerIdx, smallBlindAmount, initStacks, trueWinPlayerIdx, \
    trueWinAmount, hashToPlayerIdx, playerIdxToHash = getGameVariables(game)
        
    board, players, controlVariables, availableActions = initGame(boardCards, smallBlindPlayerIdx, 
                                                                  smallBlindAmount, initStacks.copy(), 
                                                                  holeCards)
    for state in states:
        actions = game[state]
        
        nActions = len(actions)
        isAllIn = False
        for i,action in enumerate(actions):
            truePlayerIdx = getTruePlayerIdx(action, hashToPlayerIdx)
            playerIdx = getActingPlayerIdx(players)
            
            actionToExec, amount, trueTotalBets, trueTotalPot, trueStack, trueBets = \
                getActionToExecute(action)
                
            tmpAction = list(action.values())[0]['action'][0]
            isAllIn = tmpAction == 'All-In(Raise)' or tmpAction == 'All-In'
            isFold = tmpAction == 'Folds'
            
            # Execute the action
            board, players, \
                controlVariables, availableActions = executeAction(board, players, controlVariables, 
                                                                   actionToExec, availableActions)
            
            isRiverShowdown = (state == 'river') and (i == nActions-1) and (tmpAction != 'Folds')
            isAllInShowdown = (i == nActions-1) and (tmpAction != 'Folds') and isAllIn

            if(isRiverShowdown or isAllInShowdown or isFold):
                winPlayerIdx = getWinningPlayerIdx(controlVariables)
                losePlayerIdx = np.abs(1-winPlayerIdx)

                # The game ends when showdown / fold
                assert getGameEndState(controlVariables) == 1
            
                # Correct winning player
                assert trueWinPlayerIdx == winPlayerIdx
                
                # Stacks are correct
                stacks = getStacks(players)
                winAmount = stacks[winPlayerIdx] - initStacks[winPlayerIdx]
                assert trueWinAmount == winAmount
                assert stacks[winPlayerIdx] > initStacks[winPlayerIdx]
                assert stacks[losePlayerIdx] < initStacks[losePlayerIdx]
                assert stacks[winPlayerIdx] == initStacks[winPlayerIdx] + trueWinAmount
                assert stacks[losePlayerIdx] == initStacks[losePlayerIdx] - trueWinAmount
                
                # Pot and bets are zero
                assert getPot(board) == 0
                assert np.all(getBets(players) == [0,0])
                




















