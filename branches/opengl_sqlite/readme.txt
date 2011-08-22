what's going on here?

Highfrontier has a lot of potential as a game.  It features quite a
sophisticated simulation, and has an awful lot of data and research
that has already been gathered and implemented in that simulation.
Data consistency and error checking seem to be the major stumbling
blocks at the moment.  

The big problems are the data model and gui code.  I'm hacking at
those, to see if I can't build the game up from scratch, mostly like
the original, but much easier to understand and maintain thanks to a
consistent model-view-controller framework.  Consistent and thorough
exception-handling will make errors easier to track down, and reduce
the number of crashes.  A thorough set of unit tests should reduce
those crashes even further.

Rather than pickling and unpickling data, I've opted to use Python's
built-in sqlite3 interface.  Sqlite3 utilises advanced algorithms and
a well-known format for persistant storage, in an attempt to eliminate
the need for most in-code table scans.

The graphics could be updated from homebrew Pygame calls to an
established Gui library and OpenGL for rendering.  

Separation of concerns means that a change to the gui code won't
adversely affect the simulation code, and vice versa.  Since this
project is about building space cities, and not showcasing a homebrew
gui library, I hope these implementation decisions are acceptible.

