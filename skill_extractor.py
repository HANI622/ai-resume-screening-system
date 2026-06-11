from skills import skills_list

def extract_skills(text):

    text = text.lower()

    found_skills = []

    for skill in skills_list:

        if skill.lower() in text:
            found_skills.append(skill)

    return list(set(found_skills))