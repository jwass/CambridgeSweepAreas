CambridgeSweepAreas
===================

This little project grew out of frustration in deciphering Cambridge, MA's
street sweeping schedule.  If you're a Cambridge resident and you're going to
be away from the city for some time, it's difficult to determine where to park
while you're away, unless you don't mind being ticketed and towed.

The city's 
[street cleaning schedule and routes page](http://www.cambridgema.gov/theworks/ourservices/streetcleaning/schedulesandroutes.aspx) links to a map displaying
the sweep areas.  The map has no labels.  In order to use the site you have
to keep open their map of the sweep areas, a labeled street map
(Openstreetmap, Google Maps, etc.) to find the actual road boundaries and the
web page containing the street sweep schedule.  

This script merges the street sweep boundaries with the city's street sweet
schedule.  The boundaries are from CodeForBoston's import of Cambridge's Open
Data.  The script downloads and parses the table from the website listed
above.

As a test, I used Pandas to pull the table and re-shuffle the data into the
desired format.
