// Mock window.claude db for local QA. window.__MOCK = {quizzes:n, mode}
(() => {
  const P = window.__MOCK || {};
  const N = P.quizzes ?? 45, now = Date.now();
  const subs = ["ECON 3010", "PSYC 2005", "SOC 2870", "ANTH 2444", "Linear Algebra"];
  const docs = new Map();           // path -> data
  const writes = [];                // log of set/update/delete
  window.__writes = writes; window.__docs = docs;
  const iso = ms => new Date(ms).toISOString();
  const mcq = (i) => ({ prompt: `Q${i}: If demand is **elastic** and price rises 10%, what happens to revenue with $\\frac{\\partial R}{\\partial P}<0$?`, choices: ["Rises", "Falls", "Unchanged", "Doubles"], answer: "B", explanation: "Elastic demand means quantity falls by more than 10%, so revenue falls." });
  const shortq = { prompt: "Name the curve that shows combinations of two goods giving equal utility.", answer: "indifference curve", accept: ["IC"], explanation: "Indifference curves hold utility constant." };
  const tblq = { prompt: "Using the schedule, what is the arc elasticity between $4 and $5?", table: { headers: ["Price", "Qty"], rows: [["$4", "100"], ["$5", "80"]] }, choices: ["-1", "-0.5", "-2", "-1.5"], answer: "A", explanation: "Midpoint: (-20/90)/(1/4.5) = -1." };
  const longq = { prompt: "A long scrolling prompt. " + "The economy is described by a set of equations relating consumption, investment, and output, and the central bank sets the interest rate according to a rule. ".repeat(6) + "Which statement is right?", choices: ["Output rises", "Output falls", "No change", "Ambiguous"], answer: "D", explanation: "Depends on parameters." };
  const graphq = { type: "graph", prompt: "Sketch $y=(x-2)^2-1$ and mark the vertex.", graph: { xMin: -2, xMax: 6, yMin: -3, yMax: 8, xStep: 1, yStep: 1, xLabel: "x", yLabel: "y", answer: { curves: [{ fn: "(x-2)^2-1" }], dots: [{ x: 2, y: -1 }] } }, answer: "Parabola opening up, vertex (2,-1)", explanation: "Shift right 2, down 1." };
  const frqq = { type: "frq", prompt: "A city taxes sellers of coffee $2. Explain who bears the burden and why.", points: 6, rubric: ["Says incidence depends on relative elasticity (2)", "Explains the less elastic side bears more (2)", { text: "Applies it to the coffee market", pts: 2 }], explanation: "Full credit names the mechanism and applies it." };
  const quizzes = [];
  for (let i = 0; i < N; i++){
    const subject = subs[i % subs.length], t = now - i * 3.7 * 3600e3;
    const v = i % 9, qs = [mcq(`1.${v}`), tblq, mcq(`2.${v}`), shortq, mcq(`3.${v}`), longq, mcq(`4.${v}`)];
    if (i % 3 === 0) qs.push(graphq);
    if (i % 4 === 0) qs.push(frqq);
    const id = `${subject.toLowerCase().replace(/[^a-z0-9]+/g, "")}-t${i}-20261123a`;
    const q = { title: `Mock quiz ${i} · ${subject}`, subject, createdAt: iso(t), questions: qs };
    if (i === 7) q.kind = "test";
    if (i === 2) q.kind = "compound";
    if (i === 1) q.availableAt = iso(now + 2 * 3600e3);
    quizzes.push([id, q]);
    if (P.mode !== "noresults" && i > 1){
      const items = qs.map((x, k) => ({ n: k + 1, prompt: x.prompt, yourAnswer: "B. Falls", correctAnswer: "B. Falls", correct: (i + k) % 3 !== 0, flagged: k === 2, seconds: 8 + ((i * 7 + k * 13) % 50), ...(x.type === "frq" ? { type: "frq", points: 6, pointsEarned: 4, rubric: [] } : {}) }));
      const score = items.filter(x => x.correct).length;
      docs.set("results/" + id, { quizId: id, title: q.title, subject, topic: "", finishedAt: iso(t + 1800e3), score, total: items.length, needsSelfCheck: 0, history: [{ at: iso(t + 1800e3), score, total: items.length }], totalSeconds: 400, items });
    }
  }
  if (P.mode !== "noquiz") quizzes.forEach(([id, q]) => docs.set("quizzes/" + id, q));
  docs.set("rubrics/econ-3010", { subject: "ECON 3010", key: "econ-3010", updatedAt: iso(now), markdown: "# ECON 3010 FRQs\n- Reward labeled graphs\n- State the mechanism before the example" });
  docs.set("meta/folders", { folders: { f1: { id: "f1", name: "Unit 2", subject: "econ-3010", color: "#8ec5ff" } }, assign: {} });

  const listeners = [];   // {kind:'col'|'doc', path, cb}
  const snapDoc = (path) => { const d = docs.get(path); return { id: path.split("/").pop(), exists: d !== undefined, data: () => d === undefined ? undefined : JSON.parse(JSON.stringify(d)), metadata: { fromCache: false } }; };
  const snapCol = (col) => { const out = []; for (const [p, d] of docs) if (p.startsWith(col + "/") && p.split("/").length === 2) out.push({ id: p.slice(col.length + 1), data: () => JSON.parse(JSON.stringify(d)) }); return { docs: out, metadata: { fromCache: false } }; };
  const fire = (path) => listeners.forEach(l => { if (l.kind === "doc" && l.path === path) l.cb(snapDoc(path)); if (l.kind === "col" && path.startsWith(l.path + "/")) l.cb(snapCol(l.path)); });
  window.__fire = fire;
  const delay = (v) => new Promise(r => setTimeout(() => r(v), 5));
  const db = {
    collection(c){ const q = { orderBy: () => q, limit: () => q, onSnapshot(cb, err){ listeners.push({ kind: "col", path: c, cb }); setTimeout(() => cb(snapCol(c)), 20); return () => {}; } }; return q; },
    doc(path){ return {
      get: () => delay(snapDoc(path)),
      set: (d) => { writes.push(["set", path, d]); docs.set(path, JSON.parse(JSON.stringify(d))); setTimeout(() => fire(path), 5); return delay(); },
      update: (d) => { writes.push(["update", path, d]); docs.set(path, { ...(docs.get(path) || {}), ...JSON.parse(JSON.stringify(d)) }); setTimeout(() => fire(path), 5); return delay(); },
      delete: () => { writes.push(["delete", path]); docs.delete(path); setTimeout(() => fire(path), 5); return delay(); },
      onSnapshot(cb){ listeners.push({ kind: "doc", path, cb }); setTimeout(() => cb(snapDoc(path)), 20); return () => {}; }
    }; }
  };
  window.claude = { use: async (n) => n === "db" ? db : null };
})();
