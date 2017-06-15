import Exceptions
import Util


# Print exception messages for all invalid families in the database
def validateFamilies(repository):
    exceptionMessages = []
    for family in repository.getFamilies():
        husband = repository.getPerson(family.getHusbandId())
        wife = repository.getPerson(family.getWifeId())
        try:
            validateMarriage(husband, wife, family)
        except Exceptions.MarriageException as e:
            exceptionMessages.append(e.message)
    if exceptionMessages:
        for message in exceptionMessages:
            print(message)
    else:
        print('All families are valid.')


# Pass husband, wife and family objects through validation checks
def validateMarriage(husband, wife, family):
    marriageIsBeforeDeath(husband, wife, family)
    divorceIsBeforeDeath(husband, wife, family)


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
