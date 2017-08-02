from datetime import datetime

def parseDate(string):
    if string is None:
        return
    return datetime.strptime(string, '%d %b %Y')

def formatDate(date):
    if date is None:
        return "NA"
    else:
        return datetime.strptime(date.replace(" ", "/"), "%d/%b/%Y").strftime('%Y-%m-%d')

def formatValue(value):
    if value is None or not value:
        return 'NA'
    else:
        return value