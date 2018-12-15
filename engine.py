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


# Player state ................................................................
def getStacks(playerStates): return playerStates[:,2]

def getBets(playerStates): return playerStates[:,3]

def setBet(playerStates, amount, playerIdx):
    playerStates[playerIdx,2] -= amount
    playerStates[playerIdx,3] += amount
    return playerStates

def setActingPlayer(playerStates, playerIdx): 
    otherPlayerIdx = np.abs(playerIdx-1)
    playerStates[playerIdx,6] = 1
    playerStates[otherPlayerIdx,6] = 0
    return playerStates

# Board state .................................................................
def getSmallBlindAmount(boardState): return boardState[1]

def getBigBlindAmount(boardState): return boardState[2]



def initGame(boardCards, smallBlindPlayerIdx, smallBlindAmount, stacks, holeCards):
    
    # Set board
    board = np.zeros(13, dtype=np.int)
    board[0] = 0                    # Pot
    board[1] = smallBlindAmount     # Small blind
    board[2] = smallBlindAmount*2   # Big blind
    board[3:8] = 0                  # Visible board cards
    board[8:] = boardCards          # Board cards
    
    # Set players
    players = np.zeros((2,8), dtype=np.int)
    players[:,:2] = holeCards       # Hole cards
    players[:,2] = stacks           # Stacks
    players[:,3] = 0                # Bets
    players[smallBlindPlayerIdx,4] = 1      # Set small blind for the player
    bigBlindPlayerIdx = np.abs(smallBlindPlayerIdx-1)
    players[bigBlindPlayerIdx,5] = 1        # Set big blind for the player
    players = setActingPlayer(players, smallBlindPlayerIdx)  # Small blind acts first on the preflop in heads up
    players[:,7] = 0                # Has player acted?
    
    # Set game control variables
    controlVariables = np.zeros(3, dtype=np.int)
    controlVariables[0] = 0         # Betting round
    controlVariables[1] = 0         # Game end state
    
#    pot = 0
#    bets = np.array([0,0])
#    numPlayersActed = 0
#    gameEndState = 0
#    bettingRound = 0    # 0 = pre-flop, 1 = flop, 2 = turn, 3 = river
#    boardCardsVisible = np.zeros(5, dtype=np.int)-1
#    bigBlindAmount = smallBlindAmount*2
    
    # Check that both players have enough money
    if(not np.all(getStacks(players) >= getBigBlindAmount(board))):
        print('ERROR, not enough money')
        board = None
        players = None
        availableActions = None
        controlVariables = None
        return board, players, availableActions, controlVariables
    
#    smallBlindPlayerIdx = blindPositions[0]
#    bigBlindPlayerIdx = blindPositions[1]
    
    # Set bets
    players = setBet(players, getSmallBlindAmount(board), smallBlindPlayerIdx)
    players = setBet(players, getBigBlindAmount(board), bigBlindPlayerIdx)
    
#    stacks[smallBlindPlayerIdx] -= smallBlindAmount
#    bets[smallBlindPlayerIdx] += smallBlindAmount
#    stacks[bigBlindPlayerIdx] -= bigBlindAmount
#    bets[bigBlindPlayerIdx] += bigBlindAmount
    
    # Small blind acts first on the preflop in heads up
#    actingPlayerIdx = smallBlindPlayerIdx
    
    # Available actions
    availableActions = np.zeros(4, dtype=np.int)
    availableActions[0]
    
    bets = getBets(players)
    stacks = getStacks(players)
    bigBlindAmount = getBigBlindAmount(board)
    callAmount = np.abs(bets[0]-bets[1])
    maxRaiseAmount = np.min(stacks)
    raiseMinMax = np.array([min(max(callAmount+bigBlindAmount,callAmount*2), maxRaiseAmount), 
                            maxRaiseAmount])   # Max raise is all-in
    if(maxRaiseAmount < callAmount): raiseMinMax[:] = -1
    
    
    callAmount = getSmallBlindAmount(board)
    maxRaiseAmount = np.min(getStacks(players))
    raiseMinMax = np.array([min(callAmount+bigBlindAmount, maxRaiseAmount), maxRaiseAmount])   # Max raise is all-in
    if(maxRaiseAmount == callAmount): raiseMinMax[:] = -1
    
    return pot, bets, stacks, bigBlindAmount, numPlayersActed, gameEndState, \
        bettingRound, boardCardsVisible, actingPlayerIdx, callAmount, raiseMinMax




# %%

# "Static" variables (over single round)
tmpCards = np.random.choice(52, size=9, replace=0)
boardCards = tmpCards[:5]
holeCards = np.array([tmpCards[5:7],tmpCards[7:]])
smallBlindPlayerIdx = 1     # Which player is small blind?
#blindPositions = np.random.choice(2, size=2, replace=0)     # 1st index = small blind player
smallBlindAmount = 4

# "Nonstatic" variables, these are modified by the engine
stacks = np.array([smallBlindAmount*8+2,smallBlindAmount*6+5])



# %%



pot, bets, stacks, bigBlindAmount, numPlayersActed, gameEndState, bettingRound, \
    boardCardsVisible, actingPlayerIdx, callAmount, raiseMinMax = initGame(blindPositions, 
                                                                           smallBlindAmount, stacks)

# %%
    
# In 'action' 
#   1st index is fold
#   2nd is call amount
#   3rd is raise amount. 
# Only one action can be declared, for instance, [-1,-1, 25] means raise to 25.

#action = np.array([-1,-1,raiseMinMax[1]])
action = np.array([-1,callAmount,-1])


pot, bets, stacks, bigBlindAmount, numPlayersActed, gameEndState, bettingRound, \
    boardCardsVisible, actingPlayerIdx, callAmount, raiseMinMax = \
    executeAction(pot, bets, stacks, bigBlindAmount, numPlayersActed, gameEndState, 
                  bettingRound, boardCardsVisible, actingPlayerIdx, callAmount, raiseMinMax, action)
    
    
    
    

# %%

def executeAction(pot, bets, stacks, bigBlindAmount, numPlayersActed, gameEndState, 
                  bettingRound, boardCardsVisible, actingPlayerIdx, callAmount, raiseMinMax, action):
    
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
        gameEndState = 1
        pot = -1
        numPlayersActed = -1
        nextPlayerIdx = -1
        raiseMinMax[:] = -1
        callAmount = -1
        stacks[secondPlayerIdx] += np.sum(bets)
        bets[:] = -1
        print('* * * * * PLAYER FOLDS * * * * * *')
        # TODO: return stuffs
        return 666
        
    
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
























