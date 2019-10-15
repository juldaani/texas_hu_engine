#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 16 13:02:17 2019

@author: juho
"""

import numpy as np
from numba import jit, prange

from texas_hu_engine.engine_numba import initGame, executeAction, getGameEndState


class GameState:
    
    def __init__(self, boardStates, playerStates, controlVariables, availableActions, validMask=None,
                 validMaskPlayers=None):
        self.boards = boardStates
        self.players = playerStates
        self.controlVariables = controlVariables
        self.availableActions = availableActions
        
        if(validMask is None):
            validMask = np.ones(len(boardStates), dtype=np.bool_)
        if(validMaskPlayers is None):
            validMaskPlayers = np.ones(len(playerStates), dtype=np.bool_)

        self.validMask = validMask
        self.validMaskPlayers = validMaskPlayers


def initRandomGames(nGames, seed=-1):
    boards, players, controlVariables, availableActions, initStacks = initGamesWrapper(nGames, seed=seed)
    
    return GameState(boards, players, controlVariables, availableActions), initStacks


def executeActions(gameState, actionsToExecute):
    boards, players, controlVariables, availableActions, validMask, validMaskPlayers = \
        executeActionsWrapper(actionsToExecute, gameState.boards, gameState.players, 
                              gameState.controlVariables, gameState.availableActions)
    
    return GameState(boards, players, controlVariables, availableActions, validMask=validMask,
                     validMaskPlayers=validMaskPlayers)


@jit(nopython=True, fastmath=True)
def initGamesWrapper(nGames, seed=-1):
    if(seed != -1):
        np.random.seed(seed)
    
    boardsArr = np.zeros((nGames, 13), dtype=np.int32)
    playersArr = np.zeros((nGames*2, 8), dtype=np.int32)
    controlVariablesArr = np.zeros((nGames, 3), dtype=np.int16)
    availableActionsArr = np.zeros((nGames, 3), dtype=np.int64)
    initStacksArr = np.zeros((nGames, 2), dtype=np.int64)
    
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
        initStacksArr[i,:] = initStacks
        
    return boardsArr, playersArr, controlVariablesArr, availableActionsArr, initStacksArr
    

@jit(nopython=True, cache=True, fastmath=True)
def createActionsToExecute(amounts):
    """
    Create action that can be fed into holdem engine.
    
    Returns numpy array of actions
    
    amount - call or raise amount, if -1 then fold
    """
    
    actionsToExec = np.zeros((len(amounts),2), dtype=np.int64) - 1

    for i in range(len(amounts)):
        actionsToExec[i,1] = amounts[i]

        if(amounts[i] < 0):     # This means fold
            actionsToExec[i,0] = 1
            actionsToExec[i,1] = -1
    
    return actionsToExec


@jit(nopython=True, fastmath=True)
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
        
        validMask[i] = True
        validMaskPlayers[i*2:i*2+2] = True
        
        boards[i,:], players[i*2:i*2+2,:], controlVariables[i,:], availableActions[i,:] = \
            executeAction(curBoard, curPlayers, curControlVars, curAction, curAvailableActions)
    
    return boards, players, controlVariables, availableActions, validMask, validMaskPlayers




