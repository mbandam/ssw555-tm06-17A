import Classes
import Domain
import pymongo
from prettytable import PrettyTable
from datetime import datetime

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

class Repository(object):
    def __init__(self, host, port):
        #Database config
        self.dbClient = pymongo.MongoClient("localhost", 27017)
        self.db = self.dbClient.ssw555_tm06_17A
        self.dbClient.drop_database(self.db)

        #Declare buckets
        self.peopleDb = self.db.people
        self.familyDb = self.db.families

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
                        tags.append(Classes.TagLine(level, tag, args))
                if len(tags) > 0:
                    if currentType == "INDI":
                        self.peopleDb.insert_one(Classes.Person(tags).getJson())
                    elif currentType == "FAM":
                        self.familyDb.insert_one(Classes.Family(tags).getJson())
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
                    tags.append(Classes.TagLine(level, tag, args))

    def printFamilies(self):
        familyTable = PrettyTable()
        familyTable.field_names = ["ID", "Married", "Divorced", "Husband ID", "Husband Name", "Wife ID", "Wife Name",
                                "Children"]
        print("Families:")
        for family in self.familyDb.find({}):
            # print(family)
            family['hus_name'] = "hus_name"
            family['wife_name'] = "wife_name"
            if family['divorceDate'] is None:
                family['divorceDate'] = "NA"
            if family['marriageDate'] is None:
                family['marriageDate'] = "NA"

            # Note: Change this, it's costly to query entire collection of individuals for every single family
            for person in self.peopleDb.find({}):
                if (family['husbandId'] == person['indId']):
                    family['hus_name'] = person['name']
                elif (family['wifeId'] == person['indId']):
                    family['wife_name'] = person['name']

            familyTable.add_row([family['famId'], family['marriageDate'], family['divorceDate'], family['husbandId'],
                              family['hus_name'], family['wifeId'], family['wife_name'], family['childrenIds']])
        print(familyTable)

    def printPeople(self):
        personTable = PrettyTable()
        personTable.field_names = ["ID", "Name", "Gender", "Birthday", "Age", "Alive", "Death", "Child", "Spouse"]
        print("Individuals:")
        for person in self.peopleDb.find({}):
            # print(person)
            person['birth'] = person['birth'].replace(" ", "/")
            b_date = datetime.strptime(person['birth'], "%d/%b/%Y").strftime('%m/%d/%Y')
            b_date = datetime.strptime(b_date, '%m/%d/%Y').date()
            person['age'] = int((datetime.today().date() - b_date).days / 365)
            person['birth'] = datetime.strptime(person['birth'], "%d/%b/%Y").strftime('%Y-%m-%d')
            person['child'] = "NA"
            person['alive'] = "True"
            person['death'] = "NA"
            person['spouse'] = "NA"

            lastTag = None
            for tagLineString in person['tags']:
                tagLine = tagLineString.split(" ", maxsplit=2)

                level = tagLine[0]
                tag = tagLine[1]

                args = ""
                if len(tagLine) > 2:
                    args = tagLine[2]

                if args == "FAMS" or args == "FAMC":
                    args, tag = tag, args

                person['alive'] = "True"
                person['death'] = "NA"

                if tag == "FAMC":
                    person['child'] = "{}".format(args.strip("@"))
                elif tag == "FAMS":
                    person['spouse'] = "{}".format(args.strip("@"))
                elif tag == "DEAT":
                    person['alive'] = "False"
                elif tag == "DATE":
                    if lastTag == "DEAT":
                        person['death'] = args

                lastTag = tag

            personTable.add_row([person['indId'], person['name'], person['sex'], person['birth'],
                                 person['age'], person['alive'], person['death'], person['child'], person['spouse']])
        print(personTable)

