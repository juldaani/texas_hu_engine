#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 16 13:02:17 2019

@author: juho
"""

import numpy as np
from numba import jit

from texas_hu_engine.engine_numba import initGame, executeAction, getGameEndState


@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def initGamesWrapper(nGames):
    
    boardsArr = np.zeros((nGames, 13), dtype=np.int32)
    playersArr = np.zeros((nGames*2, 8), dtype=np.int32)
    controlVariablesArr = np.zeros((nGames, 3), dtype=np.int16)
    availableActionsArr = np.zeros((nGames, 3), dtype=np.int64)
    
    for i in range(nGames):
        tmpCards = np.random.choice(52, size=9, replace=0)
        boardCards = tmpCards[:5]
        holeCards = np.zeros((2,2), dtype=np.int64)
        holeCards[0,:] = tmpCards[5:7]
        holeCards[1,:] = tmpCards[7:]
        smallBlindPlayerIdx = np.random.randint(0,high=2)
        smallBlindAmount = np.random.randint(1,high=100)
        initStacks = np.array([np.random.randint(smallBlindAmount*2, high=smallBlindAmount*1000 + \
                                                 np.random.randint(smallBlindAmount)), 
                               np.random.randint(smallBlindAmount*2, high=smallBlindAmount*1000 + \
                                                 np.random.randint(smallBlindAmount))])
        board, players, controlVariables, availableActions = initGame(boardCards, smallBlindPlayerIdx, 
                                                                      smallBlindAmount, initStacks.copy(), 
                                                                      holeCards)
    
        boardsArr[i,:] = board
        playersArr[i*2:i*2+2,:] = players
        controlVariablesArr[i,:] = controlVariables
        availableActionsArr[i,:] = availableActions
        
    return boardsArr, playersArr, controlVariablesArr, availableActionsArr
    

@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def createActionsToExecute(amounts):
    """
    Create action that can be fed into holdem engine.
    
    Returns numpy array of actions
    
    amount - call or raise amount, if -1 then fold
    """
    
    actionsToExec = np.zeros((len(amounts),2), dtype=np.int64) - 1

    for i in range(len(amounts)):
        actionsToExec[i,1] = amounts[i]

        if(amounts[i] < 0):
            actionsToExec[i,0] = 1
            actionsToExec[i,1] = -1
    
    return actionsToExec


@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def executeActionsWrapper(actionsToExec, boards, players, controlVariables, availableActions):
    
    validMask = np.zeros(len(boards), dtype=np.bool_)
    validMaskPlayers = np.zeros((len(boards)*2), dtype=np.bool_)
    
    for i in range(len(boards)):
        curBoard = boards[i]
        curPlayers = players[i*2:i*2+2,:]
        curControlVars = controlVariables[i]
        curAvailableActions = availableActions[i]
        curAction = actionsToExec[i]
    
        # Skip if the game has ended
        if(getGameEndState(curControlVars) == 1):
            continue
        
        # Skip if error has occured (-999 is code for error)
        if(curBoard[0] == -999):
            continue
        
        boards[i,:], players[i*2:i*2+2,:], controlVariables[i,:], availableActions[i,:] = \
            executeAction(curBoard, curPlayers, curControlVars, curAction, curAvailableActions)
    
        if(getGameEndState(controlVariables[i,:]) == 0):
            validMask[i] = True
            validMaskPlayers[i*2:i*2+2] = True
            
    return boards, players, controlVariables, availableActions, validMask, validMaskPlayers



# %%

nGames = 10000
boards, players, controlVariables, availableActions = initGamesWrapper(nGames)


# %%


amounts = availableActions[np.arange(len(boards)),np.random.randint(0,3,size=len(boards))]
#foldIdx = np.random.choice(len(amounts), size=int(0.05*len(amounts)), replace=0)
#amounts[foldIdx] = 23151234

actionsToExec = createActionsToExecute(amounts)

    

boards, players, controlVariables, availableActions, validMask, validMaskPlayers = \
    executeActionsWrapper(actionsToExec, boards, players, controlVariables, availableActions)



print(np.sum(validMask))
np.sum(controlVariables[:,-1] == -1) / len(controlVariables)










