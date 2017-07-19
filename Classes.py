import Domain
import pymongo
from prettytable import PrettyTable
from datetime import datetime


class TagLine(object):
    def __init__(self, level, tag, args):
        self.level = level
        self.tag = tag
        self.args = args

    @classmethod
    def parse(cls, string):
        split = string.split()
        level = split[0]
        tag = split[1]
        count = 2
        args = ''
        while len(split) > count:
            if (count + 1) is not len(split):
                args += split[count] + ' '
            else:
                args += split[count]
            count += 1
        return cls(level, tag, args)

    def getString(self):
        return self.level + " " + self.tag + " " + self.args


class TagList(object):
    def __init__(self, tagLines):
        self.tagLines = tagLines

    @classmethod
    def fromJson(cls, jsonTags):
        tags = []
        for tag in jsonTags:
            tags.append(TagLine.parse(tag))
        return cls(tags)

    def getTags(self):
        tags = []
        for tagLine in self.tagLines:
            tags.append(tagLine.getString())
        return tags

    def addTag(self, tagLine):
        self.tagLines.append(tagLine)

    def getArg(self, targetTag):
        for tagLine in self.tagLines:
            if tagLine.tag == targetTag:
                return tagLine.args

    def getArgs(self, targetTag):
        args = []
        for tagLine in self.tagLines:
            if tagLine.tag == targetTag:
                args.append(tagLine.args)
        return args


class Person(TagList):
    def getIndiId(self):
        return formatId(self.getArg("INDI"))

    def getName(self):
        return self.getArg("NAME").replace("/", "")

    def getLastName(self):
        return self.getName().split()[-1].replace("/", "")

    def getSex(self):
        return self.getArg("SEX")

    def getBirthDate(self):
        nextIsBirthDate = False
        for tagLine in self.tagLines:
            if tagLine.tag == 'BIRT':
                nextIsBirthDate = True
                continue
            if nextIsBirthDate:
                return tagLine.args

    def getDeathDate(self):
        nextIsDeathDate = False
        for tagLine in self.tagLines:
            if tagLine.tag == 'DEAT':
                nextIsDeathDate = True
                continue
            if nextIsDeathDate:
                return tagLine.args

    def getSpousalFamilyIds(self):
        famIds = []
        for famId in self.getArgs('FAMS'):
            famIds.append(formatId(famId))
        return famIds

    def getChildFamilyId(self):
        return formatId(self.getArg('FAMC'))

    def getFamId(self):
        famId = None
        for tagLine in self.tagLines:
            if tagLine.tag == 'FAMS':
                return tagLine.args
            if tagLine.tag == 'FAMC':
                famId = tagLine.args
            if tagLine.tag == 'FAM' and famId is None:
                famId = tagLine.args
        return formatId(famId)

    def getJson(self):
        return {"indId": self.getIndiId(),
                "name": self.getName(),
                "birth": self.getBirthDate(),
                "death": self.getDeathDate(),
                "sex": self.getSex(),
                "famId": self.getFamId(),
                "tags": self.getTags()}


class Family(TagList):
    def getFamId(self):
        return formatId(self.getArg("FAM"))

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
        return formatId(self.getArg("HUSB"))

    def getWifeId(self):
        return formatId(self.getArg("WIFE"))

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
                "childrenIds": self.getChildrenIds(),
                "tags": self.getTags()}


class Repository(object):
    def __init__(self, host, port, gedcomFile=None):
        # Database config
        self.dbClient = pymongo.MongoClient("localhost", 27017)
        self.db = self.dbClient.ssw555_tm06_17A
        self.dbClient.drop_database(self.db)

        # Declare buckets
        self.peopleDb = self.db.people
        self.familyDb = self.db.families
        if gedcomFile is not None:
            self.add(gedcomFile)

    def add(self, gedcomFile):
        print("Writing entries from '" + gedcomFile + "' to database...")
        # Read in all of the lines from the GEDCOM file
        with open(gedcomFile) as file:
            lines = [line.rstrip("\n") for line in file.readlines()]
        # Store all lines as individuals and families in the database
        validTags = Domain.validTags()
        tags = []
        currentId = None  # GEDCOM unique ID
        currentType = None  # INDI or FAM
        for line in lines:
            tokens = line.split(" ", maxsplit=2)
            level = tokens[0]
            tag = tokens[1]

            args = ""
            if len(tokens) > 2:
                args = tokens[2]

            # For INDI and FAM, ID comes before the tag,
            # so swap the 'args' and 'tag' variables
            if args == "INDI" or args == "FAM":
                args, tag = tag, args

            levelTagPair = (level + " " + tag)

            """
            Insert the current individual or family once we've reached either:
                - a new individual
                - a new family
                - the end of the GEDCOM file
            """
            if levelTagPair == "0 INDI" or levelTagPair == "0 FAM" or line == lines[len(lines) - 1]:
                if line == lines[len(lines) - 1]:
                    if levelTagPair not in validTags:
                        print("Ignoring '{}': unrecognized level+tag combination".format(line))
                    else:
                        tags.append(TagLine(level, tag, args))
                if len(tags) > 0:
                    if currentType == "INDI":
                        self.peopleDb.insert_one(Person(tags).getJson())
                    elif currentType == "FAM":
                        self.familyDb.insert_one(Family(tags).getJson())
                    else:
                        print("Error: Current entity not of type INDI or FAM")
                        currentId = None
                        currentType = None
                currentId = args
                currentType = tag
                tags = []

            if line != lines[len(lines) - 1]:
                if not currentId:
                    print("Ignoring '{}': haven't started individual or family".format(line))
                elif levelTagPair not in validTags:
                    print("Ignoring '{}': unrecognized level+tag combination".format(line))
                else:
                    tags.append(TagLine(level, tag, args))

    def getPeople(self):
        people = []
        for json in self.peopleDb.find({}):
            people.append(Person.fromJson(json['tags']))
        return people

    def getFamilies(self):
        families = []
        for json in self.familyDb.find({}):
            families.append(Family.fromJson(json['tags']))
        return families

    def getPerson(self, personId):
        return Person.fromJson(self.peopleDb.find_one({'indId': personId})['tags'])

    def getFamily(self, familyId):
        return Family.fromJson(self.familyDb.find_one({'famId': familyId})['tags'])

    def getFamilyId(self, individualId):
        return self.peopleDb.find_one({'indId': individualId})['famId']

    def getMarriageDate(self, familyId):
        return self.peopleDb.find_one({'famId': familyId})['marriageDate']

    def getDivoreceDate(self, familyId):
        return self.peopleDb.find_one({'famId': familyId})['divorceDate']


def formatId(id):
    if id is None:
        return
    return id.replace("@", "")
