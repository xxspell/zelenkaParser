import random
import re
import structlog
import settings

logger = structlog.get_logger(__name__)

def extract_information(text, rules):
    """
    Extracts information from text using rules.

    Parameters:
    - text (str): The original text from which information needs to be extracted.
    - rules (list): A list of rules for extracting information.
                    Each rule is represented as a tuple (name, regular expression).

    Returns:
    - dict: A dictionary where keys are rule names,
            and values are corresponding fragments extracted from the text.
    """
    extracted_info = {}

    for rule_name, regex_pattern in rules:
        matches = re.findall(regex_pattern, text)

        if matches:
            extracted_info[rule_name] = matches
            logger.info(f"Extracted information for rule '{rule_name}': {matches}")
        else:
            logger.info(f"No matches found for rule '{rule_name}'")

    return extracted_info




def convert_row_to_dict(row):
    fields = settings.DB_USERFIELDS
    return {field[0]: value for field, value in zip(fields, row)}


def random_number_in_range(input_string):
    # Splitting a string into two values by a space
    min_value, max_value = map(int, input_string.split())

    # Generating a random number within a specified range
    result = random.randint(min_value, max_value)

    return result


def write_to_file(variable, filename):
    with open(filename, 'a') as file:
        file.write(str(variable) + '\n')