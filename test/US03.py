import Classes
import Validator
import Exceptions
import unittest

class US03Test(unittest.TestCase):
    def getExceptionsForAllPeople(self, filename):
        repository = Classes.Repository("localhost", 27017)
        repository.add(filename)
        exceptionMessages = []

        for person in repository.getPeople():
            try:
                Validator.birthBeforeDeath(person)
            except Exceptions.PersonException as e:
                exceptionMessages.append(e.message)

        return exceptionMessages

    def testOneError(self):
        exceptionMessages = self.getExceptionsForAllPeople("test_us03_1.ged")
        self.assertEqual(len(exceptionMessages), 1)

    def testThreeErrors(self):
        exceptionMessages = self.getExceptionsForAllPeople("test_us03_2.ged")
        self.assertEqual(len(exceptionMessages), 3)

    def testNoErrors(self):
        exceptionMessages = self.getExceptionsForAllPeople("test_us03_3.ged")
        self.assertEqual(len(exceptionMessages), 0)

    def testMissingBirth(self):
        exceptionMessages = self.getExceptionsForAllPeople("test_us03_4.ged")
        self.assertEqual(len(exceptionMessages), 0)

    def testSameDate(self):
        exceptionMessages = self.getExceptionsForAllPeople("test_us03_5.ged")
        self.assertEqual(len(exceptionMessages), 0)


if __name__ == '__main__':
    unittest.main()
