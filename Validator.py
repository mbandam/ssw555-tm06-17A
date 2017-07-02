import Exceptions
import Util


# Print exception messages for all invalid individuals in the database
def validatePeople(repository):
    functions = [birthIsBeforeDeath]
    exceptionMessages = []

    for person in repository.getPeople():
        for fn in functions:
            try:
                fn(person)
            except Exceptions.PersonException as e:
                exceptionMessages.append(e.message)

    if exceptionMessages:
        for message in exceptionMessages:
            print(message)
    else:
        print("All individuals are valid.")


def birthIsBeforeDeath(person):
    birthDate = Util.parseDate(person.getBirthDate())
    deathDate = Util.parseDate(person.getDeathDate())

    if deathDate is not None and birthDate is not None and birthDate > deathDate:
        raise Exceptions.BirthAfterDeath(person)


# Print exception messages for all invalid families in the database
def validateFamilies(repository):
    functions = [marriageIsBeforeDeath, divorceIsBeforeDeath, marriageIsBeforeDivorce]
    exceptionMessages = []

    for family in repository.getFamilies():
        husband = repository.getPerson(family.getHusbandId())
        wife = repository.getPerson(family.getWifeId())

        for fn in functions:
            try:
                fn(husband, wife, family)
            except Exceptions.MarriageException as e:
                exceptionMessages.append(e.message)

    if exceptionMessages:
        for message in exceptionMessages:
            print(message)
    else:
        print('All families are valid.')


# Confirm the marriage occured before the death of the husband and wife
def marriageIsBeforeDeath(husband, wife, family):
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


def birthIsBeforeMarriage(husband, wife, family):
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


# Confirm the divorce occured before the death of the husband and wife
def divorceIsBeforeDeath(husband, wife, family):
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


def marriageIsBeforeDivorce(husband, wife, family):
    marriageDate = Util.parseDate(family.getMarriageDate())
    divorceDate = Util.parseDate(family.getDivorceDate())

    if divorceDate is not None and marriageDate is not None and marriageDate > divorceDate:
        raise Exceptions.MarriageAfterDivorce(husband, family)
