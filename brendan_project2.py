def main():
    valid_tag_set = {"0 INDI", "1 NAME", "1 SEX", "1 BIRT", "1 DEAT", "1 FAMC", "1 FAMS", "0 FAM", "1 MARR", "1 HUSB",
                     "1 WIFE", "1 CHIL", "1 DIV", "2 DATE", "0 HEAD", "0 TRLR", "0 NOTE"}

    with open("test1.ged") as file:
        lines = [line.rstrip("\n") for line in file.readlines()]

        for line in lines:
            print("--> {}".format(line))

            tokens = line.split(" ", maxsplit=2)
            level = tokens[0]
            tag = tokens[1]

            args = ""
            if len(tokens) > 2:
                args = tokens[2]

            if args == "INDI" or args == "FAM":
                temp = args
                args = tag
                tag = temp

            valid = "N"
            if (level + " " + tag) in valid_tag_set:
                valid = "Y"

            if args:
                print("<-- {}|{}|{}|{}".format(level, tag, valid, args))
            else:
                print("<-- {}|{}|{}".format(level, tag, valid))

if __name__ == "__main__":
    main()