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

##Compiling

Run `compileMovie.py` to compile the firmware movie. Give the firmware name on the command line. Do not forget to use quotes if there are spaces: `python compileMovie.py "fw name"`. The output will be named `brain_age_firmware.dsm`.

##Streaming

There are a few options for streaming

### `stream.py`

This was set up to run multiple .dsm files one after another. The first command line arg is the stream and the rest are dsm files.

### `ds_stream.py`

If run from the command line the result shold be identical to `stream.py`. However the code has been refactored to be easier to work with and reuse.

### `stream_brain_age.py`

This is intended to be the main streaming program. The command line arguments are the serial interface and the file list of dsm files. It is assumed that the `tas_projects` repo is cloned next to this one. The default is the `file_list.txt` file in there and the files listed will be considered to be relative to that directory. A different file can be specified so that you can have multiple files ready for each incentive scenario and pick the final one at the last minute. For example: `python stream_brain_age.py serial_port ../tas_projects/AGDQ2016/finished_images/twich_helix_file_list.txt`

This script supports a special entry in the file list for twitch images. When the script reaches a `<twitch>` entry it begins the sequence for twitch input. The irc bot should be run completely separately in a separate terminal. This script will monitor the `publish` directory to determine when twitch input is ready. When a new input file is published there it will be streamed. Until then empty controller input is streamed. After the twitch image the script will move on to the next file in the file list.

Example `file_list.txt`:

    ../AGDQ2016.dsm
    input/images/clippy_6.dsm
    input/fake/fake_0.dsm
    <twitch>
    input/fake/fake_11.dsm
    input/fake/fake_0.dsm
    input/fake/fake_40.dsm

To make sure the text in the twitch chat image was actually sent after reaching that point, you need to hit no twice in the irc bot console. After that the next set of text will be recent.

