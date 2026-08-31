from database import (
    get_all_students_with_applications,
    get_all_fellowships,
    get_student_preferences,
    get_faculty_preferences,
)


def run_matching():
    """
    Runs algorithm where it only match if professors and students are both ranked top 2 
    in the list of preferences
    """
    students = get_all_students_with_applications()
    fellowship_list = get_all_fellowships()

    student_match = {s: None for s in students}
    fellowship_matches = {fid: [] for fid, _ in fellowship_list}
    student_next = {s: 0 for s in students}
    unmatched = set(students)

    student_prefs = {}
    for s in students:
        prefs = get_student_preferences(s)
        student_prefs[s] = [fid for fid, _ in prefs]

    faculty_prefs = {}
    for fid, capacity in fellowship_list:
        prefs = get_faculty_preferences(fid)
        faculty_prefs[fid] = {
            "rank_list": [s for s, _ in prefs],
            "rank_index": {s: i for i, (s, _) in enumerate(prefs)},
            "capacity": capacity
        }

    while unmatched:
        student = unmatched.pop()
        prefs = student_prefs.get(student, [])

        if student_next[student] >= len(prefs):
            continue

        fid = prefs[student_next[student]]
        student_next[student] += 1

        if student_next[student] - 1 > 1:
            continue

        faculty_data = faculty_prefs.get(fid, {})
        rank_idx = faculty_data.get("rank_index", {})
        student_rank = rank_idx.get(student, float('inf'))

        if student_rank > 1:
            unmatched.add(student)
            continue

        matched_list = fellowship_matches[fid]
        cap = faculty_data["capacity"]

        if len(matched_list) < cap:
            matched_list.append(student)
            student_match[student] = fid
            continue

        ranked_matches = [(rank_idx.get(s, float('inf')), s) for s in matched_list]
        worst_rank, worst_student = max(ranked_matches, key=lambda x: x[0])

        if student_rank < worst_rank:
            matched_list.remove(worst_student)
            matched_list.append(student)
            student_match[student] = fid
            student_match[worst_student] = None
            unmatched.add(worst_student)
        else:
            unmatched.add(student)

    return {fid: s for fid, s in fellowship_matches.items() if s}
