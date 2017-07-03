from datetime import datetime

def parseDate(string):
    if string is None:
        return
    return datetime.strptime(string, '%d %b %Y')
