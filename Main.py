import Classes
import Validator

def main():
    print('Welcome to the Stevens Institute of Technology GEDCOM Family Tree Project - SSW555 2017')
    repository = Classes.Repository("localhost", 27017)
    repository.add("test1.ged")
    repository.printFamilies()
    repository.printPeople()
    repository.datesBeforeCurrentDate()
    repository.birthBeforeMarriage()
    Validator.validatePeople(repository)
    Validator.validateFamilies(repository)


if __name__ == "__main__":
    main()
