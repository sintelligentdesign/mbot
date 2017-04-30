# Testing Strings
useTestingStrings = False
testingStringType = 'simple'

testingStringsSimple = [
    u"The sky is blue.",
    u"Dogs are very fluffy!",
    u"I want to be your friend.",
    u"I love pickles!",
    u"The quick brown fox jumped over the lazy dog."
]

if testingStringType == 'simple':
    testingStrings = testingStringsSimple
elif testingStringType == 'fuzz':
    with open('utils/questions.txt', 'r') as file:
        testingStrings = '\n'.split(file)