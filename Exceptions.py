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
        self.message += 'The person was born in the future on {} where Today is {}.'.format(person.getBirthDate(),
                                                                                  date.today())
class DeathInFuture(PersonException):
    def __init__(self, person):
        PersonException.__init__(self, person, '01')
        self.message += 'The person is died in the future on {} where Today is {}.'.format(person.getDeathDate(),
                                                                                  date.today())

class BirthAfterDeath(PersonException):
    def __init__(self, person):
        PersonException.__init__(self, person, '03')
        self.message += 'They were born on {} after they died on {}.'.format(person.getBirthDate(),
                                                                             person.getDeathDate())
class AgeMorethan150(PersonException):
    def __init__(self, person):
        PersonException.__init__(self, person, '07')
        self.message += 'The person is living for more than 150 years - birthdate is {}.'.format(person.getBirthDate())

class MarriageException(Error):
    def __init__(self, person, family, userStoryNumber):
        if person.getSex() == Domain.Sex.MALE.value:
            self.message = 'ERROR: US{}: FAMILY {}: HUSBAND {}: Marriage on {} is invalid.'.format(userStoryNumber,
                                                                                                    family.getFamId(),
                                                                                                    person.getIndiId(),
                                                                                                    family.getMarriageDate())
        else:
            self.message = 'ERROR: US{}: FAMILY {}: WIFE {}: Marriage on {} is invalid.'.format(userStoryNumber,
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
class BirthBeforeMarriageOfParents(MarriageException):
    def __init__(self, person, family):
        MarriageException.__init__(self, person, family, '08')
        self.message = 'ANOMALY: US08: Family {}: Child {} born on {} before marriage on {}.'.format(family.getFamId(), person.getIndiId(), person.getBirthDate(), family.getMarriageDate())
        
class BirthAfterDivorceOfParents(MarriageException):
    def __init__(self, person, family):
        MarriageException.__init__(self, person, family, '08')
        self.message = 'ANOMALY: US08: Family {}: Child {} born on {} after divorce on {}.'.format(family.getFamId(), person.getIndiId(), person.getBirthDate(), family.getMarriageDate())
        
class MarriageInFuture(MarriageException):
    def __init__(self, person, family):
        MarriageException.__init__(self, person, family, '01')
        self.message = 'ERROR: US01: Family {}: This family has marriage date in the future on {} where Today is {}.'.format(family.getFamId(), family.getMarriageDate(), date.today())

class DivorceInFuture(MarriageException):
    def __init__(self, person, family):
        MarriageException.__init__(self, person, family, '01')
        self.message = 'ERROR: US01: Family {}: This family has divorce date in the future on {} where Today is {}.'.format(family.getFamId(), family.getDivorceDate(), date.today())
