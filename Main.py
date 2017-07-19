import Classes
import Validate
import Print


def main():
    print('Welcome to the Stevens Institute of Technology GEDCOM Family Tree Project - SSW555 2017')

    repository = Classes.Repository("localhost", 27017, "test1.ged")

    Print.people(repository)
    Print.families(repository)
    Print.deadPeople(repository)
    Print.livingMarriedPeople(repository)

    Validate.people(repository)
    Validate.families(repository)


if __name__ == "__main__":
    main()
