import Classes
import pymongo
from prettytable import PrettyTable
from datetime import datetime

def main():
    # These are the only level+tag combinations we are recognizing
    # Note: removed "0 HEAD", "0 TRLR", "0 NOTE"
    valid_tag_set = {"0 INDI", "1 NAME", "1 SEX", "1 BIRT", "1 DEAT", "1 FAMC", "1 FAMS", "0 FAM", "1 MARR", "1 HUSB",
                     "1 WIFE", "1 CHIL", "1 DIV", "2 DATE"}

    # Read in all of the lines from the GEDCOM file
    with open("test1.ged") as file:
        lines = [line.rstrip("\n") for line in file.readlines()]

    # Setup database
    dbClient = pymongo.MongoClient("localhost", 27017)
    db = dbClient.ssw555_tm06_17A
    dbClient.drop_database(db)
    people = db.people
    families = db.families

    # Store all individuals and families in the database
    tags = []
    currentId = None  # GEDCOM unique ID
    currentType = None  # INDI or FAM
    for line in lines:
        tokens = line.split(" ", maxsplit=2)
        level = tokens[0]
        tag = tokens[1]

        args = ""
        if len(tokens) > 2:
            args = tokens[2]

        # For INDI and FAM, ID comes before the tag,
        # so swap the 'args' and 'tag' variables
        if args == "INDI" or args == "FAM":
            args, tag = tag, args

        levelTagPair = (level + " " + tag)

        """
        Insert the current individual or family once we've reached either:
            - a new individual
            - a new family
            - the end of the GEDCOM file
        """
        if levelTagPair == "0 INDI" or levelTagPair == "0 FAM" or line == lines[len(lines) - 1]:
            if line == lines[len(lines) - 1]:
                if levelTagPair not in valid_tag_set:
                    print("Ignoring '{}': unrecognized level+tag combination".format(line))
                else:
                    tags.append(Classes.TagLine(level, tag, args))
            if len(tags) > 0:
                if currentType == "INDI":
                    people.insert_one(Classes.Person(tags).getJson())
                elif currentType == "FAM":
                    families.insert_one(Classes.Family(tags).getJson())
                else:
                    print("Error: Current entity not of type INDI or FAM")
                    currentId = None
                    currentType = None
            currentId = args
            currentType = tag
            tags = []

        if line != lines[len(lines) - 1]:
            if not currentId:
                print("Ignoring '{}': haven't started individual or family".format(line))
            elif levelTagPair not in valid_tag_set:
                print("Ignoring '{}': unrecognized level+tag combination".format(line))
            else:
                tags.append(Classes.TagLine(level, tag, args))

    # Pretty Table design
    Individuals = PrettyTable()
    Individuals.field_names = ["ID", "Name", "Gender", "Birthday","Age","Alive","Death","Child","Spouse"]
    print("Individuals:")
    for person in people.find({}):
        #print(person)
        person['birth'] = person['birth'].replace(" ", "/")
        b_date = datetime.strptime(person['birth'],"%d/%b/%Y").strftime('%m/%d/%Y')
        b_date = datetime.strptime(b_date, '%m/%d/%Y').date()
        person['age'] = int((datetime.today().date() - b_date).days/365)
        person['birth'] = datetime.strptime(person['birth'], "%d/%b/%Y").strftime('%Y-%m-%d')
        person['child'] = "NA"
        person['alive'] = "True"
        person['death'] = "NA"
        if len(person['tags']) == 2:
            word = person['tags'][1].split()
            if word[1] == "FAMC":
                word[2] = word[2].replace("@","")
                person['child'] = '{'+word[2]+'}'
                person['alive'] = "True"
                person['death'] = "False"
            
            elif word[1]== "FAMS":
                word[2] = word[2].replace("@","")
                person['spouse'] = '{'+word[2]+'}'
                person['alive'] = "True"
                person['death'] = "False"
            
            else:
                person['child'] = "NA"
                person['spouse'] = "NA"
        else:
            person['child'] = "NA"
            person['spouse'] = "NA"
        
        if len(person['tags']) == 4:
            word = person['tags'][1].split()
            if word[1] == "DEAT":
                person['alive'] = "False"
            else:
                person['alive'] = "True"
            word = person['tags'][2].split()
            if word[1] == "DATE":
                DeathDate = word[2]+"/"+word[3]+"/"+word[4]
                person['death'] = datetime.strptime(DeathDate, "%d/%b/%Y").strftime('%Y-%m-%d')
            else:
                person['death'] = "NA"
            word = person['tags'][3].split()
            if word[1] == "FAMC":
                word[2] = word[2].replace("@","")
                person['child'] = '{'+word[2]+'}'
            elif word[1]== "FAMS":
                word[2] = word[2].replace("@","")
                person['spouse'] = '{'+word[2]+'}'
            else:
                person['child'] = "NA"
                person['spouse'] = "NA"
        
        Individuals.add_row([person['indId'],person['name'],person['sex'],person['birth'],
                             person['age'],person['alive'],person['death'],person['child'],person['spouse']])
    print(Individuals)
    
    Families = PrettyTable()
    Families.field_names = ["ID", "Married", "Divorced", "Husband ID","Husband Name","Wife ID","Wife Name","Children"]
    print("Families:")
    for family in families.find({}):
        #print(family)
        family['hus_name'] = "hus_name"
        family['wife_name'] = "wife_name"
        if family['divorceDate'] is None:
            family['divorceDate'] = "NA"
        for person in people.find({}):
            if(family['husbandId'] == person['indId']):
                family['hus_name'] = person['name']
            if(family['wifeId'] == person['indId']):
                family['wife_name'] = person['name']
            
        Families.add_row([family['famId'],family['marriageDate'],family['divorceDate'],family['husbandId'],
                          family['hus_name'],family['wifeId'],family['wife_name'],family['childrenIds']])
    print(Families)


if __name__ == "__main__":
    main()
