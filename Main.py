import Classes
import Validator
import Console


def main():
    print('Welcome to the Stevens Institute of Technology GEDCOM Family Tree Project - SSW555 2017')
    repository = Classes.Repository("localhost", 27017)
    repository.add("test1.ged")
    Console.printPeople(repository)
    Console.printFamilies(repository)
    Console.printDeadPeople(repository)
    Console.printLivingMarriedPeople(repository)
    Validator.validatePeople(repository)
    Validator.validateFamilies(repository)


if __name__ == "__main__":
    main()
