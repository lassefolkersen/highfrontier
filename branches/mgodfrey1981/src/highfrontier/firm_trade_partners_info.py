import fast_list
import merchant
import os
import global_variables
import sys
import string
import pygame
import datetime
import math
import company
import primitives
import random
import time

class firm_trade_partners_info():
    """
    Subview of the firm view. Shows a list of past trading transactions for the firm.
    """
    def __init__(self,solar_system_object,action_surface):
        self.solar_system_object_link = solar_system_object
        self.rect = pygame.Rect(50,50,700,500)
        self.action_surface = action_surface
        


    def create(self):
        """
        The creation function. Doesn't return anything, but saves self.window_transactions variable and renders using the self.renderer. 
        """
        
        firm_selected = self.solar_system_object_link.firm_selected
        if isinstance(firm_selected,company.merchant):
            location_list = [firm_selected.from_location, firm_selected.to_location]
            
        else:
            location_list = [firm_selected.location]

        
        transactions = {}
        for k, location_instance in enumerate(location_list):
            
            market = location_instance.market
            for i, resource in enumerate(market["transactions"]):
                
                for j, transaction in enumerate(market["transactions"][resource]):
                    
                    date = transaction["date"]
                    if transaction["buyer"] is not None:
                        buyer = transaction["buyer"].name
                    else:
                        buyer = None
                    if transaction["seller"] is not None:
                        seller = transaction["seller"].name
                    else:
                        seller = None
                    price = transaction["price"]
                    #print "The price is of class " + str(price.__class__)
                    quantity = transaction["quantity"]
                    if firm_selected.name in [buyer,seller]:
                        transactions[(i+1)*(j+1)*(k+1)] =  {"date":date,"buyer":buyer,"seller":seller,"price":price,"quantity":quantity}
#                        print "no this was it"
#                        print location_instance.name + " name of market"
#                        print "for the " + str(i) + " resource which is " + str(resource)
#                        print "for the " + str(j) + " transaction which is " + str(transaction)
                    
                        
#        print "transaction keys " + str(transactions.keys())
#        print "transactions: " + str(transactions)
        self.fast_list = fast_list.fast_list(
            self.action_surface, 
            transactions, 
            rect = self.rect,
            sort_by = "date",
            column_order = ["date","buyer","seller","price","quantity"])
    def receive_click(self,event):
        self.fast_list.receive_click(event)

        
        
