from prettytable import PrettyTable
from datetime import datetime
import Domain


def printPeople(repository):
    personTable = PrettyTable()
    personTable.field_names = ["ID", "Name", "Gender", "Birthday", "Age", "Alive", "Death", "Child", "Spouse"]
    print("Individuals:")
    for person in repository.getPeople():
        birthDate = datetime.strptime(person.getBirthDate().replace(" ", "/"), "%d/%b/%Y").strftime('%m/%d/%Y')
        age = int((datetime.today().date() - datetime.strptime(birthDate, '%m/%d/%Y').date()).days / 365)

        personTable.add_row([person.getIndiId(),
                             person.getName(),
                             person.getSex(),
                             birthDate,
                             age,
                             person.getDeathDate() is None,
                             formatValue(person.getDeathDate()),
                             formatValue(person.getChildFamilyId()),
                             formatValue(person.getSpousalFamilyIds())])
    print(personTable)


def printDeadPeople(repository):
    deathTable = PrettyTable()
    deathTable.field_names = ["ID", "Name", "Death Date"]
    for person in repository.getPeople():
        if person.getDeathDate() is not None:
            deathTable.add_row([person.getIndiId(), person.getName(), person.getDeathDate()])
    print('US29: The following people are dead:')
    print(deathTable)


def printLivingMarriedPeople(repository):
    marriageTable = PrettyTable()
    marriageTable.field_names = ["ID", "Name", "Role", "Family ID"]
    for person in repository.getPeople():
        if person.getDeathDate() is None and person.getSpousalFamilyIds():
            for familyId in person.getSpousalFamilyIds():
                if repository.getFamily(familyId).getDivorceDate() is None:
                    if person.getSex() == Domain.Sex.MALE.value:
                        role = 'Husband'
                    else:
                        role = 'Wife'
                    marriageTable.add_row([person.getIndiId(), person.getName(), role, person.getSpousalFamilyIds()])
                    break
    print('US30: The following people are living and married:')
    print(marriageTable)


def printFamilies(repository):
    familyTable = PrettyTable()
    familyTable.field_names = ["ID", "Married", "Divorced", "Husband ID", "Husband Name", "Wife ID", "Wife Name",
                               "Children"]
    print("Families:")
    for family in repository.getFamilies():
        divorceDate = formatDate(family.getDivorceDate())
        marriageDate = formatDate(family.getMarriageDate())
        husbandName = repository.getPerson(family.getHusbandId()).getName()
        wifeName = repository.getPerson(family.getWifeId()).getName()

        familyTable.add_row([family.getFamId(),
                             marriageDate,
                             divorceDate,
                             family.getHusbandId(),
                             husbandName,
                             family.getWifeId(),
                             wifeName,
                             family.getChildrenIds()])
    print(familyTable)


def formatDate(date):
    if date is None:
        return "NA"
    else:
        return datetime.strptime(date.replace(" ", "/"), "%d/%b/%Y").strftime('%Y-%m-%d')


def formatValue(value):
    if value is None or not value:
        return 'NA'
    else:
        return value
