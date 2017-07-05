import Domain
from datetime import date


class Error(Exception):
    pass


class PersonException(Error):
    def __init__(self, person, userStoryNumber):
        self.message = 'ERROR: US{}: INDIVIDUAL {}: ' \
            .format(userStoryNumber, person.getIndiId())


class BirthInFuture(PersonException):
    def __init__(self, person):
        PersonException.__init__(self, person, '01')
        self.message += 'They were born in the future on {}. Today is {}.'.format(person.getBirthDate(),
                                                                                  date.today())


class BirthAfterDeath(PersonException):
    def __init__(self, person):
        PersonException.__init__(self, person, '03')
        self.message += 'They were born on {} after they died on {}.'.format(person.getBirthDate(),
                                                                             person.getDeathDate())


class MarriageException(Error):
    def __init__(self, person, family, userStoryNumber):
        if person.getSex() == Domain.Sex.MALE.value:
            self.message = 'ERROR: US{}: FAMILY {}: HUSBAND {}: Marriage on {} is invalid. '.format(userStoryNumber,
                                                                                                    family.getFamId(),
                                                                                                    person.getIndiId(),
                                                                                                    family.getMarriageDate())
        else:
            self.message = 'ERROR: US{}: FAMILY {}: WIFE {}: Marriage on {} is invalid. '.format(userStoryNumber,
                                                                                                 family.getFamId(),
                                                                                                 person.getIndiId(),
                                                                                                 family.getMarriageDate())


class MarriageBeforeBirth(MarriageException):
    def __init__(self, person, family):
        MarriageException.__init__(self, person, family, '02')
        self.message += 'Their marriage occurred before their birth on {}.'.format(person.getBirthDate())


class MarriageAfterDivorce(MarriageException):
    def __init__(self, person, family):
        MarriageException.__init__(self, person, family, '04')
        self.message += 'Their divorce occurred before the marriage on {}.'.format(family.getDivorceDate())


class MarriageAfterDeath(MarriageException):
    def __init__(self, person, family):
        MarriageException.__init__(self, person, family, '05')
        self.message += 'They died before the marriage on {}.'.format(person.getDeathDate())


class DivorceAfterDeath(MarriageException):
    def __init__(self, person, family):
        MarriageException.__init__(self, person, family, '06')
        self.message += 'They died {}, before their divorce on {}.'.format(person.getDeathDate(),
                                                                           family.getDivorceDate())
