import json


def _to_json_text(data):
    return json.dumps(data, ensure_ascii=False, indent=2)


def build_judge_prompt(question_data, student_answer):
    judge_schema = {
        "score": 0,
        "matched_points": ["学生答案中已达到的要点，列表"],
        "missing_points": ["学生答案中缺失的要点，列表"],
        "incorrect_points": ["学生答案中的错误或不严谨之处，列表"],
        "is_goal_reached": False,
        "brief_comment": "不超过40字的中文评价"
    }

    instructions = {
        "任务": "你是判断模块，负责依据标准答案与评分要点评估学生作答质量。",
        "评分原则": [
            "只根据题目、标准答案、评分要点和学生答案评分。",
            "分数使用0到满分之间的整数。",
            "若核心结论错误，通常不能判定为达到目标。",
            "若只有结论没有过程，可给部分分，但不应给满分。",
            "优先检查是否正确使用“力矩=重量×距离”以及是否比较左右总力矩。",
            "输出必须是严格JSON，不要包含代码块、解释性文字或额外前后缀。"
        ],
        "输出字段要求": {
            "score": "整数",
            "matched_points": "字符串列表",
            "missing_points": "字符串列表",
            "incorrect_points": "字符串列表",
            "is_goal_reached": "布尔值，达到本题目标填true，否则false",
            "brief_comment": "简短中文评价"
        }
    }

    payload = {
        "instruction": instructions,
        "question_data": question_data,
        "student_answer": student_answer,
        "json_schema_example": judge_schema
    }

    return (
        "请严格按要求完成判断任务，并只输出JSON对象。\n"
        + _to_json_text(payload)
    )


def build_analyzer_prompt(question_data, student_answer, judge_result, attempt_count):
    analyzer_schema = {
        "reasoning_stage": "observation",
        "stage_description": "学生当前所处推理阶段的中文描述",
        "guidance_type": "concept_hint",
        "guidance_message": "面向学生的中文引导语，不直接整段给出标准答案"
    }

    instructions = {
        "任务": "你是分析模块，负责根据学生答案、判断结果和作答轮次分析其推理阶段，并生成一次中文引导。",
        "轮次规则": [
            "attempt_count=1 表示学生刚完成第1次作答，此时若未达标，应提供启发式引导。",
            "attempt_count>=2 时，引导应更聚焦关键错误，但仍避免直接照抄完整标准答案。",
            "若判断结果已达到目标，也要简要指出其所处阶段，并给出肯定性反馈。"
        ],
        "可用推理阶段": [
            "observation",
            "concept_activation",
            "single_torque_calc",
            "multi_torque_sum",
            "comparison_and_conclusion"
        ],
        "guidance_type建议": [
            "affirmation",
            "observation_hint",
            "concept_hint",
            "calculation_hint",
            "comparison_hint",
            "error_correction"
        ],
        "引导原则": [
            "全程使用中文。",
            "引导语要短、清晰、适合学生阅读。",
            "优先指出下一步该想什么，而不是直接报最终答案。",
            "如果是多物体题，要特别关注是否遗漏“分别计算再相加”。",
            "输出必须是严格JSON，不要包含代码块、解释性文字或额外前后缀。"
        ],
        "输出字段要求": {
            "reasoning_stage": "上述阶段之一",
            "stage_description": "中文描述学生当前阶段",
            "guidance_type": "引导类型字符串",
            "guidance_message": "给学生看的中文引导语"
        }
    }

    payload = {
        "instruction": instructions,
        "question_data": question_data,
        "student_answer": student_answer,
        "judge_result": judge_result,
        "attempt_count": attempt_count,
        "json_schema_example": analyzer_schema
    }

    return (
        "请严格按要求完成分析任务，并只输出JSON对象。\n"
        + _to_json_text(payload)
    )