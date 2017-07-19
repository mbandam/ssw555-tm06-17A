import Classes
import Validate
from Exceptions import MarriageAfterDeath
import unittest


class US06Test(unittest.TestCase):
    def setUp(self):
        husbandTags = []
        husbandTags.append(Classes.TagLine('0', '@I1@', 'INDI'))
        husbandTags.append(Classes.TagLine('1', 'NAME', 'Joe'))
        husbandTags.append(Classes.TagLine('2', 'SUR', 'Smith'))
        husbandTags.append(Classes.TagLine('1', 'SEX', 'M'))
        husbandTags.append(Classes.TagLine('1', 'BIRT', ''))
        husbandTags.append(Classes.TagLine('2', 'DATE', '3 APR 1960'))
        husbandTags.append(Classes.TagLine('1', 'FAMS', '@F1@'))
        self.husband = Classes.Person(husbandTags)

        wifeTags = []
        wifeTags.append(Classes.TagLine('0', '@I2@', 'INDI'))
        wifeTags.append(Classes.TagLine('1', 'NAME', 'Sally'))
        wifeTags.append(Classes.TagLine('2', 'SUR', 'Smith'))
        wifeTags.append(Classes.TagLine('1', 'SEX', 'F'))
        wifeTags.append(Classes.TagLine('1', 'BIRT', ''))
        wifeTags.append(Classes.TagLine('2', 'DATE', '3 APR 1960'))
        wifeTags.append(Classes.TagLine('1', 'FAMS', '@F1@'))
        self.wife = Classes.Person(wifeTags)

        familyTags = []
        familyTags.append(Classes.TagLine('0', '@F1@', 'FAM'))
        familyTags.append(Classes.TagLine('1', 'HUSB', '@I1@'))
        familyTags.append(Classes.TagLine('1', 'WIFE', '@I2@'))
        familyTags.append(Classes.TagLine('1', 'MARR', ''))
        familyTags.append(Classes.TagLine('2', 'DATE', '1 JAN 2000'))
        self.family = Classes.Family(familyTags)

    def testHusbandDiedAfterMarriage(self):
        self.husband.addTag(Classes.TagLine('1', 'DEAT', 'Y'))
        self.husband.addTag(Classes.TagLine('1', 'DATE', '8 JAN 2001'))
        Validate.marriageBeforeDeath(self.husband, self.wife, self.family)

    def testWifeDiedAfterMarriage(self):
        self.wife.addTag(Classes.TagLine('1', 'DEAT', 'Y'))
        self.wife.addTag(Classes.TagLine('1', 'DATE', '8 JAN 2001'))
        Validate.marriageBeforeDeath(self.husband, self.wife, self.family)

    def testBothDiedAfterMarriage(self):
        self.husband.addTag(Classes.TagLine('1', 'DEAT', 'Y'))
        self.husband.addTag(Classes.TagLine('1', 'DATE', '8 JAN 2001'))
        self.wife.addTag(Classes.TagLine('1', 'DEAT', 'Y'))
        self.wife.addTag(Classes.TagLine('1', 'DATE', '8 JAN 2001'))
        Validate.marriageBeforeDeath(self.husband, self.wife, self.family)

    def testHusbandDiedBeforeMarriage(self):
        self.husband.addTag(Classes.TagLine('1', 'DEAT', 'Y'))
        self.husband.addTag(Classes.TagLine('1', 'DATE', '8 JAN 1999'))
        self.assertRaises(MarriageAfterDeath, Validate.marriageBeforeDeath, self.husband, self.wife, self.family)

    def testWifeDiedBeforeMarriage(self):
        self.wife.addTag(Classes.TagLine('1', 'DEAT', 'Y'))
        self.wife.addTag(Classes.TagLine('1', 'DATE', '8 JAN 1999'))
        self.assertRaises(MarriageAfterDeath, Validate.marriageBeforeDeath, self.husband, self.wife, self.family)

    def testBothDiedBeforeMarriage(self):
        self.husband.addTag(Classes.TagLine('1', 'DEAT', 'Y'))
        self.husband.addTag(Classes.TagLine('1', 'DATE', '8 JAN 1999'))
        self.wife.addTag(Classes.TagLine('1', 'DEAT', 'Y'))
        self.wife.addTag(Classes.TagLine('1', 'DATE', '8 JAN 1999'))
        self.assertRaises(MarriageAfterDeath, Validate.marriageBeforeDeath, self.husband, self.wife, self.family)

    def testBothStillAlive(self):
        Validate.marriageBeforeDeath(self.husband, self.wife, self.family)


if __name__ == '__main__':
    unittest.main()
