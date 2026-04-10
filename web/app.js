const LESSON_KB = {
  lesson_name: "杠杆平衡与多物体力矩叠加",
  questions: [
    {
      id: 1,
      question: "把5kg物体挂在左边距离中点50cm的位置，若右边距离中点10cm的位置已经放了10kg的物品，假如你还有50kg的物品，你会放在什么位置？为什么？",
    },
    {
      id: 2,
      question: "把5kg物体挂在左边距离中点50cm的位置，若右边距离中点10cm的位置已经放了10kg的物品，如果你只能再在右边距离中点15cm处放一个物品，物品应该是多少kg？为什么？",
    },
  ],
};

const state = { session: null, chat: [] };
const el = (id) => document.getElementById(id);

function createInitialState(studentId) {
  return { studentId, currentQuestionIndex: 0, attemptCount: 0, finished: false, questionRecords: [] };
}

function getCurrentQuestion(s) {
  return LESSON_KB.questions[s.currentQuestionIndex] || null;
}

function progressText(s) {
  if (s.finished || s.currentQuestionIndex >= LESSON_KB.questions.length) return `已完成全部 ${LESSON_KB.questions.length} 题。`;
  return `当前第 ${s.currentQuestionIndex + 1}/${LESSON_KB.questions.length} 题，本题已作答 ${s.attemptCount} 次，还可作答 ${Math.max(0, 2 - s.attemptCount)} 次。`;
}

function containsAny(text, words) { return words.some((w) => text.includes(w)); }

function fallbackJudge(qid, raw) {
  const answer = (raw || "").replaceAll(" ", "");
  let score = 1;
  const matched_points = [], missing_points = [], incorrect_points = [];

  if (qid === 1) {
    const has3 = containsAny(answer, ["3cm", "3厘米", "3公分", "三厘米"]);
    const hasRight = answer.includes("右");
    const hasReason = containsAny(answer, ["平衡", "相等", "杠杆", "力矩", "乘", "×"]);
    if (has3) matched_points.push("答出了3cm这个关键数值"); else missing_points.push("没有答出正确位置3cm");
    if (hasRight) matched_points.push("说明了应放在右边"); else missing_points.push("没有明确说明放在右边");
    if (hasReason) matched_points.push("尝试用杠杆平衡条件解释理由"); else missing_points.push("没有根据杠杆平衡条件说明理由");
    score = has3 && hasRight && hasReason ? 5 : has3 ? 3 : 1;
  } else {
    const has10 = containsAny(answer, ["10kg", "10千克", "10公斤", "十千克", "十公斤"]);
    const has15 = containsAny(answer, ["15cm", "15厘米", "15公分", "十五厘米", "15"]);
    const hasReason = containsAny(answer, ["平衡", "相等", "杠杆", "力矩", "乘", "×"]);
    if (has10) matched_points.push("答出了10kg这个关键数值"); else missing_points.push("没有答出正确重量10kg");
    if (has15) matched_points.push("能对应到右边15cm处这个位置"); else missing_points.push("没有结合右边15cm处这个已知位置分析");
    if (hasReason) matched_points.push("尝试用杠杆平衡条件解释理由"); else missing_points.push("没有根据杠杆平衡条件说明理由");
    score = has10 && hasReason ? 5 : has10 ? 3 : 1;
  }

  return {
    score,
    matched_points,
    missing_points,
    incorrect_points,
    is_goal_reached: score === 5,
    brief_comment: score === 5 ? "答案正确且解释较完整。" : score === 3 ? "结果基本正确，但理由还可以更完整。" : "目前答案还不够准确，需要继续思考。",
  };
}

function fallbackAnalyze(judge, attemptCount) {
  if (judge.score === 5) return { guidance_message: "你的思路已经比较完整，可以继续保持这种先比较左右总效果再下结论的方法。" };
  if (attemptCount >= 2) return { guidance_message: "记住：不能只看一个物体，要比较左边总效果和右边两个物体效果之和是否相等。" };
  return { guidance_message: "请先算左边总效果，再考虑右边已有部分，差值由新增物体补足。" };
}

async function callLLMJson(system, prompt) {
  const cfg = window.APP_CONFIG || {};
  if (!cfg.API_KEY) throw new Error("API_KEY not set");
  const r = await fetch(`${cfg.BASE_URL || "https://api.deepseek.com"}/chat/completions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${cfg.API_KEY}`,
    },
    body: JSON.stringify({
      model: cfg.MODEL || "deepseek-chat",
      messages: [{ role: "system", content: system }, { role: "user", content: prompt }],
      temperature: 0.2,
    }),
  });
  const data = await r.json();
  const text = data?.choices?.[0]?.message?.content || "{}";
  const match = text.match(/\{[\s\S]*\}/);
  return JSON.parse(match ? match[0] : text);
}

async function judgeAgent(question, answer) {
  try {
    return await callLLMJson("你是一个严格遵守JSON输出格式的教学辅助智能体。", `请评分，输出字段: score,matched_points,missing_points,incorrect_points,is_goal_reached,brief_comment。题目：${question.question} 学生答案：${answer}`);
  } catch {
    return fallbackJudge(question.id, answer);
  }
}

async function analyzeAgent(question, answer, judge, attemptCount) {
  try {
    return await callLLMJson("你是一个严格遵守JSON输出格式的教学辅助智能体。", `请分析并输出 guidance_message。题目：${question.question} 学生答案：${answer} 评分：${JSON.stringify(judge)} 第${attemptCount}次作答`);
  } catch {
    return fallbackAnalyze(judge, attemptCount);
  }
}

function pushChat(role, text) {
  state.chat.push({ role, text });
  const chat = el("chat");
  chat.innerHTML = state.chat.map((m) => `<div class="msg ${m.role === "学生" ? "user" : "bot"}"><b>${m.role}：</b>${m.text}</div>`).join("");
  chat.scrollTop = chat.scrollHeight;
}

function appendLog(payload) {
  const key = `logs:${state.session?.studentId || "unknown"}`;
  const logs = JSON.parse(localStorage.getItem(key) || "[]");
  logs.push({ timestamp: new Date().toISOString(), ...payload });
  localStorage.setItem(key, JSON.stringify(logs));
}

async function submitAnswer() {
  if (!state.session) return;
  const answer = el("answerInput").value.trim();
  if (!answer) return;
  el("answerInput").value = "";
  pushChat("学生", answer);

  const s = state.session;
  const q = getCurrentQuestion(s);
  if (!q) return;

  const attempt = s.attemptCount + 1;
  const judge = await judgeAgent(q, answer);
  const analysis = await analyzeAgent(q, answer, judge, attempt);
  s.attemptCount = attempt;

  const reply = [`【本次评分】${judge.score || 1}分`, `【点评】${judge.brief_comment || "请继续完善你的回答。"}`];
  const done = attempt >= 2 || judge.is_goal_reached;
  if (done) {
    s.currentQuestionIndex += 1;
    s.attemptCount = 0;
    if (s.currentQuestionIndex >= LESSON_KB.questions.length) {
      s.finished = true;
      reply.push("【总评】两题作答结束。建议继续巩固“左右总力矩相等”。");
    } else {
      reply.push(`【下一题】${getCurrentQuestion(s).question}`);
    }
  } else {
    reply.push(`【引导】${analysis.guidance_message}`);
  }

  pushChat("系统", reply.join("\n"));
  el("status").textContent = progressText(s);
  appendLog({ event: "student_answer", answer, judge, analysis, state: s });
}

function startSession() {
  const studentId = el("studentId").value.trim();
  if (!studentId) return;
  state.session = createInitialState(studentId);
  state.chat = [];
  pushChat("系统", `欢迎进入三智能体协同的学生科学推理能力辅助系统。\n\n【第1题】${getCurrentQuestion(state.session).question}`);
  el("status").textContent = progressText(state.session);
  appendLog({ event: "start_session", state: state.session });
}

function clearUI() {
  state.session = null;
  state.chat = [];
  el("chat").innerHTML = "";
  el("status").textContent = "已清空，请重新输入学生ID并点击开始答题。";
  el("answerInput").value = "";
}

function loadLogs() {
  const studentId = el("studentId").value.trim() || state.session?.studentId || "unknown";
  const logs = JSON.parse(localStorage.getItem(`logs:${studentId}`) || "[]");
  el("logsBox").textContent = logs.length ? logs.map((x) => JSON.stringify(x)).join("\n") : "暂无日志。";
}

el("startBtn").addEventListener("click", startSession);
el("sendBtn").addEventListener("click", submitAnswer);
el("clearBtn").addEventListener("click", clearUI);
el("loadLogsBtn").addEventListener("click", loadLogs);
el("answerInput").addEventListener("keydown", (e) => {
  if (e.key === "Enter") submitAnswer();
});
