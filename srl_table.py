#!/usr/bin/python3

from pprintpp import pprint as pp

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('filename', help='file name with SRL table')
args = parser.parse_args()

def main():
    with open(args.filename, 'r') as myfile:
        lines = myfile.readlines()

    heading_section = True
    heading_lines = 0
    columns = []
    output_lines = []

    for line in lines:
        if line.startswith("A"):
            print(line.strip())
            continue 
        if line.startswith("+"):
            if heading_section and line.startswith("+="):
                heading_section = False
            continue
        if heading_lines == 0 and line.startswith("|"):
            heading_lines += 1
            # Add full line to our 'output_lines' as a list
            output_lines.append([text.strip() for text in line.strip().split("|")])
            # Parse the contents of each column to set title and max_width
            for column_text in line.strip().split("|"):
                columns.append({
                    "title": column_text.strip(),
                    "max_width": len(column_text.strip())
                })
            continue
        if line.startswith("|"):
            output_lines.append([text.strip() for text in line.strip().split("|")])
            for index, column_text in enumerate(line.strip().split("|")):
                if len(column_text.strip()) > columns[index]['max_width']:
                    columns[index]['max_width'] = len(column_text.strip())
            if heading_section:
                heading_lines += 1

    first_line = "+"
    for column in columns:
        if column['max_width'] == 0:
            continue
        first_line += f"{'-' * (column['max_width'] + 2)}+"
    print(first_line)
    heading_section = True
    for line_list in output_lines:
        line = "|"
        for index, column_text in enumerate(line_list):
            if columns[index]['max_width'] == 0:
                continue
            line += f" {column_text:<{columns[index]['max_width']}} |"
        print(line)
        if heading_section:
            heading_lines -= 1
            if heading_lines == 0:
                print(first_line.replace("-", "="))
                heading_section = False
    print(first_line)    
        


if __name__=="__main__":
    main()
