import Classes
import pymongo

def main():
    valid_tag_set = {"0 INDI", "1 NAME", "1 SEX", "1 BIRT", "1 DEAT", "1 FAMC", "1 FAMS", "0 FAM", "1 MARR", "1 HUSB",
                     "1 WIFE", "1 CHIL", "1 DIV", "2 DATE", "0 HEAD", "0 TRLR", "0 NOTE"}

    with open("test1.ged") as file:
        lines = [line.rstrip("\n") for line in file.readlines()]

    id = 1
    people = []
    tags = []

    for line in lines:
        tokens = line.split(" ", maxsplit=2)
        level = tokens[0]
        tag = tokens[1]

        args = ""
        if len(tokens) > 2:
            args = tokens[2]

        if args == "INDI" or args == "FAM":
            # Swap args and tag
            args, tag = tag, args

        if (level + " " + tag) in valid_tag_set:
                tags.append(Classes.TagLine(level, tag, args))
        else:
            print("Ignoring '" + line + "' invalid format.")
            continue

        if (level + " " + tag) == "0 INDI" and len(tags) > 0:
            for tag in tags:
                if Classes.TagLine.getTag(tag) == "NAME":
                    people.append(Classes.Person(tags).getJson(id))
                    id += 1
            tags = []

    #Here are 'Person' JSON objects we can persist in MongoDB :)
    for person in people:
        print(person)

if __name__ == "__main__":
    main()