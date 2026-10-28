/* Письменный разбор контрольной для пятерых. Запуск из корня: node сборка/build_kontrol_reports.js */
const fs = require("fs");
const path = require("path");
const root = path.join(__dirname, "..");
const Q = require(path.join(root, "quiz_core.js"));

const students = fs.readFileSync(path.join(root, "students.js"), "utf8")
  .replace(/^window\.QUIZ_STUDENTS = /, "")
  .replace(/;\s*$/, "");
const all = JSON.parse(students);
const team = [
  "Подъячий Глеб Русланович",
  "Керимов Андрей Эдуардович",
  "Мамбетов Родион Рудемович",
  "Черакаев Антон Александрович",
  "Кулиш Артём Евгеньевич"
];
const outDir = path.join(root, "контрольная");
fs.mkdirSync(outDir, { recursive: true });

function esc(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function state(f) {
  if (f.kind === "count") return "C: " + Q.fmt(f.c) + " | B: " + Q.fmt(f.b);
  if (f.kind === "recur") return "";
  return Q.fmt(f.a || []);
}

function fileBase(name) {
  const parts = name.split(" ");
  return parts[0] + "_" + parts[1];
}

function report(student) {
  const work = Q.buildWork(student);
  const tasks = work.tasks.map(function (task) {
    const frames = Q.flatFrames(task);
    const intro = frames[0].text;
    const outro = frames[frames.length - 1].text;
    const rows = frames.map(function (f, i) {
      const cut = f.title.indexOf("Неубывающая пирамида, исходный") === 0 && i > 0
        ? "<tr><td colspan='3'><b>Второй случай: неубывающая пирамида</b></td></tr>"
        : "";
      if (f.kind === "recur") {
        return cut + "<tr><td>" + (i + 1) + "</td><td colspan='2'><b>" + esc(f.title) + "</b><br>" + esc(f.text) + "</td></tr>";
      }
      return cut + "<tr><td>" + (i + 1) + "</td><td>" + esc(f.title) + "</td><td class='mono'>" + esc(state(f)) + "</td></tr>";
    }).join("");
    const pointsWord = task.points === 1 ? "балл" : (task.points < 5 ? "балла" : "баллов");
    return "<section class='task'><h2>" + esc(task.title) + " (" + task.points + " " + pointsWord + ")</h2><p>" + esc(intro) + "</p><table><tr><th>Шаг</th><th>Что происходит</th><th>Состояние</th></tr>" + rows + "</table><p><b>Итог.</b> " + esc(outro) + "</p></section>";
  }).join("");

  return "<!DOCTYPE html><html lang='ru'><head><meta charset='utf-8'><title>Контрольная, " + esc(student.name) + "</title><style>" +
    "@page { size: A4; margin: 12mm; } body { font-family: 'Times New Roman', Times, serif; font-size: 12pt; color: #111; } h1 { font-size: 16pt; margin: 0 0 6px; } h2 { font-size: 13pt; margin: 0 0 6px; } p { margin: 0 0 8px; } table { width: 100%; border-collapse: collapse; margin: 6px 0 8px; } th, td { border: 1px solid #888; padding: 2px 4px; vertical-align: top; font-size: 10pt; } th { background: #f3e3d4; } .mono { font-family: Consolas, 'Courier New', monospace; } .task { break-before: page; } section.task:first-of-type { break-before: auto; }</style></head><body>" +
    "<h1>Контрольная работа</h1>" +
    "<p>Дисциплина: Алгоритмы и структуры данных. Тема: алгоритмическая сложность, алгоритмы сортировки. Группа И-1-24. Срок в задании: 29.11.2026.</p>" +
    "<p><b>" + esc(student.name) + "</b>. Вариант " + student.variant + ".</p>" +
    "<p>Массив слева направо: " + student.arr.join(", ") + ". В таблице преподавателя это столбцы a0...a9. В разборе индексы с 1, как в лабораторных: A[1] = " + student.arr[0] + ".</p>" +
    "<p>Задание 6: k = 5. Задание 7: a = " + student.pa + ", b = " + student.pb + ", c &gt; 1.</p>" +
    "<p>Формат сдачи отдельно не называли. Ниже письменный разбор всех семи заданий: что делает шаг и каким становится массив. Те же шаги листаются на сайте команды, вкладка «контрольная».</p>" +
    tasks +
    "</body></html>";
}

team.forEach(function (name) {
  const student = all.find(function (s) { return s.name === name; });
  if (!student) throw new Error("нет строки " + name);
  const htmlPath = path.join(outDir, fileBase(name) + ".html");
  fs.writeFileSync(htmlPath, report(student), "utf8");
  console.log(htmlPath);
});
