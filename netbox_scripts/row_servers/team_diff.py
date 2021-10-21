#!/usr/bin/python3

def main():
    teams1 = set()
    teams2 = set()

    with open('teams_row_b', 'r') as f:
        for team in f.readlines():
            teams1.add(team.rstrip("\n"))

    with open('teams_row_d', 'r') as f:
        for team in f.readlines():
            teams2.add(team.rstrip("\n"))

    print("Add: {}".format((teams2 - teams1)))
    print("Remove: {}".format((teams1 - teams2))) 


if __name__=="__main__":
    main()

