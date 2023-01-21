import pyperclip
import os.path
import csv
import re


def chk_if_valid_file(user_text: str):
    path_exists = os.path.exists(user_text) \
                  or os.path.exists(f"{user_text}.csv")

    if not path_exists:
        message = "File does not exist. Attempting to convert as csv text."
        return False, message

    if not user_text[-4:] == ".csv":
        # Add .csv since user gave filename without it
        message = "User did not include .csv in the filepath."
        user_text = f"{user_text}.csv"
    else:
        message = "File found!"

    return user_text, message


def clean_cell(cell_text):
    chars_to_remove = ['\n', '\\', '\r', ';', ',', '|']

    # Remove chars in cell that are in chars_to_remove
    cleaned_cell = re.sub(f"[{''.join(chars_to_remove)}]", '', cell_text)

    # Replace tab characters with spaces
    cleaned_cell = cleaned_cell.replace("\t", " ")

    # Remove trailing, leading, and two or more continuous spaces
    cleaned_cell = re.sub(" +", ' ', cleaned_cell.strip())

    return cleaned_cell


def clean_list(csv_list: list) -> list:
    cleaned_list = []
    longest_row = len(max(csv_list, key=len))
    too_short_rows = []

    # Clean the rows
    for index, row in enumerate(csv_list):
        cleaned_row = []
        # Clean cell text
        for cell in row:
            cleaned_row.append(clean_cell(cell))

        # Check for empty values
        if len(row) < longest_row:
            too_short_rows.append(index)

        cleaned_list.append(cleaned_row)

    # Lengthen the rows
    # for num in too_short_rows:
    #     lengthen_row(cleaned_list[num], longest_row)

    return cleaned_list


def lengthen_row(csv_row: list, desired_length: int) -> None:
    difference = desired_length - len(csv_row)

    for num in range(difference):
        csv_row.append("NaN")


def convert_csv_to_markdown(csv_text: list, has_headers: str) -> str:
    max_column_width = []
    column_count = 1  # In-case of empty list

    for i in range(len(csv_text[0])):
        # Get the max width per column
        column_count = len(csv_text[0])
        row_max_width = len(max([row[i] for row in csv_text], key=len))

        # Save the max width per column
        max_column_width.append(row_max_width)

    markdown_table = []

    try:
        # Create the headers
        if has_headers != 'n':
            markdown_table.append(
                '| '
                + ' | '.join([csv_text[0][index].center(max_column_width[index])
                              for index in range(column_count)])
                + ' |'
            )
        else:
            # Create basic numbers for the headers
            new_headers = [str(num) for num in range(column_count)]
            markdown_table.append(
                '| '
                + ' | '.join([new_headers[index].center(max_column_width[index])
                              for index in range(column_count)])
                + ' |'
            )

        # Create the text-alignment row
        markdown_table.append(
            '|:'
            + ':|:'.join('-' * width
                         for width in max_column_width)
            + ':|'
        )

        # Create the main body
        for row in csv_text[1:]:
            markdown_table.append(
                '| '
                + ' | '.join([cell.center(max_column_width[i])
                              for i, cell in enumerate(row)])
                + ' |'
            )

        return '\n'.join(markdown_table)
    except IndexError:
        print("It appears the text you entered/pasted is neither a filepath to "
              "a csv file, or csv text itself. Please try again...")
        exit(1)


def clipboard_setup() -> None:
    pyperclip.determine_clipboard()
    user_input = input("Your clipboard will be cleared. "
                       "Is that okay? [Y/n]: ").casefold().strip()

    if user_input == 'n':
        print("Exiting program...")
        exit(0)

    pyperclip.copy('')


def check_clipboard(user_text: str) -> str:
    user_data = pyperclip.paste() or user_text
    return user_data


if __name__ == "__main__":
    # Clear clipboard
    clipboard_setup()

    # Check if there's headers
    headers = input("Would you like to include headers? [Y/n]: ") \
        .casefold().strip()

    input_data = check_clipboard(input("Copy or enter filepath or csv text:\n"))
    file, status_message = chk_if_valid_file(input_data)

    print()
    print(status_message)

    # Check if user input is a filepath or regular csv text
    if file:
        with open(file, newline='', encoding='utf-8') as csv_file:
            cursor = csv.reader(csv_file)
            rows = [row for row in cursor]
    else:
        rows = [cell.split() for cell in input_data.split('\n')]

    # Create Markdown table
    markdown = convert_csv_to_markdown(clean_list(rows), headers)

    # Print out Markdown table
    print(markdown)

    # Copy to clipboard
    pyperclip.copy(markdown)

    # Print final message
    print()
    print("Copied to clipboard!")
