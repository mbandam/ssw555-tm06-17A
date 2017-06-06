class TagLine(object):
    def __init__(self, level, tag, args):
        self.level = level
        self.tag = tag
        self.args = args

    def getString(self):
        return self.level + " " + self.tag + " " + self.args

    def getTag(self):
        return self.tag

    def getArgs(self):
        return self.args


class Person(object):
    def __init__(self, tags):
        self.tags = tags

    def getName(self):
        for tag in self.tags:
            if TagLine.getTag(tag) == 'NAME':
                return TagLine.getArgs(tag)

    def getSex(self):
        for tag in self.tags:
            if TagLine.getTag(tag) == 'SEX':
                return TagLine.getArgs(tag)

    def getBirthDate(self):
        nextIsBirthDate = False
        for tag in self.tags:
            if TagLine.getTag(tag) == 'BIRT':
                nextIsBirthDate = True
                continue
            if nextIsBirthDate:
                return TagLine.getArgs(tag)

    def getFamId(self):
        famId = None
        for tag in self.tags:
            if TagLine.getTag(tag) == 'FAMS':
                return TagLine.getArgs(tag)
            if TagLine.getTag(tag) == 'FAM':
                return TagLine.getArgs(tag)
            if TagLine.getTag(tag) == 'FAMC':
                famId = TagLine.getArgs(tag)
        return famId

    def getOptionalTags(self):
        primaryTags = ['NAME', 'SEX', 'BIRT', 'FAMC']
        tags = []
        for tag in self.tags:
            if tag not in primaryTags:
                tags.append(TagLine.getString(tag))
        return tags

    def getJson(self, docId):
        return {"_id": docId,
                "name": self.getName(),
                "birth": self.getBirthDate(),
                "sex": self.getSex(),
                "famId" : self.getFamId(),
                "tags": [self.getOptionalTags()]}
