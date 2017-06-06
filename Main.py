import Classes
import pymongo


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
            if len(tags) > 0:
                if currentType == "INDI":
                    people.insert_one(Classes.Person(tags).getJson())
                # elif currentType == "FAM":
                #     families.insertOne(Classes.Family(tags).getJson())
                else:
                    print("Error: Current entity not of type INDI or FAM")
                    currentId = None
                    currentType = None
            currentId = args
            currentType = tag
            tags = []

        if not currentId:
            print("Ignoring '{}': haven't started individual or family".format(line))
        elif levelTagPair not in valid_tag_set:
            print("Ignoring '{}': invalid level+tag combination".format(line))
        else:
            tags.append(Classes.TagLine(level, tag, args))

    print("People:")
    for person in people.find({}):
        print(person)


if __name__ == "__main__":
    main()
