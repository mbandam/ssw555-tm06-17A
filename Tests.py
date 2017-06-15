import Classes
import Validator
import Exceptions
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

class US06Test(unittest.TestCase):

    def setUp(self):
        husbandTags = []
        husbandTags.append(Classes.TagLine(0, '@I1@', 'INDI'))
        husbandTags.append(Classes.TagLine(1, 'NAME', 'Joe'))
        husbandTags.append(Classes.TagLine(2, 'SUR', 'Smith'))
        husbandTags.append(Classes.TagLine(1, 'SEX', 'M'))
        husbandTags.append(Classes.TagLine(1, 'BIRT', ''))
        husbandTags.append(Classes.TagLine(2, 'DATE', '3 APR 1960'))
        husbandTags.append(Classes.TagLine(1, 'FAMS', '@F1@'))
        self.husband = Classes.Person(husbandTags)

        wifeTags = []
        wifeTags.append(Classes.TagLine(0, '@I2@', 'INDI'))
        wifeTags.append(Classes.TagLine(1, 'NAME', 'Sally'))
        wifeTags.append(Classes.TagLine(2, 'SUR', 'Smith'))
        wifeTags.append(Classes.TagLine(1, 'SEX', 'F'))
        wifeTags.append(Classes.TagLine(1, 'BIRT', ''))
        wifeTags.append(Classes.TagLine(2, 'DATE', '3 APR 1960'))
        wifeTags.append(Classes.TagLine(1, 'FAMS', '@F1@'))
        self.wife = Classes.Person(wifeTags)

        familyTags = []
        familyTags.append(Classes.TagLine(0, '@F1@', 'FAM'))
        familyTags.append(Classes.TagLine(1, 'HUSB', '@I1@'))
        familyTags.append(Classes.TagLine(1, 'WIFE', '@I2@'))
        familyTags.append(Classes.TagLine(1, 'MARR', ''))
        familyTags.append(Classes.TagLine(2, 'DATE', '1 JAN 2000'))
        self.family = Classes.Family(familyTags)

    def husbandDiedBeforeMarriage(self):
        self.husband.addTag(Classes.TagLine(1, 'DEAT', 'Y'))
        self.husband.addTag(Classes.TagLine(1, 'DATE', '8 JAN 1999'))
        self.assertRaises(Validator.marriageIsBeforeDeath(self.husband, self.wife, self.family), Exceptions.MarriageAfterDeath)


    def wifeDiedBeforeMarriage(self):
        self.wife.addTag(Classes.TagLine(1, 'DEAT', 'Y'))
        self.wife.addTag(Classes.TagLine(1, 'DATE', '8 JAN 1999'))
        self.assertRaises(Validator.marriageIsBeforeDeath(self.husband, self.wife, self.family), Exceptions.MarriageAfterDeath)

    def bothDiedBeforeMarriage(self):
        self.husband.addTag(Classes.TagLine(1, 'DEAT', 'Y'))
        self.husband.addTag(Classes.TagLine(1, 'DATE', '8 JAN 1999'))
        self.wife.addTag(Classes.TagLine(1, 'DEAT', 'Y'))
        self.wife.addTag(Classes.TagLine(1, 'DATE', '8 JAN 1999'))
        self.assertRaises(Validator.marriageIsBeforeDeath(self.husband, self.wife, self.family), Exceptions.MarriageAfterDeath)

    def bothStillAlive(self):
        Validator.marriageIsBeforeDeath(self.husband, self.wife, self.family)

    def bothDiedAfterMarriage(self):
        self.husband.addTag(Classes.TagLine(1, 'DEAT', 'Y'))
        self.husband.addTag(Classes.TagLine(1, 'DATE', '8 JAN 2001'))
        self.wife.addTag(Classes.TagLine(1, 'DEAT', 'Y'))
        self.wife.addTag(Classes.TagLine(1, 'DATE', '8 JAN 2001'))
        Validator.marriageIsBeforeDeath(self.husband, self.wife, self.family)


if __name__ == '__main__':
    unittest.main()