def calculate_match(resume_skills, job_description):

    job_description = job_description.lower()

    matched = []
    missing = []

    for skill in resume_skills:

        if skill.lower() in job_description:
            matched.append(skill)

    for word in [
        "python",
        "java",
        "sql",
        "machine learning",
        "html",
        "css",
        "javascript",
        "react",
        "django",
        "flask"
    ]:

        if word in job_description and word not in matched:
            missing.append(word)

    if len(matched) + len(missing) == 0:
        score = 0
    else:
        score = (
            len(matched)
            / (len(matched) + len(missing))
        ) * 100

    return matched, missing, round(score, 2)