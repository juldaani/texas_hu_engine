#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 23 11:36:11 2019

@author: juho
"""

import numpy as np
from numba import jit

from texas_hu_engine.wrappers import initRandomGames, executeActions, createActionsToExecute



class GameDataContainer:
    
    def __init__(self, nGames):
        self.__indexes = [[] for i in range(nGames)]
        self.__boardsData, self.__playersData, self.__controlVariablesData, \
            self.__availableActionsData = None, None, None, None
    
    def flattenPlayersData(self, playersData):
        flattenedData = np.zeros((int(len(playersData)/2), 
                                  playersData.shape[1]*2), dtype=playersData.dtype)
        flattenedData[:,:playersData.shape[1]] = playersData[::2]
        flattenedData[:,playersData.shape[1]:] = playersData[1::2]
        
        return flattenedData
        
    def addData(self, gameStates):
        validIndexes = np.nonzero(gameStates.validMask)[0]
        nDataPts = 0
        
        if(self.__boardsData is None):
            self.__boardsData = gameStates.boards[validIndexes]
            self.__playersData = self.flattenPlayersData(gameStates.players)[validIndexes]
            self.__controlVariablesData = gameStates.controlVariables[validIndexes]
            self.__availableActionsData = gameStates.availableActions[validIndexes]
        else:
            nDataPts = len(self.__boardsData)
            self.__boardsData = np.row_stack((self.__boardsData, gameStates.boards[validIndexes]))
            self.__playersData = np.row_stack((self.__playersData, 
                                               self.flattenPlayersData(
                                                     gameStates.players)[validIndexes]))
            self.__controlVariablesData = np.row_stack((self.__controlVariablesData, 
                                                      gameStates.controlVariables[validIndexes]))
            self.__availableActionsData = np.row_stack((self.__availableActionsData, 
                                                      gameStates.availableActions[validIndexes]))
        
        dataIndexes = np.arange(len(validIndexes)) + nDataPts
        for gameIdx,dataIdx in zip(validIndexes,dataIndexes):
            self.__indexes[gameIdx].append(dataIdx)
        
    def getIndexes(self): return self.__indexes
    
    def getData(self): return {'boardsData': self.__boardsData,
                               'playersData': self.__playersData,
                               'availableActionsData': self.__availableActionsData,
                               'controlVariablesData': self.__controlVariablesData}
        

# %%
             
from texas_hu_engine.wrappers import GameState

            
N = 300

cont = GameDataContainer(N)
states = initRandomGames(N)

for i in range(100):
    
    tmp = np.arange(N).reshape((N,-1))
    states.availableActions[:] = tmp
    states.boards[:] = tmp
    states.controlVariables[:] = tmp
    states.players[:] = np.tile(tmp.flatten(), (2,1)).T.reshape((N*2,-1))
#    states.validMask = np.array([1,0,1])
#    states.validMask = np.array([1,0,0])
    states.validMask = np.random.randint(0,2,N)
    
    cont.addData(states)


# %%

#cont.indexes
#cont.boardsData
#cont.playersData
#cont.availableActionsData
#cont.controlVariablesData

for i in range(N):
    #i = 1
    idx = cont.getIndexes()[i]
#    len(idx)
    assert np.allclose(cont.getData()['boardsData'][idx], i)
    assert np.allclose(cont.getData()['playersData'][idx], i)
    assert np.allclose(cont.getData()['availableActionsData'][idx], i)
    assert np.allclose(cont.getData()['controlVariablesData'][idx], i)

# %%




asd = GameDataContainer.flattenPlayersData(states.players)

playersData = states.players

tmpPlayersData = np.zeros((int(len(playersData)/2), 
                           playersData.shape[1]*2), dtype=playersData.dtype)
tmpPlayersData[:,:playersData.shape[1]] = playersData[::2]
tmpPlayersData[:,playersData.shape[1]:] = playersData[1::2]



boards = states.boards

tmpPlayers = states.players

asd = np.zeros((len(boards), tmpPlayers.shape[1]*2), dtype=tmpPlayers.dtype)

asd[:,:tmpPlayers.shape[1]] = tmpPlayers[::2]
asd[:,tmpPlayers.shape[1]:] = tmpPlayers[1::2]

tmpPlayers.shape
asd.shape










