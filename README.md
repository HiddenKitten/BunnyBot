# BunnyBot

This is the code for a bot made specifically for the MeeMTeam discord server.
This is also probably not the best example, if you're looking for how to do anything.

Under cogs/utils you can find some code for pinging several gameservers. 
I couldn't find a better example for pinging srb2kart, Just using the srb2 code alone resulted in mostly nonsense for the later values and I wasn't entirely certain what some of the values were, so this is the best I could manage. (if someone has proper documentation on srb2*kart* packets somewhere, please, send it my way!)
tf2 was done the way it was because struct.unpack doesn't directly support strings with unknown length, might try to rewrite it at some point to use struct, but right now it works.