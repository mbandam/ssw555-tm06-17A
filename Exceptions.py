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

        self.message = "ERROR: INDIVIDUAL: US03: {}: {} was born on {} after they died on {}".format(indiId, name,
                                                                                                     birthDate,
                                                                                                     deathDate)


class MarriageException(Error):
    def __init__(self, person, family):
        self.indId = person.getIndiId()
        self.famId = family.getFamId()
        self.marriageDate = family.getMarriageDate()


class MarriageAfterDeath(MarriageException):
    def __init__(self, person, family):
        if person.getSex() == Domain.Sex.MALE.value:
            self.message = "ERROR: FAMILY: US05: {}: Husband ({}) cannot get married on {} as he died before on {}".format(
                famId, indId, marriageDate, deathDate)
        else:
            famId = family.getFamId()
            indId = person.getIndiId()
            self.message = (
            'ERROR: FAMILY: US05: {}: ' + 'Wife (' + indId + ')' + ' cannot get married on ' + marriageDate + ' as she died before on ' + deathDate)


class MarriageBeforeBirth(MarriageException):
    def __init__(self, person, family):
        MarriageException.__init__(self, person, family)
        self.message = "ERROR: FAMILY: US06: {}: Husband ({}) cannot get divorced on {} as he died before on ({})".format(
            self.famId, self.indId, self.divorceDate, self.deathDate)


class DivorceAfterDeath(MarriageException):
    def __init__(self, person, family):
        name = person.getName()
        deathDate = person.getDeathDate()
        divorceDate = family.getDivorceDate()
        if person.getSex() == Domain.Sex.MALE.value and name is not None:
            famId = family.getFamId()
            indId = person.getIndiId()
            self.message = "ERROR: FAMILY: US06: {}: Husband ({}) cannot get divorced on {} as he died before on ({})".format(
                famId, indId, divorceDate, deathDate)
        elif name is not None:
            famId = family.getFamId()
            indId = person.getIndiId()
            self.message = "ERROR: FAMILY: US06: {}: Wife ({}) cannot get divorced on {} as she died before on ({})".format(
                famId, indId, divorceDate, deathDate)
        elif person.getSex() == Domain.Sex.MALE:
            famId = family.getFamId()
            indId = person.getIndiId()
            self.message = "ERROR: FAMILY: US06: {}: Husband ({}) cannot get divorced on {} as he died before on ({})".format(
                famId, indId, divorceDate, deathDate)
        else:
            famId = family.getFamId()
            indId = person.getIndiId()
            self.message = "ERROR: FAMILY: US06: {}: Wife ({}) cannot get divorced on {} as she died before on ({})".format(
                famId, indId, divorceDate, deathDate)


class MarriageAfterDivorce(MarriageException):
    def __init__(self, family):
        marriageDate = family.getMarriageDate()
        divorceDate = family.getDivorceDate()
        famId = family.getFamId()

        self.message = "ERROR: FAMILY: US04: {}: Family has marriage date ({}) later than their divorce date ({}).".format(
            famId, marriageDate, divorceDate)
