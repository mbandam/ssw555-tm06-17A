import Exceptions
import Util
import Domain
from datetime import datetime
from dateutil.relativedelta import relativedelta


def people(repository):
    functions = [birthBeforeDeath, birthInFuture, deathInFuture, ageMorethan150, birthBeforeParentDeath]
    exceptionMessages = []

    for person in repository.getPeople():
        for fn in functions:
            try:
                fn(person, repository)
            except Exceptions.PersonException as e:
                exceptionMessages.append(e.message)

    try:
        uniqueIndividualIds(repository)
    except Exceptions.PersonException as e:
        exceptionMessages.append(e.message)

    if exceptionMessages:
        for message in exceptionMessages:
            print(message)
    else:
        print("All individuals are valid.")


def birthBeforeDeath(person, repository):
    birthDate = Util.parseDate(person.getBirthDate())
    deathDate = Util.parseDate(person.getDeathDate())

    if deathDate is not None and birthDate is not None and birthDate > deathDate:
        raise Exceptions.BirthAfterDeath(person)


def birthInFuture(person, repository):
    if inFuture(Util.parseDate(person.getBirthDate())):
        raise Exceptions.BirthInFuture(person)


def deathInFuture(person, repository):
    if person.getDeathDate() is not None:
        if inFuture(Util.parseDate(person.getDeathDate())):
            raise Exceptions.DeathInFuture(person)


def ageMorethan150(person, repository):
    birthDate = Util.parseDate(person.getBirthDate())
    deathDate = Util.parseDate(person.getDeathDate())
    if deathDate is not None and birthDate is not None and (relativedelta(deathDate, birthDate).years >= 150):
        raise Exceptions.AgeMorethan150(person)
    if deathDate is None and birthDate is not None and (relativedelta(datetime.today(), birthDate).years >= 150):
        raise Exceptions.AgeMorethan150(person)


def birthBeforeParentDeath(person, repository):
    famId = person.getChildFamilyId()

    if famId is not None:
        family = repository.getFamily(famId)
        father = repository.getPerson(family.getHusbandId())
        mother = repository.getPerson(family.getWifeId())

        fatherDeathDate = Util.parseDate(father.getDeathDate())
        motherDeathDate = Util.parseDate(mother.getDeathDate())
        childBirthDate = Util.parseDate(person.getBirthDate())

        if (fatherDeathDate is not None) and relativedelta(childBirthDate, fatherDeathDate).months >= 9:
            raise Exceptions.BirthOver9MonthsAfterFatherDeath(person, father.getDeathDate())
        elif (motherDeathDate is not None) and childBirthDate > motherDeathDate:
            raise Exceptions.BirthAfterMotherDeath(person, mother.getDeathDate())


def uniqueIndividualIds(repository):
    individualIds = []
    for person in repository.getPeople():
        individualIds.append(person.getIndiId())
    if len(individualIds) != len(set(individualIds)):
        dupIds = set([x for x in individualIds if individualIds.count(x) > 1])
        for individualId in dupIds:
            individual = repository.getPerson(individualId)
            raise Exceptions.UniqueIndividualIds(individual)


# Print exception messages for all invalid families in the database
def families(repository):
    functions = [marriageBeforeDeath, birthBeforeMarriage, divorceBeforeDeath, marriageBeforeDivorce, marriageInFuture,
                 divorceInFuture, marriageAfter14, birthBfMarriageOfParents, differentMaleLastName, marriedToDescendant,
                 correctGenderForRole, siblingsNotMarried, firstCousinsNotMarried]

    exceptionMessages = []
    for family in repository.getFamilies():
        husband = repository.getPerson(family.getHusbandId())
        wife = repository.getPerson(family.getWifeId())
        for fn in functions:
            try:
                fn(husband, wife, family, repository)
            except Exceptions.MarriageException as e:
                exceptionMessages.append(e.message)

    try:
        uniqueFamilyIds(repository)
    except Exceptions.MarriageException as e:
        exceptionMessages.append(e.message)

    if exceptionMessages:
        for message in exceptionMessages:
            print(message)
    else:
        print('All families are valid.')


def marriageInFuture(husband, wife, family, repository):
    if inFuture(Util.parseDate(family.getMarriageDate())):
        raise Exceptions.MarriageInFuture(husband, family)


def divorceInFuture(husband, wife, family, repository):
    if family.getDivorceDate() is not None:
        if inFuture(Util.parseDate(family.getDivorceDate())):
            raise Exceptions.DivorceInFuture(husband, family)


def marriageBeforeDeath(husband, wife, family, repository):
    marriageDate = Util.parseDate(family.getMarriageDate())
    if marriageDate is None:
        return
    husbandDeathDate = Util.parseDate(husband.getDeathDate())
    wifeDeathDate = Util.parseDate(wife.getDeathDate())
    if husbandDeathDate is None and wifeDeathDate is None:
        return
    if husbandDeathDate is not None and husbandDeathDate < marriageDate:
        raise Exceptions.MarriageAfterDeath(husband, family)
    if wifeDeathDate is not None and wifeDeathDate < marriageDate:
        raise Exceptions.MarriageAfterDeath(wife, family)
    return


def birthBeforeMarriage(husband, wife, family, repository):
    marriageDate = Util.parseDate(family.getMarriageDate())
    if marriageDate is None:
        return
    husbandBirthday = Util.parseDate(husband.getBirthDate())
    wifeBirthday = Util.parseDate(wife.getBirthDate())
    if husbandBirthday is None and wifeBirthday is None:
        return
    if husbandBirthday is not None and husbandBirthday > marriageDate:
        raise Exceptions.MarriageBeforeBirth(husband, family)
    if wifeBirthday is not None and wifeBirthday > marriageDate:
        raise Exceptions.MarriageBeforeBirth(wife, family)


def divorceBeforeDeath(husband, wife, family, repository):
    divorceDate = Util.parseDate(family.getDivorceDate())
    if divorceDate is None:
        return
    husbandDeathDate = Util.parseDate(husband.getDeathDate())
    wifeDeathDate = Util.parseDate(wife.getDeathDate())
    if husbandDeathDate is None and wifeDeathDate is None:
        return
    if husbandDeathDate is not None and husbandDeathDate < divorceDate:
        raise Exceptions.DivorceAfterDeath(husband, family)
    if wifeDeathDate is not None and wifeDeathDate < divorceDate:
        raise Exceptions.DivorceAfterDeath(wife, family)
    return


def marriageBeforeDivorce(husband, wife, family, repository):
    marriageDate = Util.parseDate(family.getMarriageDate())
    divorceDate = Util.parseDate(family.getDivorceDate())

    if divorceDate is not None and marriageDate is not None and marriageDate > divorceDate:
        raise Exceptions.MarriageAfterDivorce(husband, family)


def marriageAfter14(husband, wife, family, repository):
    marriageDate = Util.parseDate(family.getMarriageDate())
    husbandBirthDate = Util.parseDate(husband.getBirthDate())
    wifeBirthDate = Util.parseDate(wife.getBirthDate())

    if relativedelta(marriageDate, husbandBirthDate).years < 14:
        raise Exceptions.MarriageBefore14(husband, family)
    if relativedelta(marriageDate, wifeBirthDate).years < 14:
        raise Exceptions.MarriageBefore14(wife, family)


def birthBfMarriageOfParents(husband, wife, family, repository):
    marriageDate = Util.parseDate(family.getMarriageDate())
    divorceDate = Util.parseDate(family.getDivorceDate())
    for cid in family.getChildrenIds():
        child = repository.getPerson(cid)
        childBdate = Util.parseDate(child.getBirthDate())
        if marriageDate > childBdate:
            raise Exceptions.BirthBeforeMarriageOfParents(child, family)
        if divorceDate is not None and relativedelta(childBdate, divorceDate).months >= 9:
            raise Exceptions.BirthAfterDivorceOfParents(child, family)


def marriedToDescendant(husband, wife, family, repository):
    uncheckedFamilies = {family}
    checkedFamilies = set()
    while uncheckedFamilies:
        family = uncheckedFamilies.pop()
        checkedFamilies.add(family.getFamId())
        for childId in family.getChildrenIds():
            if childId == husband.getIndiId():
                raise Exceptions.MarriedToDescendant(wife, family)
            if childId == wife.getIndiId():
                raise Exceptions.MarriedToDescendant(husband, family)
            for familyId in repository.getPerson(childId).getSpousalFamilyIds():
                if familyId not in checkedFamilies:
                    uncheckedFamilies.add(repository.getFamily(familyId))


def differentMaleLastName(husband, wife, family, repository):
    for childId in family.getChildrenIds():
        child = repository.getPerson(childId)
        if child.getSex() is Domain.Sex.MALE.value and child.getLastName() != husband.getLastName():
            raise Exceptions.differentMaleLastName(husband, family, child)


def correctGenderForRole(husband, wife, family, repository):
    husbandSex = husband.getSex()
    wifeSex = wife.getSex()
    if husbandSex != 'M':
        raise Exceptions.NotCorrectGenderForHusband(husband, family)
    if wifeSex != 'F':
        raise Exceptions.NotCorrectGenderForWife(wife, family)


def uniqueFamilyIds(repository):
    familyIds = []
    for family in repository.getFamilies():
        familyIds.append(family.getFamId())
    if len(familyIds) != len(set(familyIds)):
        dupIds = set([x for x in familyIds if familyIds.count(x) > 1])
        for familyId in dupIds:
            family = repository.getFamily(familyId)
            husband = repository.getPerson(family.getHusbandId())
            raise Exceptions.UniqueFamilyIds(husband, family)


def siblingsNotMarried(husband, wife, family, repository):
    husbandId = husband.getIndiId()
    wifeId = wife.getIndiId()

    for otherFamily in repository.getFamilies():
        childrenIds = otherFamily.getChildrenIds()
        if husbandId in childrenIds and wifeId in childrenIds:
            raise Exceptions.SiblingMarriage(husband, family, otherFamily)


def firstCousinsNotMarried(husband, wife, family, repository):
    husbandId = husband.getIndiId()
    wifeId = husband.getIndiId()

    husbandFamilyId = husband.getChildFamilyId()
    wifeFamilyId = wife.getChildFamilyId()

    if husbandFamilyId and wifeFamilyId:
        husbandFamily = repository.getFamily(husbandFamilyId)
        wifeFamily = repository.getFamily(wifeFamilyId)

        husbandFatherId = husbandFamily.getHusbandId()
        husbandMotherId = husbandFamily.getWifeId()
        wifeFatherId = wifeFamily.getHusbandId()
        wifeMotherId = wifeFamily.getWifeId()

        parentIds = [husbandFatherId, husbandMotherId, wifeFatherId, wifeMotherId]
        parents = []
        for id in parentIds:
            if id:
                parents.append(repository.getPerson(id))

        parentFamilyIds = []
        for parent in parents:
            childFamilyId = parent.getChildFamilyId()
            if childFamilyId:
                parentFamilyIds.append(childFamilyId)

        for id in parentFamilyIds:
            if parentFamilyIds.count(id) >= 2:
                raise Exceptions.FirstCousinMarriage(husband, family)


def inFuture(day):
    if day:
        return day > datetime.today()
