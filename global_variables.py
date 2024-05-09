
import datetime
import pygame
import time
import market_decisions
import os
pygame.font.init()

# variables that are "meta-gamespecific" ie. that should not follow a savegame
window_size=(1024,768)

flat_earth_scaling_start = 360

fullscreen = False # if the game should run in fullscreen
action_window_size = window_size # but corrected by initializing the command box, which changes this variable to the size of the action_window (ie. without the commandbox)
max_number_of_companies = 500 #hard upper limit on companies
persons_per_company = 1200000   #upper limit on the number of companies relative to the number of people in the universe
max_transactions_tracked = 100 #the max number of tracked transaction in a market.
max_letters_in_company_names = 32

courier_font = pygame.font.Font(os.path.join("fonts","CRYSRG__.TTF"), 11) #some fonts
standard_font = pygame.font.SysFont(os.path.join("fonts","freesansbold.ttf"), 13, bold=False, italic=False) #some fonts
standard_font_small= pygame.font.Font(os.path.join("fonts","freesansbold.ttf"),10)
standard_font_small_bold = pygame.font.Font(os.path.join("fonts","freesansbold.ttf"),10)
standard_font_small_bold.set_bold(True)
max_stepback_history_size = 10 # how many steps back we can use the "back" key
market_decisions = market_decisions.market_decisions() #this is the class of market decisions that should be globally available.




# variables that are "gamespecific" ie. that should follow a savegame. These are loaded into the solar system instance on startup and are here merely as defaults.
effectuate_growth = False#if False all growth calculations are performed, but are not actually applied to population numbers. Useful for equilibrizing the markets first.
effectuate_migration = False #if False all migration calculations are performed, but are not actually applied to population numbers. Useful for equilibrizing the markets first.
start_date = datetime.date(time.localtime()[0],time.localtime()[1],time.localtime()[2])
step_delay_time = 100 # 10-500  - how much delay (in miliseconds, I think) there should be before initiating the next iteration. This can be changed from the settings within the game
technology_research_cost = 1000 #a variable specifying how much technology costs (in fact it is conversion factor for distance in the technology tree to research points) (100000 is pretty fast)
gas_change_multiplier = 100.0 # (100.0)a variable modifying how much a given gas emmision changes atmospheric gas pressure. It divides with the ton_per_pa_here, so a higher number means faster atmosphere change with less emission
mineral_deposit_size_multiplier = 100.0 # (100.0) a variable modifying how much a given mining intensity modifies mineral reserves. It is divided by the calculated deposit reduction, so a higher number means more deposits and slower reduction
