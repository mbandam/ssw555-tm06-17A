import Domain


class Error(Exception):
    pass


class PersonException(Error):
    def __init__(self, person, userStoryNumber):
        self.message = "ERROR: INDIVIDUAL {}: US{}: " \
            .format(person.getIndiId(), userStoryNumber)


class BirthAfterDeath(PersonException):
    def __init__(self, person):
        PersonException.__init__(self, person, '03')
        self.message += "They were born on {} after they died on {}".format(person.getBirthDate(),
                                                                            person.getDeathDate())


class MarriageException(Error):
    def __init__(self, person, family, userStoryNumber):
        if person.getSex() == Domain.Sex.MALE.value:
            self.message = "ERROR: FAMILY {}: HUSBAND {}: US{}: Marriage on {} is invalid. ".format(family.getFamId(),
                                                                                                    person.getIndiId(),
                                                                                                    userStoryNumber,
                                                                                                    family.getMarriageDate())
        else:
            self.message = "ERROR: FAMILY {}: WIFE {}: US{}: Marriage on {} is invalid. ".format(family.getFamId(),
                                                                                                 person.getIndiId(),
                                                                                                 userStoryNumber,
                                                                                                 family.getMarriageDate())


class MarriageAfterDeath(MarriageException):
    def __init__(self, person, family):
        MarriageException.__init__(self, person, family, "05")
        self.message += "They died before the marriage on {}.".format(person.getDeathDate())


class MarriageBeforeBirth(MarriageException):
    def __init__(self, person, family):
        MarriageException.__init__(self, person, family, "06")
        self.message += "Their birth occurred before the marriage on {}.".format(person.getBirthDate())


class DivorceAfterDeath(MarriageException):
    def __init__(self, person, family):
        MarriageException.__init__(self, person, family, "06")
        self.message += "They died {}, before the divorce on {}.".format(person.getDeathDate(), family.getDivorceDate())


class MarriageAfterDivorce(MarriageException):
    def __init__(self, person, family):
        MarriageException.__init__(self, person, family, "04")
        self.message += "Their divorce occurred before the marriage on {}.".format(family.getDivorceDate())
