#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 22:26:05 2018

@author: juho
"""

import numpy as np



# board: pot, smallBlindAmount, bigBlindAmount, boardCardsVisible, boardCards
# players: holeCards, stacks, bets, isSmallBlind, isBigBlind, isPlayersTurn, hasActed
# availableActions: fold, callAmount, raiseMinMax
# controlVariables: bettingRound, gameEndState





# Players .....................................................................
def getStacks(playerStates): return playerStates[:,2]

def getBets(playerStates): return playerStates[:,3]

def setBet(playerStates, amount, playerIdx):
    playerStates[playerIdx,2] -= amount     # Stack
    playerStates[playerIdx,3] += amount     # Bets
    return playerStates

def setActingPlayerIdx(playerStates, playerIdx): 
    otherPlayerIdx = np.abs(playerIdx-1)
    playerStates[playerIdx,6] = 1
    playerStates[otherPlayerIdx,6] = 0
    return playerStates

def getActingPlayerIdx(playerStates): return np.where(playerStates[:,6] != 0)[0][0]

def setHasPlayerActed(playerState, playerIdx):
    playerState[playerIdx,7] = 1
    return playerState


# Board .......................................................................
def getSmallBlindAmount(boardState): return boardState[1]

def getBigBlindAmount(boardState): return boardState[2]

def moveBetsToPot(playerState, boardState):
    boardState[0] += np.sum(playerState[:,3])
    playerState[:,3] = 0
    return playerState, boardState

def movePotToPlayer(playerState, playerIdx, boardState):
    playerState[playerIdx,2] += boardState[0]           # Stacks
    boardState[0] = 0
    return playerState, boardState


# Actions .....................................................................
def getAvailableActions(playerState, boardState):
    bets = getBets(playerState)
    stacks = getStacks(playerState)
    bigBlindAmount = getBigBlindAmount(boardState)
    callAmount = np.abs(bets[0]-bets[1])
    maxRaiseAmount = np.min(stacks)
    raiseMinMax = np.array([min(max(callAmount+bigBlindAmount,callAmount*2), maxRaiseAmount), 
                            maxRaiseAmount])   # Max raise is all-in
    return np.concatenate((np.array([callAmount]),raiseMinMax))

def getCallAmount(availableActions): return availableActions[0]

def getRaiseAmount(availableActions): return availableActions[1:]


# Control variables ...........................................................
def setGameEndState(controlVariables, availableActions):
    controlVariables[1] = 1
    availableActions[:] = -1
    return controlVariables, availableActions


def initGame(boardCards, smallBlindPlayerIdx, smallBlindAmount, stacks, holeCards):
    
    # Set board
    board = np.zeros(13, dtype=np.int)
    board[0] = 0                    # Pot
    board[1] = smallBlindAmount     # Small blind amount
    board[2] = smallBlindAmount*2   # Big blind amount
    board[3:8] = 0                  # Visible board cards
    board[8:] = boardCards          # Board cards
    
    # Set players
    players = np.zeros((2,9), dtype=np.int)
    players[:,:2] = holeCards       # Hole cards
    players[:,2] = stacks           # Stacks
    players[:,3] = 0                # Bets
    players[smallBlindPlayerIdx,4] = 1      # Set small blind for the player
    bigBlindPlayerIdx = np.abs(smallBlindPlayerIdx-1)
    players[bigBlindPlayerIdx,5] = 1        # Set big blind for the player
    players = setActingPlayerIdx(players, smallBlindPlayerIdx)  # Small blind acts first on the preflop in heads up
    players[:,7] = 0                # Has player acted?
    players[:,8] = 0                # Is player all-in?
    
    # Set game control variables
    controlVariables = np.zeros(2, dtype=np.int)
    controlVariables[0] = 0         # Betting round
    controlVariables[1] = 0         # Game end state
    
    # Check that both players have enough money
    if(not np.all(getStacks(players) >= getBigBlindAmount(board))):
        print('ERROR, not enough money')
        board = None
        players = None
        availableActions = None
        controlVariables = None
        return board, players, availableActions, controlVariables
    
    # Set bets
    players = setBet(players, getSmallBlindAmount(board), smallBlindPlayerIdx)
    players = setBet(players, getBigBlindAmount(board), bigBlindPlayerIdx)
    
    # Available actions
    availableActions = getAvailableActions(players, board)
    
    return board, players, controlVariables, availableActions





# %%

tmpCards = np.random.choice(52, size=9, replace=0)
boardCards = tmpCards[:5]
holeCards = np.array([tmpCards[5:7],tmpCards[7:]])
smallBlindPlayerIdx = 1     # Which player is small blind?
smallBlindAmount = 4
stacks = np.array([smallBlindAmount*8+2,smallBlindAmount*6+5])



# %%


board, players, controlVariables, availableActions = initGame(boardCards, smallBlindPlayerIdx, 
                                                              smallBlindAmount, stacks, holeCards)
    

    


# %%
    
# In 'action' 
#   1st index is fold
#   2nd is call amount
#   3rd is raise amount. 
# Only one action can be declared, for instance, [-1,-1, 25] means raise to 25.

#action = np.array([-1,-1,raiseMinMax[1]])
#action = np.array([-1,getCallAmount(availableActions),-1])
action = np.array([1,-1,-1])





#pot, bets, stacks, bigBlindAmount, numPlayersActed, gameEndState, bettingRound, \
#    boardCardsVisible, actingPlayerIdx, callAmount, raiseMinMax = \
#    executeAction(pot, bets, stacks, bigBlindAmount, numPlayersActed, gameEndState, 
#                  bettingRound, boardCardsVisible, actingPlayerIdx, callAmount, raiseMinMax, action)
#    
#    
    
    

# %%
#
#def executeAction(pot, bets, stacks, bigBlindAmount, numPlayersActed, gameEndState, 
#                  bettingRound, boardCardsVisible, actingPlayerIdx, callAmount, raiseMinMax, action):
    
    callAmount = getCallAmount(availableActions)
    raiseMinMax = getRaiseAmount(availableActions)
    actingPlayerIdx = getActingPlayerIdx(players)

    # Check that only one action is declared
    if(np.sum(action > -1) != 1):
        print('ERROR 0')
        return None
        
    # Check that call and raise amounts are valid
    if( (action[1] > -1) and (action[1] != callAmount) ):
        print('ERROR 1')
        return None
    if( (action[2] > -1) and ((action[2] < raiseMinMax[0]) or (action[2] > raiseMinMax[1])) ):
        print('ERROR 2')
        return None
        
    # Check that stacks are not negative
    if(np.any(stacks < 0)):
        print('ERROR 3')
        return None
        
    actionToExecute = np.argmax(action)
    secondPlayerIdx = np.abs(actingPlayerIdx-1)
    
    # Player folds
    if(actionToExecute == 0):
        controlVariables, availableActions = setGameEndState(controlVariables, availableActions)
        players, board = moveBetsToPot(players, board)
        players, board = movePotToPlayer(players, secondPlayerIdx, board)
        players = setHasPlayerActed(players, actingPlayerIdx)

        print('* * * * * PLAYER FOLDS * * * * * *')
        
        return board, players, controlVariables, availableActions
        
    
    # Player either calls or raises
    if(actionToExecute == 1 or actionToExecute == 2):
        amount = action[actionToExecute]
        
        stacks[actingPlayerIdx] -= amount
        bets[actingPlayerIdx] += amount
    
        # Check that stacks are not negative after the action
        if(np.any(stacks < 0)):
            print('ERROR')
            return None
    
        numPlayersActed += 1
        nextPlayerIdx = secondPlayerIdx
     
        # Check if both players have acted and the bets are equal -> next betting round or showdown
        if( (numPlayersActed >= 2) and (np.sum(np.diff(bets)) == 0) ):
            pot += np.sum(bets)
            bets[:] = 0
            numPlayersActed = 0
            boardCardsVisible[:3+min(bettingRound,2)] = boardCards[:3+min(bettingRound,2)]
            bettingRound += 1
            
            # Big blind acts first on the flop, turn and river
            bigBlindPlayerIdx = blindPositions[1]
            nextPlayerIdx = bigBlindPlayerIdx
            
            # If all-in situation then go to the showdown
            if(np.min(stacks) == 0): bettingRound = 4
            
            # Showdown
            if(bettingRound > 3):
                print('* * * * SHOWDOWN * * * * ')
                # TODO: Evaluete hands
                # TODO: return stuffs
                return 666
        
        
        # Available actions
        callAmount = np.abs(bets[0]-bets[1])
        maxRaiseAmount = np.min(stacks) #+ callAmount
        raiseMinMax = np.array([min(max(callAmount+bigBlindAmount,callAmount*2), maxRaiseAmount), 
                                maxRaiseAmount])   # Max raise is all-in
        if(maxRaiseAmount < callAmount): raiseMinMax[:] = -1


        return pot, bets, stacks, bigBlindAmount, numPlayersActed, gameEndState, \
            bettingRound, boardCardsVisible, nextPlayerIdx, callAmount, raiseMinMax
























