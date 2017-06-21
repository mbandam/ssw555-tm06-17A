import Classes
import Domain
import pymongo
from prettytable import PrettyTable
from datetime import datetime, date


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
        return self.getArg("NAME")

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
    def __init__(self, host, port):
        # Database config
        self.dbClient = pymongo.MongoClient("localhost", 27017)
        self.db = self.dbClient.ssw555_tm06_17A
        self.dbClient.drop_database(self.db)

        # Declare buckets
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
            else:
                family['divorceDate'] = family['divorceDate'].replace(" ", "/")
                family['divorceDate'] = datetime.strptime(family['divorceDate'], "%d/%b/%Y").strftime('%Y-%m-%d')
            if family['marriageDate'] is None:
                family['marriageDate'] = "NA"
            else:
                family['marriageDate'] = family['marriageDate'].replace(" ", "/")
                family['marriageDate'] = datetime.strptime(family['marriageDate'], "%d/%b/%Y").strftime('%Y-%m-%d')

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

                # person['alive'] = "True"
                # person['death'] = "NA"

                if tag == "FAMC":
                    person['child'] = "{}".format(args.strip("@"))
                elif tag == "FAMS":
                    person['spouse'] = "{}".format(args.strip("@"))
                elif tag == "DEAT":
                    person['alive'] = "False"
                elif tag == "DATE":
                    if lastTag == "DEAT":
                        person['death'] = args
                        person['death'] = person['death'].replace(" ", "/")
                        person['death'] = datetime.strptime(person['death'], "%d/%b/%Y").strftime('%Y-%m-%d')

                lastTag = tag

            personTable.add_row([person['indId'], person['name'], person['sex'], person['birth'],
                                 person['age'], person['alive'], person['death'], person['child'], person['spouse']])
        print(personTable)

    # Going forward, let's reserve the repository class for CRUD operations.
    # To learn more about the repository pattern, check this out: https://msdn.microsoft.com/en-us/library/ff649690.aspx
    # - Tim
    def birthBeforeMarriage(self):
        errorMessages = []
        for family in self.familyDb.find({}):
            for person in self.peopleDb.find({}):
                if (family['husbandId'] == person['indId']):
                    person['birth'] = person['birth'].replace(" ", "/")
                    hus_bdate = datetime.strptime(person['birth'], "%d/%b/%Y").strftime('%m/%d/%Y')
                    hus_bdate = datetime.strptime(hus_bdate, '%m/%d/%Y').date()
                if (family['wifeId'] == person['indId']):
                    person['birth'] = person['birth'].replace(" ", "/")
                    wife_bdate = datetime.strptime(person['birth'], "%d/%b/%Y").strftime('%m/%d/%Y')
                    wife_bdate = datetime.strptime(wife_bdate, '%m/%d/%Y').date()

            if family['marriageDate'] is not None:
                family['marriageDate'] = family['marriageDate'].replace(" ", "/")
                marriage_date = datetime.strptime(family['marriageDate'], "%d/%b/%Y").strftime('%m/%d/%Y')
                marriage_date = datetime.strptime(marriage_date, '%m/%d/%Y').date()
                if Repository.checkBirthBeforeMarriage(hus_bdate, marriage_date) is False:
                    error = "For family " + family['famId'] + ": Husband " + family[
                        'husbandId'] + " has date of birth " + str(hus_bdate) + " after marriage date " + str(
                        marriage_date)
                    errorMessages.append(error)
                if Repository.checkBirthBeforeMarriage(wife_bdate, marriage_date) is False:
                    error = "For family " + family['famId'] + ": Wife " + family[
                        'wifeId'] + " has date of birth " + str(wife_bdate) + " after marriage date " + str(
                        marriage_date)
                    errorMessages.append(error)
        if errorMessages:
            print(errorMessages)

    def checkBirthBeforeMarriage(b_date, m_date):
        if b_date is None:
            print("The given birthday date is null")
            return False
        else:
            if m_date is None:
                print("Marriage date is not available")
                return False
            elif b_date < m_date:
                return True
            else:
                return False

    def datesBeforeCurrentDate(self):
        errorMessages = []
        today = date.today()
        # Checking birth and death dates of an individual
        for person in self.peopleDb.find({}):
            person['birth'] = person['birth'].replace(" ", "/")
            birth_date = datetime.strptime(person['birth'], "%d/%b/%Y").strftime('%m/%d/%Y')
            birth_date = datetime.strptime(birth_date, '%m/%d/%Y').date()
            if (birth_date > today):
                error = person['indId'] + "has birthday on " + str(birth_date) + " which is after current date"
                errorMessages.append(error)

            lastTag = None
            death_date = "NA"
            for tagLineString in person['tags']:
                tagLine = tagLineString.split(" ", maxsplit=2)

                level = tagLine[0]
                tag = tagLine[1]

                args = ""
                if len(tagLine) > 2:
                    args = tagLine[2]

                if tag == "DATE":
                    if lastTag == "DEAT":
                        death_date = args
                        death_date = death_date.replace(" ", "/")
                        death_date = datetime.strptime(death_date, "%d/%b/%Y").strftime('%m/%d/%Y')
                        death_date = datetime.strptime(death_date, '%m/%d/%Y').date()

                lastTag = tag
            if death_date != "NA":
                if (death_date > today):
                    error = person['indId'] + "has deathday on " + str(death_date) + " which is after current date"
                    errorMessages.append(error)

        # Checking marriage and divorce dates of a family
        for family in self.familyDb.find({}):
            if family['divorceDate'] is not None:
                family['divorceDate'] = family['divorceDate'].replace(" ", "/")
                divorce_date = datetime.strptime(family['divorceDate'], "%d/%b/%Y").strftime('%m/%d/%Y')
                divorce_date = datetime.strptime(divorce_date, '%m/%d/%Y').date()
                if (divorce_date > today):
                    error = family['famId'] + "has marriageday on " + str(divorce_date) + " which is after current date"
                    errorMessages.append(error)
            if family['marriageDate'] is not None:
                family['marriageDate'] = family['marriageDate'].replace(" ", "/")
                marriage_date = datetime.strptime(family['marriageDate'], "%d/%b/%Y").strftime('%m/%d/%Y')
                marriage_date = datetime.strptime(marriage_date, '%m/%d/%Y').date()
                if (marriage_date > today):
                    error = family['famId'] + "has marriageday on " + str(
                        marriage_date) + " which is after current date"
                    errorMessages.append(error)

        if errorMessages:
            print(errorMessages)

    def checkBirthBeforeDeath(self):
        '''US03'''
        peopleWithErrors = []
        for person in self.peopleDb.find({}):

            if person['birth'] and person["death"]:
                birthDate = self.convertGedcomDate(person['birth'])
                deathDate = self.convertGedcomDate(person['death'])

                if birthDate > deathDate:
                    print("Error US03: {}'s death date ({}) precedes their birth date ({})".format(person["name"],
                                                                                                   person["death"],
                                                                                                   person["birth"]))
                    peopleWithErrors.append(person)
        return peopleWithErrors

    def convertGedcomDate(self, date):
        '''Convert GEDCOM date string to datetime.date object'''
        return datetime.strptime(date, "%d %b %Y").date()

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

    def getPerson(self, individualId):
        for person in self.getPeople():
            if person.getIndiId() == individualId:
                return person
        return None

    def getFamily(self, famId):
        for family in self.getFamilies():
            if family.getFamId() == famId:
                return family
        return None

    def getSpouses(self, individualId):
        familyId = self.getFamilyId(individualId)

    def getFamilyId(self, individualId):
        return self.peopleDb.find({'indId': individualId})['famId']

    def getMarriageDate(self, familyId):
        return self.peopleDb.find({'famId': familyId})['marriageDate']

    def getDivoreceDate(self, familyId):
        return self.peopleDb.find({'famId': familyId})['divorceDate']


def formatId(id):
    if id is None:
        return
    return id.replace("@", "")
