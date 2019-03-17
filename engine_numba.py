#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 22:26:05 2018

@author: juho
"""

import numpy as np
from numba import jit
from hand_eval.evaluator_numba import evaluate_numba2 as evaluate
from hand_eval.params import ranks_7cards, LUT_nChooseK_7cards



# Players .....................................................................
@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def getStacks(playerStates): return playerStates[:,2]

@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def getBets(playerStates): return playerStates[:,3]

@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def setBet(playerStates, amount, playerIdx):
    playerStates[playerIdx,2] -= amount     # Stack
    playerStates[playerIdx,3] += amount     # Bets
    return playerStates

@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def setActingPlayerIdx(playerStates, playerIdx): 
    otherPlayerIdx = np.abs(playerIdx-1)
    playerStates[playerIdx,6] = 1
    playerStates[otherPlayerIdx,6] = 0
    return playerStates

@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def getActingPlayerIdx(playerStates): return np.where(playerStates[:,6] != 0)[0][0]

@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def getBigBlindPlayerIdx(playerState): return np.argmax(playerState[:,5])

@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def getSmallBlindPlayerIdx(playerState): return np.argmax(playerState[:,4])

@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def setHasPlayerActed(playerState, playerIdx):
    playerState[playerIdx,7] = 1
    return playerState

@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def getNumPlayersActed(playerState): return np.sum(playerState[:,7])

@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def getPlayerHoleCards(playerState, playerIdx): return playerState[playerIdx,:2]
    

# Board .......................................................................
@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def getSmallBlindAmount(boardState): return boardState[1]

@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def getBigBlindAmount(boardState): return boardState[2]

@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def moveBetsToPot(playerState, boardState):
    boardState[0] += np.sum(playerState[:,3])
    playerState[:,3] = 0
    return playerState, boardState

@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def movePotToPlayer(playerState, playerIdx, boardState):
    if(playerIdx == -1):    # If tie
        halfPot = boardState[0] / 2
        playerState[0,2] += halfPot     # Stacks
        playerState[1,2] += halfPot
        boardState[0] = 0
    else:
        playerState[playerIdx,2] += boardState[0]           # Stacks
        boardState[0] = 0
        
    return playerState, boardState
    
@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def getBoardCardsVisible(boardState): return boardState[3:8]
    
@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def setBoardCardsVisible(boardState, visibleMask):
    boardState[3:8] = visibleMask
    return boardState

@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def getBoardCards(boardState): return boardState[8:]

@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def getPot(boardState): return boardState[0]


# Actions .....................................................................
@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def getAvailableActions(playerState, boardState):
    actingPlayerIdx = getActingPlayerIdx(playerState)
    bets = getBets(playerState)
    bigBlindAmount = getBigBlindAmount(boardState)
    callAmount = np.abs(bets[0]-bets[1])
    tmpStacks = getStacks(playerState).copy()
    tmpStacks[actingPlayerIdx] -= callAmount
    raiseMax = np.min(tmpStacks) + callAmount   # Max raise is all-in
    raiseMin = min(max(callAmount + bigBlindAmount, callAmount*2), raiseMax)
    raiseMinMax = np.array([raiseMin, raiseMax])
    
    if(raiseMax == callAmount):
        raiseMinMax[:] = -1
    
    return np.concatenate((np.array([callAmount]),raiseMinMax))

@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def getCallAmount(availableActions): return availableActions[0]

@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def getRaiseAmount(availableActions): return availableActions[1:]


# Control variables ...........................................................
@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def setGameEndState(controlVariables, availableActions, winPlayerIdx):
    controlVariables[0] = -1                # Betting round
    controlVariables[1] = 1                 # Game end state
    controlVariables[2] = winPlayerIdx      # Winning player index
    availableActions[:] = -1
    return controlVariables, availableActions

@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def getGameEndState(controlVariables):
    return controlVariables[1]

@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def getBettingRound(controlVariables): return controlVariables[0]
    
@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def setBettingRound(controlVariables, bettingRound): 
    controlVariables[0] = bettingRound
    return controlVariables

@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def getWinningPlayerIdx(controlVariables):
    return controlVariables[2]


# Initializers ................................................................
@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def initNextBettingRound(boardState, playerState, controlVariables):
    playerState[:,7] = 0    # Reset has players acted
    
    # Set visible board cards
    bettingRound = getBettingRound(controlVariables)
    boardCardsVisible = getBoardCardsVisible(boardState)
    boardCardsVisible[:3+min(bettingRound,2)] = 1
    boardState = setBoardCardsVisible(boardState, boardCardsVisible) 
    
    # Next betting round
    bettingRound += 1
    controlVariables = setBettingRound(controlVariables, bettingRound)
    
    # Big blind acts first on the flop, turn and river
    playerIdx = getBigBlindPlayerIdx(playerState)
    playerState = setActingPlayerIdx(playerState, playerIdx)
    
    return boardState, playerState, controlVariables

@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def initGame(boardCards, smallBlindPlayerIdx, smallBlindAmount, stacks, holeCards):
    # Set board
    board = np.zeros(13, dtype=np.int64)
    board[0] = 0                    # Pot
    board[1] = smallBlindAmount     # Small blind amount
    board[2] = smallBlindAmount*2   # Big blind amount
    board[3:8] = 0                  # Visible board cards
    board[8:] = boardCards          # Board cards
    
    # Set players
    players = np.zeros((2,8), dtype=np.int64)
    players[:,:2] = holeCards       # Hole cards
    players[:,2] = stacks           # Stacks
    players[:,3] = 0                # Bets
    players[smallBlindPlayerIdx,4] = 1      # Set small blind for the player
    bigBlindPlayerIdx = np.abs(smallBlindPlayerIdx-1)
    players[bigBlindPlayerIdx,5] = 1        # Set big blind for the player
    players = setActingPlayerIdx(players, smallBlindPlayerIdx)  # Small blind acts first on the preflop in heads up
    players[:,7] = 0                # Has player acted?
    
    # Set game control variables
    controlVariables = np.zeros(3, dtype=np.int16)
    controlVariables[0] = 0         # Betting round
    controlVariables[1] = 0         # Game end state
    controlVariables[2] = -100      # Winning player idx, -1 means tie
    
    # Check that both players have enough money
    if(not np.all(getStacks(players) >= getBigBlindAmount(board))):
        print('ERROR, not enough money')
        board[:] = -999
        players[:] = -999
        availableActions = np.zeros(3, dtype=np.int64) - 999
        controlVariables[:] = -999
        return board, players, controlVariables, availableActions
    
    # Set bets
    players = setBet(players, getSmallBlindAmount(board), smallBlindPlayerIdx)
    players = setBet(players, getBigBlindAmount(board), bigBlindPlayerIdx)
    
    # Available actions
    availableActions = getAvailableActions(players, board)
    
    return board, players, controlVariables, availableActions

    
# .............................................................................
# Game logic
@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def returnInvalidOutput(board, players, controlVariables, availableActions):
    board[:], players[:], controlVariables[:], availableActions[:] = \
        -999, -999, -999, -999
    return board, players, controlVariables, availableActions

@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def executeAction(board, players, controlVariables, action, availableActions):
    
    # Do not continue if the game has already finished
    if(getGameEndState(controlVariables) == 1):
        return returnInvalidOutput(board, players, controlVariables, availableActions)
    
    callAmount = getCallAmount(availableActions)
    raiseMinMax = getRaiseAmount(availableActions)
    actingPlayerIdx = getActingPlayerIdx(players)
    stacks = getStacks(players)
    secondPlayerIdx = np.abs(actingPlayerIdx-1)
    # In 'action' 
    #   1st index is fold
    #   2nd is call/raise/bet amount
    # Only one action can be declared, for instance, [-1, 25] means raise/call 25
    actionToExecute = np.argmax(action)
    
    # Check that only one action is declared
    if(np.sum(action > -1) != 1):
#        print('ERROR 0')
        return returnInvalidOutput(board, players, controlVariables, availableActions)
    
    # Check that call and raise amounts are valid
    if( (action[1] > -1) ):
        if( (action[1] != callAmount) and \
                not (action[1] >= raiseMinMax[0] and action[1] <= raiseMinMax[1]) ):
#            print('ERROR 1')
            return returnInvalidOutput(board, players, controlVariables, availableActions)
        
    # Check that stacks are not negative
    if(np.any(stacks < 0)):
#        print('ERROR 3')
        return returnInvalidOutput(board, players, controlVariables, availableActions)

    # Player folds
    if(actionToExecute == 0):
#        print('* * * * * PLAYER FOLDS * * * * * *')
        controlVariables, availableActions = setGameEndState(controlVariables, availableActions, 
                                                             secondPlayerIdx)
        players, board = moveBetsToPot(players, board)
        players, board = movePotToPlayer(players, secondPlayerIdx, board)
        players = setHasPlayerActed(players, actingPlayerIdx)
        
        return board, players, controlVariables, availableActions
    
    # Player either calls or raises
    amount = action[actionToExecute]
    players = setBet(players, amount, actingPlayerIdx)

    # Check that stacks are not negative after the action
    if(np.any(stacks < 0)):
#        print('ERROR')
        return returnInvalidOutput(board, players, controlVariables, availableActions)
    
    players = setHasPlayerActed(players, actingPlayerIdx)
    numPlayersActed = getNumPlayersActed(players)        
    bets = getBets(players)
    players = setActingPlayerIdx(players, secondPlayerIdx)
    
    # Check if both players have acted and the bets are equal -> next betting round or showdown
    if( (numPlayersActed >= 2) and (bets[1]-bets[0] == 0) ):
        players, board = moveBetsToPot(players, board)
        board, players, controlVariables = initNextBettingRound(board, players, controlVariables)
        bettingRound = getBettingRound(controlVariables)
        
        # If all-in situation then go to the showdown
        if(np.min(stacks) == 0): bettingRound = 4
    
        # Showdown
        if(bettingRound > 3):
#            print('* * * * SHOWDOWN * * * * ')
            cardsBoard = getBoardCards(board)
            cardsPlayer0 = np.concatenate((getPlayerHoleCards(players,0), cardsBoard))
            cardsPlayer1 = np.concatenate((getPlayerHoleCards(players,1), cardsBoard))
            
            ranks = np.zeros(2, dtype=np.uint64)
            ranks[0] = evaluate(cardsPlayer0, ranks_7cards, LUT_nChooseK_7cards)
            ranks[1] = evaluate(cardsPlayer1, ranks_7cards, LUT_nChooseK_7cards)
            
            winPlayerIdx = np.argmin(ranks)
            
            # Tie
            if(ranks[0] == ranks[1]):
                winPlayerIdx = -1
            
            players, board = movePotToPlayer(players, winPlayerIdx, board)
            controlVariables, availableActions = setGameEndState(controlVariables, availableActions,
                                                                 winPlayerIdx)

            return board, players, controlVariables, availableActions

    availableActions = getAvailableActions(players, board)

    return board, players, controlVariables, availableActions













