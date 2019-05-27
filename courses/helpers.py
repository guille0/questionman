def checkboxParse (data):
    'Turns POST info received from a checkbox into a Boolean'
    if data:
        return True
    else:
        return False

def cleanCSV (string):
    '''Given a string separated by commas
    returns it with proper spacing between the elements and no empty fields'''
    l = string.split(',')
    cleanL = [item.strip() for item in l]
    while '' in cleanL:
        cleanL.pop(cleanL.index(''))
    return ", ".join(cleanL)