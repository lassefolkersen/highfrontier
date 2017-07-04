# High Frontier

The goal of High Frontier is a civilization-like game, which uses more realistic modelling of economy, climate, research and migration. Uniquely this game starts today - the initiation date of a game is todays date and the existing world is the world as we know it today, complete with cities and countries and people. The aim from there - that is whatever the player thinks the aim is for the world. Developing of the underdeveloping world, action against climate changes, expansion into the rest of the solar system, or just racking in a lot of money. 

The game is currently somewhat playable. Working features include: 
- Google-earth-like map view of the Earth and all other bodies of the solar system. Complete solar system model with accurate orbital data. 
- Underlying economical model based on agents (countries or companies) buying and selling goods thereby setting price. Genetic/evolutionary algorithm copies variations of best agents thus continuously perfecting the AI decisions 
- Infinitly expandable research tree based on automatic technology-name generation by random selction from lists of tech-buzz-words (same way as it happens in the real world) 
- climate model, including the feature of changing sea levels based on topographical maps of the planet in question. Nice for terraforming a northern ocean on Mars. Less nice for rampant greenhouse-effects on earth (allows checking if your country should worry more or less about carbon emission in real life as well)


## Installation

These pre-[compiled python-binaries](https://sourceforge.net/projects/highfrontier/files/?source=navbar) will show the intro, but don't work much further than that. There's also an ubuntu debian image there, that I didn't test.

Setting up from source is possible however. On windows it was a matter of finding and installing:
* [Python 2.7](https://www.python.org/downloads/)
* [Pygame](http://www.pygame.org/download.shtml), just the latest version - I used the one called pygame-1.9.1.win32-py2.7.msi.
* Python Image Module: [PIL](http://www.pythonware.com/products/pil/), just the latest version - I used the one called Python Imaging Library 1.1.7 for Python 2.7


On ubuntu it was also possible. These were the needed steps:
* [Python 2.7](https://www.python.org/downloads/) - but came pre-installed of course.
* Pygame:
```
wget http://www.pygame.org/ftp/pygame-1.9.1release.tar.gz
tar -zxvf pygame-1.9.1release.tar.gz
python setup.py
```
Then I had some problems with a video-link that [stack-overflow](https://stackoverflow.com/a/14026861) solved for me.
* PIL - just using 
```
sudo apt-get install python-imaging
```




