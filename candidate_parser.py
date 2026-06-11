import re

def extract_email(text):

    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    match = re.search(pattern, text)

    if match:
        return match.group()

    return "Not Found"


def extract_phone(text):

    pattern = r"\+?\d[\d\s\-]{8,15}"

    match = re.search(pattern, text)

    if match:
        return match.group()

    return "Not Found"


def extract_name(text):

    lines = text.split("\n")

    for line in lines[:5]:

        line = line.strip()

        if len(line) > 2 and len(line.split()) <= 4:
            return line

    return "Not Found"