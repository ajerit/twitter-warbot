# Twitter-Warbot
Python script that implements the simple Twitter Warbot that chooses elements from a list and selects a winner until there is just one element left.

* Player list is stored in Postgresql DB, uploaded from a text file with the upload_name.py script. DB stores data like status, win count, death and select probability per player.

* The Bot selects two items from the DB, based on the select probability, and then chooses one to "die" based on death probability.

* Using PIL library a image is generated with all the items on DB with their current status ("Dead" items are shown with red strikethrough.

* The generated image and the corresponding selected items are sent to the Twitter API to be posted by the Bot account. 

* Config.py contains helper methods to connect to DB, twitter API and other services

* csibot.sql contains the schema for the DB
