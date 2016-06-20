# Name:             Settings / control panel
# Description:      Control panel for debugging, testing, further dev, fun, etc.
# Section:

console = {
    # Enable or disable verbose logging to the console while Emma is running
    'verboseLogging': True,

    # Enable or disable "console mode," which allows a developer to execute Emma's modules and functions one-by-one at the Python command line
    # todo: write support for this
    'consoleMode': False
}

database = {
    # Specify what file Emma stores her information in (For now, this database must be pre-formatted. Emma will support generating new database files in a future update)
    'path': './emma.db'
}

tumblr = {
    # Set the username of the Tumblr account that Emma communicates with
    'username': 'emmacanlearn',

    # Enable or disable posting on Tumblr (So that Emma doesn't post a bunch of garbage while we debug or work on new features)
    'enablePosting': False,

    # Enable or disable Tumblr post previews, which give a rough idea of what a tumblr post will look like in the terminal
    'enablePostPreview': True,

    # Enable or disable deletion of asks after we're done with them
    'deleteAsks': False
}