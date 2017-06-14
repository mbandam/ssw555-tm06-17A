import Classes

import unittest

class US03Test(unittest.TestCase):

    def setUp(self):
        self.repository = Classes.Repository("localhost", 27017)

    def getPeopleWithErrors(self, filename):
        self.repository.add(filename)
        return self.repository.checkBirthBeforeDeath()

    def testOneError(self):
        peopleWithErrors = self.getPeopleWithErrors("test_us03_1.ged")
        self.assertEqual(len(peopleWithErrors), 1)

    def testThreeErrors(self):
        peopleWithErrors = self.getPeopleWithErrors("test_us03_2.ged")
        self.assertEqual(len(peopleWithErrors), 3)

    def testNoErrors(self):
        peopleWithErrors = self.getPeopleWithErrors("test_us03_3.ged")
        self.assertEqual(len(peopleWithErrors), 0)

    def testMissingBirth(self):
        peopleWithErrors = self.getPeopleWithErrors("test_us03_4.ged")
        self.assertEqual(len(peopleWithErrors), 0)

    def testSameDate(self):
        peopleWithErrors = self.getPeopleWithErrors("test_us03_5.ged")
        self.assertEqual(len(peopleWithErrors), 0)

if __name__ == '__main__':
    unittest.main()