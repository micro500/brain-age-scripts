# brain-age-scripts

##Twitch Plays

You will need the following:
- python
-- py-yaml package
-- irc package (https://github.com/jaraco/irc)
- desmume svn version

You can get the python packages installed with pip.

    pip install yaml
    pip install irc

Once you get desmume running get to where you are about to enter a 7 in calculations x 100. Set savestate slot 4 there - the verification script expects that. 

Each python file has some built in testing. `brain_bot.py` is the main script. Run that and it will connect to irc and start the scraping process. 

`settings.yaml` has the irc connection settings. I found that it was necessary to use a specific irc server ip. You may want to have a chat profile for the bot or use someone else's oauth key. Of course for testing any irc server and channel will do.

The verification lua is written to `submission.lua`. Load that script in desmume to connect desmume. Each time a new block of text is checked the lua file gets overwritten and will restart. To verify faster, toggle turbo mode on. The lua file will write the test result to a file that the python script reads to get the result.

Each line of chat gets some automatic checks against a bad word list but there is also a human check. When the irc bot gets its text to verify it generates lua and dsm for that text. It also writes the text to the console with a prompt for the operator. The operator can then accept or reject the text. This human check will be timed out after a configurable length of time. On a timeout the text is rejected by default though this can be changed to accept for testing.

If the human test and desmume tests both pass then that screen is published. A dsm file is written in the `publish` directory. That dsm file is what to play to draw the block of text.

To shut down the bot cleanly, type `exit` at the human test prompt. Because of how the threads and input streams are set up your terminal is likely to lock if you break with Ctrl-C.

