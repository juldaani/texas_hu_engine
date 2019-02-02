#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 15:27:21 2019

@author: juho
"""

import mechanicalsoup



browser = mechanicalsoup.StatefulBrowser()
browser.open("http://www.cleverpiggy.com/nlbot")

submit = browser.get_current_page().find('input', id='text_amount')

browser.soup.select('bet_sizing')

browser.select_form()

browser['text_amount'] = 44




# %%



#browser.open("https://duckduckgo.com/")


# Fill-in the search form
browser.select_form('#search_form_homepage')
browser["q"] = "MechanicalSoup"
browser.submit_selected()


# Display the results
for link in browser.get_current_page().select('a.result__a'):
    print(link.text, '->', link.attrs['href'])







# %%









