from copy import deepcopy


def create_initial_state(student_id: str) -> dict:
    return {
        "student_id": (student_id or "").strip(),
        "current_question_index": 0,
        "attempt_count": 0,
        "finished": False,
        "question_records": [],
        "history": [],
    }


def get_current_question(state: dict, lesson_kb: dict) -> dict | None:
    if not state or state.get("finished"):
        return None

    questions = lesson_kb.get("questions", [])
    index = state.get("current_question_index", 0)

    if index < 0 or index >= len(questions):
        return None
    return questions[index]


def record_attempt(state: dict, question_id: int, student_answer: str, judge_result: dict, analysis_result: dict) -> dict:
    new_state = deepcopy(state)
    new_state["attempt_count"] = int(new_state.get("attempt_count", 0)) + 1

    attempt_record = {
        "question_id": question_id,
        "attempt_no": new_state["attempt_count"],
        "student_answer": student_answer,
        "judge_result": judge_result or {},
        "analysis_result": analysis_result or {},
    }

    question_records = list(new_state.get("question_records", []))
    question_record = None
    for item in question_records:
        if item.get("question_id") == question_id:
            question_record = item
            break

    if question_record is None:
        question_record = {
            "question_id": question_id,
            "attempts": [],
            "best_score": 0,
            "final_score": 0,
            "completed": False,
        }
        question_records.append(question_record)

    question_record.setdefault("attempts", []).append(attempt_record)

    score = judge_result.get("score", 0) if isinstance(judge_result, dict) else 0
    try:
        score = int(score)
    except (TypeError, ValueError):
        score = 0

    question_record["best_score"] = max(int(question_record.get("best_score", 0)), score)
    question_record["final_score"] = score

    is_goal_reached = False
    if isinstance(judge_result, dict):
        is_goal_reached = bool(judge_result.get("is_goal_reached", False))

    if is_goal_reached or new_state["attempt_count"] >= 2:
        question_record["completed"] = True

    history = list(new_state.get("history", []))
    history.append(
        {
            "type": "attempt",
            "question_id": question_id,
            "attempt_no": new_state["attempt_count"],
            "student_answer": student_answer,
            "judge_result": judge_result or {},
            "analysis_result": analysis_result or {},
        }
    )

    new_state["question_records"] = question_records
    new_state["history"] = history
    return new_state


def advance_question(state: dict) -> dict:
    new_state = deepcopy(state)
    new_state["current_question_index"] = int(new_state.get("current_question_index", 0)) + 1
    new_state["attempt_count"] = 0
    return new_state


def is_session_finished(state: dict, lesson_kb: dict) -> bool:
    if not state:
        return True
    if state.get("finished"):
        return True

    questions = lesson_kb.get("questions", [])
    index = int(state.get("current_question_index", 0))
    return index >= len(questions)


def build_progress_text(state: dict, lesson_kb: dict) -> str:
    questions = lesson_kb.get("questions", [])
    total_questions = len(questions)
    current_index = int(state.get("current_question_index", 0))
    finished = is_session_finished(state, lesson_kb)

    if finished:
        return f"已完成全部 {total_questions} 题。"

    current_no = current_index + 1
    attempt_count = int(state.get("attempt_count", 0))
    remain_attempts = max(0, 2 - attempt_count)
    return f"当前第 {current_no}/{total_questions} 题，本题已作答 {attempt_count} 次，还可作答 {remain_attempts} 次。"


def compute_total_score(state: dict) -> int:
    total = 0
    for record in state.get("question_records", []):
        score = record.get("final_score", 0)
        try:
            score = int(score)
        except (TypeError, ValueError):
            score = 0
        total += score
    return total


def build_final_summary(state: dict, lesson_kb: dict) -> str:
    total_score = compute_total_score(state)
    total_questions = len(lesson_kb.get("questions", []))
    full_score = total_questions * 5

    if total_score >= full_score:
        comment = "推理完整，杠杆与力矩叠加掌握较好。"
    elif total_score >= max(1, full_score - 2):
        comment = "整体较好，注意多物体力矩合并细节。"
    elif total_score >= max(1, full_score // 2):
        comment = "有一定基础，需加强平衡条件与方向判断。"
    else:
        comment = "建议回顾杠杆平衡和总力矩计算方法。"

    return f"两题作答结束，总分 {total_score}/{full_score}。总评：{comment[:50]}"