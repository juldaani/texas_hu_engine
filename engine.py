#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 22:26:05 2018

@author: juho
"""

import numpy as np


# %%

tmpCards = np.random.choice(52, size=9, replace=0)     # Board & both players hole cards
boardCards = tmpCards[:5]
playerCards = np.array([tmpCards[5:7],tmpCards[7:]])
