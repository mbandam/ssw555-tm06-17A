from prettytable import PrettyTable
from datetime import datetime, timedelta
import Domain
import Util

def people(repository):
    personTable = PrettyTable()
    personTable.field_names = ["ID", "Name", "Gender", "Birthday", "Age", "Alive", "Death", "Child", "Spouse"]
    print("Individuals:")
    for person in repository.getPeople():
        birthday = datetime.strptime(person.getBirthDate().replace(" ", "/"), "%d/%b/%Y").strftime('%m/%d/%Y')
        age = int((datetime.today().date() - datetime.strptime(birthday, '%m/%d/%Y').date()).days / 365)
        personTable.add_row([person.getIndiId(),
                             person.getName(),
                             person.getSex(),
                             birthday,
                             age,
                             person.getDeathDate() is None,
                             formatValue(person.getDeathDate()),
                             formatValue(person.getChildFamilyId()),
                             formatValue(person.getSpousalFamilyIds())])
    print(personTable)


def deadPeople(repository):
    deathTable = PrettyTable()
    deathTable.field_names = ["ID", "Name", "Death Date"]
    for person in repository.getPeople():
        if person.getDeathDate() is not None:
            deathTable.add_row([person.getIndiId(), person.getName(), person.getDeathDate()])
    print('US29: The following people are dead:')
    print(deathTable)

def recentDeadPeople(repository):
    recentDeathTable = PrettyTable()
    recentDeathTable.field_names = ["ID", "Name", "Death Date"]
    for person in repository.getPeople():
        if person.getDeathDate() is not None and (datetime.today() - timedelta(days=30)) <= Util.parseDate(person.getDeathDate()) <= datetime.today():
            recentDeathTable.add_row([person.getIndiId(), person.getName(), person.getDeathDate()])
    print('US36: List of recently dead prople')
    print(recentDeathTable)

def upcomingBirthdays(repository):
    upcomingBirthdayTable = PrettyTable()
    upcomingBirthdayTable.field_names = ["ID", "Name", "Birth Date"]
    for person in repository.getPeople():
        birthDate = Util.parseDate(person.getBirthDate())
        currentYear = datetime.now().year
        birthDate = str(birthDate.day) + " " + str(birthDate.month) + " " + str(currentYear)
        birthDate = datetime.strptime(birthDate, '%d %m %Y')
        if person.getBirthDate() is not None and (datetime.today()) <= birthDate <= (datetime.today() + timedelta(days=30)):
            upcomingBirthdayTable.add_row([person.getIndiId(), person.getName(), person.getBirthDate()])
    print('US38: List of upcoming birthdays')
    print(upcomingBirthdayTable)
    
def livingMarriedPeople(repository):
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


def families(repository):
    familyTable = PrettyTable()
    familyTable.field_names = ["ID", "Married", "Divorced", "Husband ID", "Husband Name", "Wife ID", "Wife Name",
                               "Children"]
    print("Families:")
    for family in repository.getFamilies():
        familyTable.add_row([family.getFamId(),
                             formatDate(family.getMarriageDate()),
                             formatDate(family.getDivorceDate()),
                             family.getHusbandId(),
                             repository.getPerson(family.getHusbandId()).getName(),
                             family.getWifeId(),
                             repository.getPerson(family.getWifeId()).getName(),
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
