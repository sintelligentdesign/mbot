# Name:             Settings / control panel
# Description:      Control panel for debugging, testing, further dev, fun, etc.
# Section:

debug = {
    # Enable or disable connecting to tumblr to fetch asks
    'fetchRealAsks': True,

    # If the above is false, supply a list of fake asks for Emma to read for testing and debugging
    'fakeAsks': [
        ("67890", "sharkthemepark", u"Hey babe! It's me, your mom! I just wanted to drop in and say how proud I am of you. Keep it up!"),
        ("12345", "hotpizzapie", u"I think you're fantastic. I don't know what I'd do without you."),
        ("67890", "nanopup", u"Hi Emma! I hope you're doing well. I like dogs because they are gay."),
        ("12345", "sparkplugiv", u"hi emma im gay"),
        ("67890", "sharkthemepark", u"I love nanopup they're so perfect so pretty so pure i love that dog")],

    'enableSleep': True
}

console = {
    # Enable or disable verbose logging to the console while Emma is running
    'verboseLogging': False,

    # Enable or disable a mode where you can directly chat with Emma without going through Tumblr
    'chatMode': False
}

database = {
    # Specify what file Emma stores her information in (For now, this database must be pre-formatted. Emma will support generating new database files in a future update)
    'path': './emma.db'
}

tumblr = {
    # Set the username of the Tumblr account that Emma communicates with
    'username': 'emmacanlearn',

    # Enable or disable posting on Tumblr (So that Emma doesn't post a bunch of garbage while we debug or work on new features)
    'enablePosting': True,

    # Enable or disable Tumblr post previews, which give a rough idea of what a tumblr post will look like in the terminal
    'enablePostPreview': True,

    # Enable or disable deletion of asks after we're done with them
    'enableAskDeletion': True
}