from enum import Enum
from datetime import datetime

def validTags():
    return {"0 INDI",
            "1 NAME",
            "1 SEX",
            "1 BIRT",
            "1 DEAT",
            "1 FAMC",
            "1 FAMS",
            "0 FAM",
            "1 MARR",
            "1 HUSB",
            "1 WIFE",
            "1 CHIL",
            "1 DIV",
            "2 DATE"}

class Sex(Enum):
        MALE = 'M'
        FEMALE = 'F'


