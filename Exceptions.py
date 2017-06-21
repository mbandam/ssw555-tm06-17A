import Domain


class Error(Exception):
    pass

class PersonException(Error):
    def __init__(self):
        self.message = 'This individual is invalid.'

class BirthAfterDeath(PersonException):
    def __init__(self, person):
        name = person.getName()
        indiId = person.getIndiId()
        birthDate = person.getBirthDate()
        deathDate = person.getDeathDate()

        self.message = "{} (with ID of {}) was born on {} after they died on {}".format(name, indiId, birthDate, deathDate)

class MarriageException(Error):
    def __init__(self):
        self.message = 'This marriage is invalid.'

class MarriageAfterDeath(MarriageException):
    def __init__(self, person, family):
        name = person.getName()
        deathDate = person.getDeathDate()
        marriageDate = family.getMarriageDate()
        if person.getSex() == Domain.Sex.MALE and name is not None:
            self.message = (name + ' cannot get married ' + marriageDate + '. He died before then on ' + deathDate)
        elif name is not None:
            self.message = (name + ' cannot get married ' + marriageDate + '. She died before then on ' + deathDate)
        elif person.getSex == Domain.Sex.MALE:
            famId = family.getFamId()
            self.message(
                'Husband of familyId ' + famId + ' cannot get married ' + marriageDate + '. He died before then on ' + deathDate)
        else:
            famId = family.getFamId()
            self.message(
                'Wife of familyId ' + famId + ' cannot get married ' + marriageDate + '. She died before then on ' + deathDate)

class DivorceAfterDeath(MarriageException):
    def __init__(self, person, family):
        name = person.getName()
        deathDate = person.getDeathDate()
        divorceDate = family.getDivorceDate()
        if person.getSex() == Domain.Sex.MALE and name is not None:
            self.message = (name + ' cannot get divorced ' + divorceDate + '. He died before then on ' + deathDate)
        elif name is not None:
            self.message = (name + ' cannot get divorced ' + divorceDate + '. She died before then on ' + deathDate)
        elif person.getSex == Domain.Sex.MALE:
            famId = family.getFamId()
            self.message(
                'Husband of familyId ' + famId + ' cannot get divorced ' + divorceDate + '. He died before then on ' + deathDate)
        else:
            famId = family.getFamId()
            self.message(
                'Wife of familyId ' + famId + ' cannot get divorced ' + divorceDate + '. She died before then on ' + deathDate)

class MarriageAfterDivorce(MarriageException):
    def __init__(self, family):
        marriageDate = family.getMarriageDate()
        divorceDate = family.getDivorceDate()
        famId = family.getFamId()

        self.message = "Family {} has marriage date ({}) later than their divorce date ({}).".format(famId, marriageDate, divorceDate)
