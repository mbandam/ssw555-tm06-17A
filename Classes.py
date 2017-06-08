def formatId(id):
    return id.strip("@")

class TagLine(object):
    def __init__(self, level, tag, args):
        self.level = level
        self.tag = tag
        self.args = args

    def getString(self):
        return self.level + " " + self.tag + " " + self.args

class Person(object):
    def __init__(self, tagLines):
        self.tagLines = tagLines

    def getArgs(self, targetTag):
        for tagLine in self.tagLines:
            if tagLine.tag == targetTag:
                return tagLine.args

    def getIndiId(self):
        return formatId(self.getArgs("INDI"))

    def getName(self):
        return self.getArgs("NAME")

    def getSex(self):
        return self.getArgs("SEX")

    def getBirthDate(self):
        nextIsBirthDate = False
        for tagLine in self.tagLines:
            if tagLine.tag == 'BIRT':
                nextIsBirthDate = True
                continue
            if nextIsBirthDate:
                return tagLine.args

    def getFamId(self):
        famId = None
        for tagLine in self.tagLines:
            if tagLine.tag == 'FAMS':
                return tagLine.args
            if tagLine.tag == 'FAMC':
                famId = tagLine.args
        return formatId(famId)

    def getOptionalTags(self):
        primaryTags = ['INDI', 'NAME', 'SEX', 'BIRT']
        tags = []
        for tagLine in self.tagLines:
            if tagLine.tag not in primaryTags:
                tags.append(tagLine.getString())
        return tags

    def getJson(self):
        return {"indId": self.getIndiId(),
                "name": self.getName(),
                "birth": self.getBirthDate(),
                "sex": self.getSex(),
                "famId" : self.getFamId(),
                "tags": self.getOptionalTags()}

class Family(object):
    def __init__(self, tagLines):
        self.tagLines = tagLines

    def getArgs(self, targetTag):
        for tagLine in self.tagLines:
            if tagLine.tag == targetTag:
                return tagLine.args

    def getFamId(self):
        return formatId(self.getArgs("FAM"))

    def getDate(self, targetTag):
        foundTag = False
        for tagLine in self.tagLines:
            if tagLine.tag == targetTag:
                foundTag = True
                continue
            elif foundTag and tagLine.tag == "DATE" and tagLine.level == "2":
                return tagLine.args

    def getMarriageDate(self):
        return self.getDate("MARR")

    def getDivorceDate(self):
        return self.getDate("DIV")

    def getHusbandId(self):
        return formatId(self.getArgs("HUSB"))

    def getWifeId(self):
        return formatId(self.getArgs("WIFE"))

    def getChildrenIds(self):
        childrenIds = []
        for tagLine in self.tagLines:
            if tagLine.tag == "CHIL":
                childrenIds.append(formatId(tagLine.args))
        return childrenIds

    def getJson(self):
        return {"famId": self.getFamId(),
                "marriageDate": self.getMarriageDate(),
                "divorceDate": self.getDivorceDate(),
                "husbandId": self.getHusbandId(),
                "wifeId": self.getWifeId(),
                "childrenIds": self.getChildrenIds()}