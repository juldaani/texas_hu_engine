#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 23 21:08:35 2019

@author: juho
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
    winAmount = game['win_amount']
    
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




games = np.load('/home/juho/dev_folder/texas_hu_engine/tests/hand_histories/10/parsed_games.npy')
orig = np.load('/home/juho/dev_folder/texas_hu_engine/tests/hand_histories/10/original_games.npy')

SEED = 123
states = ['pocket_cards', 'flop', 'turn', 'river']
np.random.seed(SEED)



# %%
# Test:
#   - players are acting in the correct order
#   - the action amount is inside the limits given by the game engine
#   - stacks are handled correctly
#   - pot is correct

for game, origGame in zip(games, orig):
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
                
            
            
#            elif(getGameEndState(controlVariables) == 1):   # The game has ended
#                assert getWinningPlayerIdx(controlVariables) == trueWinPlayerIdx
#                assert initStacks[trueWinPlayerIdx]+trueWinAmount == stacksAfterAction[trueWinPlayerIdx]
#                assert initStacks[trueLoserPlayerIdx]-trueWinAmount == stacksAfterAction[trueLoserPlayerIdx]
                    

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


for game, origGame in zip(games, orig):
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

np.save('orig', origGame)
np.save('parsed', game)



"""
* Test players are acting in correct order
* Test that the action amount is inside the limits given by the game engine 
* betting rounds are handled correctly:
    * go to next betting round if both players have acted at least once and bets
      are equal
    * visible cards are correct through betting rounds
    * when betting round is finished money is transferred to pot and bets are set to zero
    * other variables are correct
    * after raise/call action money is transferred properly to player's bets


- check that game goes to showdown if:
    - all-in
    - river
- if showdown:
    - stacks/pot/bets are transferred correctly
    - correct winning player idx
    - stacks are correct (money in winner's stack has increased)
- if player folds:
    - stacks/pot/bets are transferred correctly
    - correct winning player idx
    - stacks are correct (money in winner's stack has increased)


"""























