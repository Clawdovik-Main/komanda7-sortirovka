"""Собирает отчёт, презентацию, графики и формы команды 7 из results/raw.txt."""
import html
import subprocess
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor
from pptx import Presentation
from pptx.dml.color import RGBColor as PptColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Cm as Pcm, Pt as Ppt

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
NAVY = "16324F"
GOLD = "A56B12"

LABELS = {
    "python": "Python list.sort",
    "javascript": "JavaScript sort",
    "java_int": "Java int[]",
    "java_object": "Java Integer[]",
    "csharp": "C# Array.Sort",
    "cpp_sort": "C++ std::sort",
    "cpp_stable": "C++ stable_sort",
}
ORDER = ["cpp_sort", "csharp", "java_int", "cpp_stable", "javascript", "java_object", "python"]
PATTERNS = [
    ("random", "Случайные"),
    ("sorted", "По возрастанию"),
    ("reversed", "По убыванию"),
    ("few_unique", "Мало разных"),
    ("nearly_sorted", "Почти упорядочен"),
]


def parse():
    times = {}
    stable = {}
    for line in (RESULTS / "raw.txt").read_text(encoding="utf-8").splitlines():
        parts = line.split("\t")
        if not parts or not parts[0]:
            continue
        if parts[0] == "TIME":
            times[(parts[1], parts[2], int(parts[3]))] = float(parts[4].replace(",", "."))
        elif parts[0] == "STABLE":
            stable[parts[1]] = parts[2].strip()
    return times, stable


def fmt(ms):
    if ms >= 100:
        return str(int(round(ms)))
    if ms >= 10:
        return f"{ms:.1f}".replace(".", ",")
    return f"{ms:.2f}".replace(".", ",")


def chart(times, pattern, title, path):
    labels = [LABELS[key] for key in ORDER]
    values = [times[(key, pattern, 1_000_000)] for key in ORDER]
    colors = ["#1a6b8a", "#2f6f4e", "#8c3a4b", "#5c6b73", "#a56b12", "#6c3483", "#1c2830"]
    fig, ax = plt.subplots(figsize=(8.2, 4.2))
    bars = ax.barh(labels[::-1], values[::-1], color=colors[::-1])
    ax.set_xlabel("миллисекунды")
    ax.set_title(title)
    for bar, value in zip(bars, values[::-1]):
        ax.text(value + max(values) * 0.01, bar.get_y() + bar.get_height() / 2, fmt(value), va="center", fontsize=9)
    ax.set_xlim(0, max(values) * 1.18)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close()


def add_p(doc, text, bold=False, center=False, size=14):
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.space_after = Pt(6)
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.line_spacing = 1.15
    if center:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run(text)
    run.bold = bold
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor(0x1C, 0x28, 0x30)
    return paragraph


def shade_header(cell):
    cell.paragraphs[0].runs[0].bold = True
    cell.paragraphs[0].runs[0].font.name = "Times New Roman"
    cell.paragraphs[0].runs[0].font.size = Pt(12)


def set_cell(cell, text, bold=False):
    cell.text = ""
    paragraph = cell.paragraphs[0]
    run = paragraph.add_run(text)
    run.bold = bold
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)


def build_report(times):
    doc = Document()
    for section in doc.sections:
        section.top_margin = Cm(1.8)
        section.bottom_margin = Cm(1.8)
        section.left_margin = Cm(2)
        section.right_margin = Cm(1.8)
    add_p(doc, "МИНИСТЕРСТВО ОБРАЗОВАНИЯ И НАУКИ РЕСПУБЛИКИ КРЫМ", center=True, size=12)
    add_p(doc, "ГБОУВО РК «Крымский инженерно-педагогический университет имени Февзи Якубова»", center=True, size=12)
    add_p(doc, "ОТЧЁТ", bold=True, center=True, size=18)
    add_p(doc, "Групповой проект. Команда 7", bold=True, center=True)
    add_p(doc, "Сортировка в современных языках программирования", bold=True, center=True)
    add_p(doc, "Дисциплина: Алгоритмы и структуры данных", center=True, size=12)
    add_p(doc, "Преподаватель: Меметов М. Р.", center=True, size=12)
    add_p(doc, "Симферополь, 2026", center=True, size=12)

    add_p(doc, "1. Состав команды и цель", bold=True)
    add_p(doc, "Лидер команды: Подъячий Глеб Русланович. Участники: Керимов Андрей Эдуардович, Мамбетов Родион Рудемович, Черакаев Антон Александрович, Кулиш Артём Евгеньевич.")
    add_p(doc, "Цель: выяснить, какой алгоритм спрятан во встроенной сортировке Python, Java, C#, JavaScript и C++, и проверить на одних и тех же массивах, чем эти реализации отличаются по времени и по устойчивости.")

    add_p(doc, "2. Какие алгоритмы лежат в основе", bold=True)
    add_p(doc, "Python 3.14, list.sort и sorted. Это устойчивая адаптивная сортировка слиянием семейства Timsort. Короткие куски добираются вставками. С версии 3.11 порядок слияния уже готовых серий выбирает стратегия Powersort. На полностью упорядоченном массиве хватает одного прохода, время близко к линейному. Дополнительная память до O(n).")
    add_p(doc, "Java 17. У одного класса Arrays.sort два разных алгоритма. Для массива чисел int, long, float, double используется Dual-Pivot Quicksort Ярославского, Бентли и Блоха. Он не устойчивый: у одинаковых чисел нет отдельной «личности». Внутри есть вставки на коротких кусках, переход к пирамиде при плохой рекурсии и склейка уже готовых серий. Для массива объектов используется устойчивый Timsort.")
    add_p(doc, "C#, Array.Sort. С .NET Framework 4.5 это introsort: быстрая сортировка, вставки на кусках не длиннее 16 элементов и пирамида, если глубина рекурсии слишком большая. Худшее время O(n log n). Сортировка не устойчива. Устойчивый порядок даёт LINQ OrderBy: при равных ключах сравнение возвращается к исходному номеру элемента.")
    add_p(doc, "JavaScript. Стандарт ES2019 требует устойчивость, но не назначает алгоритм. Node.js 24 и Chrome используют движок V8, а в нём с версии 7.0 стоит Timsort. Firefox и Safari решают ту же задачу другим устойчивым слиянием. Отдельная ловушка: без функции сравнения числа сортируются как строки, и 10 оказывается раньше 2.")
    add_p(doc, "C++, компилятор Microsoft Visual C++ 2022. std::sort это introsort: быстрая сортировка, вставки до 32 элементов и пирамида при слишком глубокой рекурсии. Сортировка на месте и не устойчива. std::stable_sort это сортировка слиянием. Если хватает дополнительной памяти, время O(n log n), иначе стандарт разрешает O(n log n · log n).")

    add_p(doc, "3. Сложность", bold=True)
    rows = [
        ("Реализация", "Алгоритм", "Время", "Память", "Устойчивость"),
        ("Python list.sort", "Timsort, Powersort", "O(n log n), на серии O(n)", "O(n)", "да"),
        ("Java int[]", "Dual-Pivot Quicksort", "O(n log n)", "O(log n)", "нет"),
        ("Java Integer[]", "Timsort", "O(n log n), на серии O(n)", "O(n)", "да"),
        ("C# Array.Sort", "introsort", "O(n log n)", "O(log n)", "нет"),
        ("JavaScript, V8", "Timsort", "O(n log n), на серии O(n)", "O(n)", "да"),
        ("C++ std::sort", "introsort", "O(n log n)", "O(log n)", "нет"),
        ("C++ stable_sort", "слияние", "O(n log n)", "O(n)", "да"),
    ]
    table = doc.add_table(rows=len(rows), cols=5)
    table.style = "Table Grid"
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            set_cell(table.rows[r].cells[c], value, bold=(r == 0))
    add_p(doc, "O здесь верхняя оценка. Для Timsort на случайных данных она совпадает с точным порядком Θ(n log n). На уже упорядоченных данных адаптивные алгоритмы уходят к Θ(n). Introsort и Dual-Pivot Quicksort держат O(n log n) и в плохом случае, потому что глубокая рекурсия обрывается пирамидой.")

    add_p(doc, "4. Программа", bold=True)
    add_p(doc, "Скрипт run_bench.py один раз строит массивы генератором с фиксированным зерном 7. Пять видов данных: случайные числа, возрастание, убывание, всего 10 разных значений и почти упорядоченный массив, в котором переставлен каждый 50-й элемент. Размеры: 10 тысяч, 100 тысяч и 1 миллион. Один и тот же файл читают Python, Node.js, Java, C# и C++. Время первой попытки отбрасывается как прогрев. Дальше берётся медиана пяти замеров. В замер входит только вызов встроенной сортировки, не чтение файла.")
    add_p(doc, "Устойчивость проверяется отдельно. Четыреста пар «значение, исходный номер» сортируются только по значению. Если внутри равных чисел номера идут по возрастанию, прежний порядок сохранён.")

    add_p(doc, "5. Результаты", bold=True)
    add_p(doc, "Таблица ниже: медиана времени в миллисекундах при n = 1 000 000. Машина: Windows, Python 3.14.2, Node.js 24.11.1, Java 17.0.12, .NET Framework и MSVC 19.44.")
    header = ["Реализация"] + [title for _, title in PATTERNS]
    data_rows = [header]
    for key in ORDER:
        data_rows.append([LABELS[key]] + [fmt(times[(key, pattern, 1_000_000)]) for pattern, _ in PATTERNS])
    table = doc.add_table(rows=len(data_rows), cols=len(header))
    table.style = "Table Grid"
    for r, row in enumerate(data_rows):
        for c, value in enumerate(row):
            set_cell(table.rows[r].cells[c], value, bold=(r == 0))
    add_p(doc, "На случайном миллионе самые быстрые три реализации близки: Java для int 48 мс, C# 48 мс, C++ std::sort 55 мс. Python тратит 277 мс, JavaScript 175 мс, Java для объектов 260 мс. Разрыв здесь в основном из-за сравнения объектов и устройства языка, а не из-за того, что Timsort «плохой». На тех же случайных данных рост от 100 тысяч к миллиону у C++ около 12 раз, у Python около 14 раз. Это согласуется с n log n: при росте n в 10 раз ждут примерно 12.")
    add_p(doc, "На уже упорядоченном миллионе картина другая. Java для int укладывается в 0,11 мс: готовые серии почти не переставляются. Python делает это за 5,86 мс вместо 277 мс на случайных числах. Почти упорядоченный массив тоже сильно быстрее случайного у всех адаптивных реализаций.")
    add_p(doc, "Проверка устойчивости совпала с описанием алгоритмов. Python, JavaScript, Java для объектов и C++ stable_sort порядок равных элементов сохранили. C# Array.Sort и C++ std::sort его сломали: внутри равного значения более поздний элемент оказался левее раннего.")

    add_p(doc, "6. Выводы", bold=True)
    add_p(doc, "Встроенная сортировка это не один алгоритм на все языки. Python, V8 и сортировка объектов в Java устойчивы и хорошо используют готовые куски. C++ std::sort и C# Array.Sort быстрые и на месте, но равные элементы могут поменяться местами. Если порядок равных записей важен, в C++ нужен std::stable_sort, в C# нужен OrderBy, в Java нельзя сортировать числа и объекты как одну и ту же функцию. В JavaScript числовой массив сортируют только с функцией сравнения (a, b) => a - b.")
    add_p(doc, "Практическая рекомендация. Большой массив чисел и устойчивость не нужна: std::sort, Array.Sort или Arrays.sort для int. Уже почти упорядоченные данные или равные элементы с собственным смыслом: list.sort, Array.prototype.sort или Arrays.sort для объектов. Выбор самой быстрой сортировки без этих двух условий даёт неверный ответ.")

    add_p(doc, "Источники", bold=True)
    for item in [
        "Python Software Foundation. Objects/listsort.txt. Описание Timsort и переход на Powersort в CPython 3.11.",
        "Oracle. Arrays, Java SE 17. Implementation Note для Dual-Pivot Quicksort и Timsort.",
        "Microsoft. Array.Sort, .NET. Introsort: вставки, быстрая сортировка и пирамида.",
        "V8 team. Getting things sorted in V8. Переход Array.prototype.sort на устойчивый Timsort.",
        "MDN. Array.prototype.sort. Устойчивость обязательна с ECMAScript 2019.",
        "ISO/IEC 14882. std::sort и std::stable_sort: сложность и требование устойчивости.",
    ]:
        add_p(doc, item, size=12)
    path = ROOT / "Отчет_команда7.docx"
    doc.save(path)
    return path


PEOPLE = [
    {
        "file": "Подъячий_Глеб",
        "name": "Подъячий Глеб Русланович",
        "roles": "Лидер команды, исследователь, докладчик",
        "topic": "Python и общие выводы",
        "tasks": [
            ("Распределил пять языков по участникам", "У каждого есть своя часть на 1 минуту"),
            ("Разобрал list.sort в Python 3.14", "Timsort и Powersort, устойчивость подтверждена"),
            ("Собрал итоговые рекомендации", "Когда брать устойчивую сортировку, а когда нет"),
        ],
        "hard": "Нужно было не смешать пять языков в один рассказ и оставить каждому понятный кусок.",
        "best": "Общая таблица: по ней сразу видно, где алгоритм устойчивый.",
    },
    {
        "file": "Керимов_Андрей",
        "name": "Керимов Андрей Эдуардович",
        "roles": "Исследователь, разработчик, докладчик",
        "topic": "Java, два алгоритма в Arrays.sort",
        "tasks": [
            ("Разобрал Arrays.sort для int[]", "Dual-Pivot Quicksort, 48 мс на случайном миллионе"),
            ("Разобрал Arrays.sort для Integer[]", "Timsort, на том же массиве 260 мс"),
            ("Проверил устойчивость объектов", "Порядок равных элементов сохранился"),
        ],
        "hard": "В документации легко решить, что в Java один алгоритм. На самом деле их два.",
        "best": "Наглядная разница 48 мс и 260 мс на одном и том же миллионе чисел.",
    },
    {
        "file": "Мамбетов_Родион",
        "name": "Мамбетов Родион Рудемович",
        "roles": "Исследователь, разработчик, докладчик",
        "topic": "C# Array.Sort и OrderBy",
        "tasks": [
            ("Разобрал Array.Sort", "introsort: быстрая сортировка, вставки и пирамида"),
            ("Отделил OrderBy от Array.Sort", "OrderBy устойчивый, Array.Sort нет"),
            ("Проверил устойчивость на 400 элементах", "Программа показала, что порядок сломан"),
        ],
        "hard": "Короткий массив сортируется вставками и может случайно сохранить порядок. Проверку пришлось делать на 400 элементах.",
        "best": "Чёткое правило для защиты: нужен прежний порядок равных записей, вызываем OrderBy.",
    },
    {
        "file": "Черакаев_Антон",
        "name": "Черакаев Антон Александрович",
        "roles": "Разработчик, исследователь, докладчик",
        "topic": "C++ std::sort и std::stable_sort",
        "tasks": [
            ("Разобрал std::sort в MSVC", "introsort, на месте, не устойчивый"),
            ("Сравнил его со std::stable_sort", "Слияние, порядок равных сохраняется"),
            ("Собрал программу bench.cpp с оптимизацией", "Оба вызова замерены на тех же файлах"),
        ],
        "hard": "std::sort на коротком куске выглядит устойчивым. На 400 элементах неустойчивость уже видна.",
        "best": "Две функции стандартной библиотеки закрывают оба случая: быстро и устойчиво.",
    },
    {
        "file": "Кулиш_Артём",
        "name": "Кулиш Артём Евгеньевич",
        "roles": "Разработчик, исследователь, докладчик",
        "topic": "JavaScript и страница демонстрации",
        "tasks": [
            ("Разобрал Array.prototype.sort в Node.js 24", "V8, Timsort, сортировка устойчивая"),
            ("Показал ловушку без компаратора", "Числа 10, 2, 1 сортируются как строки"),
            ("Собрал страницу demo.html", "На защите видно и ловушку, и таблицу времени"),
        ],
        "hard": "Стандарт требует устойчивость, но не называет алгоритм. Пришлось отдельно указать, что замер сделан в V8, а не во всех браузерах.",
        "best": "Ловушка со строковой сортировкой объясняется за полминуты и сразу запоминается.",
    },
]


def build_person(person):
    doc = Document()
    for section in doc.sections:
        section.top_margin = Cm(1.7)
        section.bottom_margin = Cm(1.7)
        section.left_margin = Cm(2)
        section.right_margin = Cm(2)
    add_p(doc, "Индивидуальный отчёт участника", bold=True, center=True, size=16)
    add_p(doc, "Команда 7. Сортировка в современных языках программирования", center=True, size=12)
    add_p(doc, "ФИО: " + person["name"])
    add_p(doc, "Роль: " + person["roles"])
    add_p(doc, "Тема на защите: " + person["topic"])
    add_p(doc, "Выполненные задачи", bold=True)
    table = doc.add_table(rows=1 + len(person["tasks"]), cols=2)
    table.style = "Table Grid"
    set_cell(table.rows[0].cells[0], "Задача", True)
    set_cell(table.rows[0].cells[1], "Результат", True)
    for index, (task, result) in enumerate(person["tasks"], 1):
        set_cell(table.rows[index].cells[0], task)
        set_cell(table.rows[index].cells[1], result)
    add_p(doc, "Технологии: Python 3.14, Node.js 24, Java 17, C# (.NET Framework), C++ (MSVC 2022), общие массивы в двоичных файлах.")
    add_p(doc, "Сложность: " + person["hard"])
    add_p(doc, "Личный вклад: 20%. Вклад оценивается по своей языковой части и участию в общем эксперименте. Подпись ставится на защите.")
    add_p(doc, "Подпись: ____________________    Дата: 28.10.2026")
    folder = ROOT / "индивидуальные"
    folder.mkdir(exist_ok=True)
    doc.save(folder / f"{person['file']}.docx")


def build_self(person):
    doc = Document()
    for section in doc.sections:
        section.top_margin = Cm(1.5)
        section.bottom_margin = Cm(1.5)
        section.left_margin = Cm(1.8)
        section.right_margin = Cm(1.8)
    add_p(doc, "Форма самооценки и оценки вклада участников команды", bold=True, center=True, size=14)
    add_p(doc, "Дисциплина: Алгоритмы и структуры данных", size=12)
    add_p(doc, "Тема проекта: Сортировка в современных языках программирования", size=12)
    add_p(doc, "Номер команды: 7", size=12)
    add_p(doc, "Лидер команды: Подъячий Глеб Русланович", size=12)
    add_p(doc, "Часть 1. Участник", bold=True)
    add_p(doc, "ФИО: " + person["name"])
    add_p(doc, "Роль: " + person["roles"])
    add_p(doc, "Часть 2. Самооценка", bold=True)
    table = doc.add_table(rows=1 + len(person["tasks"]), cols=2)
    table.style = "Table Grid"
    set_cell(table.rows[0].cells[0], "Выполненная задача", True)
    set_cell(table.rows[0].cells[1], "Результат", True)
    for index, (task, result) in enumerate(person["tasks"], 1):
        set_cell(table.rows[index].cells[0], task)
        set_cell(table.rows[index].cells[1], result)
    scores = [("Выполнение порученных задач", "2"), ("Качество выполненной работы", "2"), ("Соблюдение сроков", "1"), ("Участие в обсуждениях и командной работе", "1"), ("Итого", "6")]
    score_table = doc.add_table(rows=len(scores), cols=2)
    score_table.style = "Table Grid"
    for index, (name, value) in enumerate(scores):
        set_cell(score_table.rows[index].cells[0], name, bold=(name == "Итого"))
        set_cell(score_table.rows[index].cells[1], value, bold=(name == "Итого"))
    add_p(doc, "Оценка собственного вклада: 20%")
    add_p(doc, "Часть 3. Вклад участников, шкала 0-5", bold=True)
    peers = doc.add_table(rows=6, cols=3)
    peers.style = "Table Grid"
    for index, title in enumerate(("ФИО участника", "Балл", "Основной вклад")):
        set_cell(peers.rows[0].cells[index], title, True)
    contributions = [
        ("Подъячий Глеб Русланович", "организация, Python, выводы"),
        ("Керимов Андрей Эдуардович", "Java, два алгоритма Arrays.sort"),
        ("Мамбетов Родион Рудемович", "C# Array.Sort и OrderBy"),
        ("Черакаев Антон Александрович", "C++ std::sort и stable_sort"),
        ("Кулиш Артём Евгеньевич", "JavaScript и демонстрация"),
    ]
    for index, (name, what) in enumerate(contributions, 1):
        set_cell(peers.rows[index].cells[0], name)
        set_cell(peers.rows[index].cells[1], "5")
        set_cell(peers.rows[index].cells[2], what)
    add_p(doc, "Часть 4. Работа команды", bold=True)
    team = [("Эффективность распределения задач", "2"), ("Взаимодействие участников", "2"), ("Соблюдение сроков выполнения проекта", "1"), ("Итого", "5")]
    team_table = doc.add_table(rows=len(team), cols=2)
    team_table.style = "Table Grid"
    for index, (name, value) in enumerate(team):
        set_cell(team_table.rows[index].cells[0], name, bold=(name == "Итого"))
        set_cell(team_table.rows[index].cells[1], value, bold=(name == "Итого"))
    add_p(doc, "Часть 5. Рефлексия", bold=True)
    add_p(doc, "Трудности: " + person["hard"])
    add_p(doc, "Лучше всего получилось: " + person["best"])
    add_p(doc, "Что улучшить: добавить замер памяти и отдельный прогон Firefox, чтобы сравнить его слияние с Timsort в V8.")
    add_p(doc, "Декларация. Подтверждаю, что указанная информация соответствует моему вкладу в проект.")
    add_p(doc, "Подпись: ____________________    Дата: 28.10.2026")
    folder = ROOT / "самооценка"
    folder.mkdir(exist_ok=True)
    doc.save(folder / f"{person['file']}.docx")


def build_roles():
    doc = Document()
    add_p(doc, "Распределение обязанностей. Команда 7", bold=True, center=True, size=16)
    add_p(doc, "Тема: Сортировка в современных языках программирования", center=True)
    add_p(doc, "Лидер: Подъячий Глеб Русланович. Он следит за комплектностью материалов и начинает защиту.")
    table = doc.add_table(rows=1 + len(PEOPLE), cols=3)
    table.style = "Table Grid"
    for index, title in enumerate(("Участник", "Часть проекта", "На защите")):
        set_cell(table.rows[0].cells[index], title, True)
    for index, person in enumerate(PEOPLE, 1):
        set_cell(table.rows[index].cells[0], person["name"])
        set_cell(table.rows[index].cells[1], person["topic"])
        set_cell(table.rows[index].cells[2], "не меньше 1 минуты")
    add_p(doc, "Порядок выступления: Подъячий, Керимов, Мамбетов, Черакаев, Кулиш, затем Подъячий кратко закрывает выводы. Демонстрация: файл demo.html и при необходимости повторный запуск run_bench.py.")
    doc.save(ROOT / "Распределение_обязанностей.docx")


def add_text(slide, text, left, top, width, height, size=20, bold=False, color=NAVY, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(Pcm(left), Pcm(top), Pcm(width), Pcm(height))
    frame = box.text_frame
    frame.word_wrap = True
    paragraph = frame.paragraphs[0]
    paragraph.alignment = align
    run = paragraph.add_run()
    run.text = text
    run.font.size = Ppt(size)
    run.font.bold = bold
    run.font.color.rgb = PptColor.from_string(color)
    run.font.name = "Calibri"
    return frame


def add_bullet(frame, text, size=18):
    paragraph = frame.add_paragraph()
    paragraph.level = 0
    paragraph.text = text
    paragraph.font.size = Ppt(size)
    paragraph.font.color.rgb = PptColor.from_string("1C2830")
    paragraph.font.name = "Calibri"


def build_pptx(times):
    prs = Presentation()
    prs.slide_width = Pcm(33.867)
    prs.slide_height = Pcm(19.05)
    blank = prs.slide_layouts[6]

    def new(bg=NAVY):
        slide = prs.slides.add_slide(blank)
        fill = slide.background.fill
        fill.solid()
        fill.fore_color.rgb = PptColor.from_string(bg)
        return slide

    slide = new()
    add_text(slide, "КОМАНДА 7", 1.4, 3.2, 30, 1.2, 18, color="D5E3EE")
    add_text(slide, "Сортировка в современных\nязыках программирования", 1.4, 4.6, 30, 4, 36, True, "FFFFFF")
    add_text(slide, "Python, Java, C#, JavaScript, C++\nАлгоритмы и структуры данных  ·  28.10.2026", 1.4, 10.2, 30, 2, 18, color="D5E3EE")
    add_text(slide, "Подъячий Глеб  ·  Керимов Андрей  ·  Мамбетов Родион\nЧеракаев Антон  ·  Кулиш Артём", 1.4, 14.2, 30, 2.2, 18, color="FFFFFF")

    slide = new("FFFFFF")
    add_text(slide, "Зачем этот проект", 1.2, 0.7, 30, 1.4, 32, True)
    frame = add_text(slide, "", 1.2, 2.6, 30, 12, 22)
    frame.paragraphs[0].text = "Одинаковое имя sort прячет разные алгоритмы."
    frame.paragraphs[0].font.size = Ppt(24)
    frame.paragraphs[0].font.name = "Calibri"
    for line in [
        "Где-то это устойчивый Timsort, где-то быстрая сортировка с пирамидой на подхвате.",
        "Мы взяли одни и те же массивы и замерили встроенные функции, а не свои реализации.",
        "Два вопроса перед выбором: нужна ли устойчивость и есть ли в данных готовый порядок.",
        "Лидер команды: Подъячий Глеб. Каждый участник рассказывает свой язык.",
    ]:
        add_bullet(frame, line, 22)

    slide = new("FFFFFF")
    add_text(slide, "Пять языков, семь вызовов", 1.2, 0.6, 31, 1.3, 32, True)
    rows = [
        ["Вызов", "Алгоритм", "Устойчивость"],
        ["Python list.sort", "Timsort + Powersort", "да"],
        ["Java Arrays.sort(int)", "Dual-Pivot Quicksort", "нет"],
        ["Java Arrays.sort(Integer)", "Timsort", "да"],
        ["C# Array.Sort", "introsort", "нет"],
        ["JavaScript, движок V8", "Timsort", "да"],
        ["C++ std::sort", "introsort", "нет"],
        ["C++ std::stable_sort", "слияние", "да"],
    ]
    table_shape = slide.shapes.add_table(len(rows), 3, Pcm(1.2), Pcm(2.3), Pcm(31), Pcm(14.5))
    table = table_shape.table
    table.columns[0].width = Pcm(12)
    table.columns[1].width = Pcm(12)
    table.columns[2].width = Pcm(7)
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            cell = table.cell(r, c)
            cell.text = value
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            for paragraph in cell.text_frame.paragraphs:
                paragraph.font.size = Ppt(16)
                paragraph.font.name = "Calibri"
                paragraph.font.bold = r == 0
                paragraph.font.color.rgb = PptColor.from_string("FFFFFF" if r == 0 else "1C2830")
            cell.fill.solid()
            cell.fill.fore_color.rgb = PptColor.from_string(NAVY if r == 0 else "FFFFFF")

    def language_slide(title, who, lines):
        slide = new("FFFFFF")
        add_text(slide, title, 1.2, 0.6, 31, 1.4, 32, True)
        add_text(slide, who, 1.2, 2.1, 31, 1, 18, True, GOLD)
        frame = add_text(slide, "", 1.2, 3.3, 30, 13, 22)
        frame.paragraphs[0].text = lines[0]
        frame.paragraphs[0].font.size = Ppt(22)
        frame.paragraphs[0].font.name = "Calibri"
        for line in lines[1:]:
            add_bullet(frame, line, 22)

    language_slide("Python", "Подъячий Глеб", [
        "list.sort и sorted. Устойчивая адаптивная сортировка слиянием.",
        "Короткие куски добираются вставками. С Python 3.11 серии сливаются по стратегии Powersort.",
        "Полностью упорядоченный массив разбирается за один проход.",
        "На миллионе случайных чисел: 277 мс. На уже упорядоченном: 5,86 мс.",
        "Проверка: порядок равных элементов сохранился.",
    ])
    language_slide("Java", "Керимов Андрей", [
        "В одном классе Arrays.sort спрятаны два алгоритма.",
        "int[] : Dual-Pivot Quicksort. На случайном миллионе 48 мс, на упорядоченном 0,11 мс.",
        "Integer[] : устойчивый Timsort. На том же случайном миллионе 260 мс.",
        "Числа нечего различать между собой, поэтому для int устойчивость не нужна.",
        "Объекты различаются, и Java сохраняет их прежний порядок.",
    ])
    language_slide("C#", "Мамбетов Родион", [
        "Array.Sort это introsort, не устойчивый.",
        "Кусок короче 17 элементов сортируется вставками. Слишком глубокая рекурсия уходит в пирамиду.",
        "На случайном миллионе 48 мс, почти как Java для int и C++.",
        "Порядок равных элементов в проверке сломался.",
        "Если порядок важен, берут LINQ OrderBy: при равенстве сравнивается исходный номер.",
    ])
    language_slide("JavaScript", "Кулиш Артём", [
        "С ES2019 сортировка обязана быть устойчивой. Алгоритм стандарт не назначает.",
        "Node.js 24 и Chrome, движок V8, используют Timsort. Наш замер сделан там.",
        "На случайном миллионе 175 мс, на упорядоченном 8,88 мс. Порядок равных сохранился.",
        "Без функции сравнения числа сортируются как строки: [10, 2, 1] становится [1, 10, 2].",
        "Правильный вызов: array.sort((a, b) => a - b).",
    ])
    language_slide("C++", "Черакаев Антон", [
        "Замер на MSVC 2022. std::sort это introsort: быстро, на месте, не устойчиво.",
        "Короткие куски до 32 элементов добираются вставками, плохая глубина уходит в пирамиду.",
        "На случайном миллионе std::sort 55 мс, std::stable_sort 52 мс.",
        "std::stable_sort это слияние. В проверке порядок сохранился, у std::sort нет.",
        "Нужна скорость и числа: std::sort. Нужен прежний порядок равных записей: stable_sort.",
    ])

    slide = new("FFFFFF")
    add_text(slide, "Случайный миллион, мс", 1.2, 0.5, 31, 1.2, 32, True)
    add_text(slide, "Один и тот же массив. Время только самой сортировки, медиана пяти прогонов после прогрева.", 1.2, 2.0, 31, 1.2, 16)
    slide.shapes.add_picture(str(RESULTS / "fig_random.png"), Pcm(2.2), Pcm(3.3), Pcm(29), Pcm(14.2))

    slide = new("FFFFFF")
    add_text(slide, "Уже упорядоченный миллион", 1.2, 0.4, 31, 1.2, 32, True)
    slide.shapes.add_picture(str(RESULTS / "fig_sorted.png"), Pcm(1.4), Pcm(1.8), Pcm(20.5), Pcm(15.5))
    add_text(slide, "Что видно", 22.4, 2.2, 10, 1, 20, True, GOLD)
    frame = add_text(slide, "", 22.4, 3.4, 10.2, 13, 16)
    frame.paragraphs[0].text = "Java int: 0,11 мс"
    frame.paragraphs[0].font.size = Ppt(18)
    frame.paragraphs[0].font.bold = True
    frame.paragraphs[0].font.name = "Calibri"
    for line in ["против 48 мс на случайных.", "Python: 5,86 вместо 277.", "Рост n в 10 раз на случайных данных даёт около 12-14 раз по времени.", "Это и есть n log n."]:
        add_bullet(frame, line, 16)

    slide = new(NAVY)
    add_text(slide, "Выводы", 1.4, 0.8, 30, 1.3, 32, True, "FFFFFF")
    frame = add_text(slide, "", 1.4, 2.6, 30, 14, 22, color="FFFFFF")
    frame.paragraphs[0].text = "sort в разных языках не означает один алгоритм."
    frame.paragraphs[0].font.size = Ppt(24)
    frame.paragraphs[0].font.color.rgb = PptColor.from_string("FFFFFF")
    frame.paragraphs[0].font.name = "Calibri"
    for line in [
        "Устойчивые и адаптивные: Python, V8, объекты Java, std::stable_sort.",
        "Быстрые и на месте, но без сохранения порядка: std::sort, Array.Sort, Java int[].",
        "На случайных числах языки с объектами медленнее не потому, что Timsort плохой.",
        "На готовом порядке адаптивные реализации выигрывают в разы.",
        "Сначала спрашиваем: важны ли равные элементы и есть ли в данных порядок.",
    ]:
        paragraph = frame.add_paragraph()
        paragraph.text = line
        paragraph.font.size = Ppt(22)
        paragraph.font.color.rgb = PptColor.from_string("FFFFFF")
        paragraph.font.name = "Calibri"
        paragraph.level = 0

    path = ROOT / "Презентация_команда7.pptx"
    prs.save(path)
    return path


def build_report_html(times):
    def row(cells, head=False):
        tag = "th" if head else "td"
        return "<tr>" + "".join(f"<{tag}>{html.escape(value)}</{tag}>" for value in cells) + "</tr>"

    body = [row(["Реализация", "Случайные", "По возрастанию", "По убыванию", "Мало разных", "Почти упорядочен"], True)]
    for key in ORDER:
        body.append(row([LABELS[key]] + [fmt(times[(key, pattern, 1_000_000)]) for pattern, _ in PATTERNS]))
    document = f"""<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8">
<title>Отчёт. Команда 7</title>
<style>
@page {{ size: A4; margin: 16mm 16mm 16mm 18mm; }}
body {{ font-family: "Times New Roman", Times, serif; font-size: 13.5pt; line-height: 1.28; color: #1c2830; }}
h1 {{ font-size: 18pt; text-align: center; margin: 0 0 6px; }}
h2 {{ font-size: 15pt; margin: 12px 0 4px; }}
p {{ margin: 0 0 6px; }}
.center {{ text-align: center; }}
.small {{ font-size: 12pt; }}
table {{ border-collapse: collapse; width: 100%; margin: 6px 0 8px; font-size: 11pt; }}
th, td {{ border: 1px solid #8aa; padding: 3px 5px; text-align: left; }}
th {{ background: #16324f; color: white; }}
</style></head><body>
<p class="center small">ГБОУВО РК «Крымский инженерно-педагогический университет имени Февзи Якубова»</p>
<h1>ОТЧЁТ</h1>
<p class="center"><b>Команда 7. Сортировка в современных языках программирования</b></p>
<p class="center small">Алгоритмы и структуры данных. Преподаватель: Меметов М. Р. Симферополь, 2026</p>
<h2>1. Состав и цель</h2>
<p>Лидер: Подъячий Глеб Русланович. Участники: Керимов Андрей Эдуардович, Мамбетов Родион Рудемович, Черакаев Антон Александрович, Кулиш Артём Евгеньевич.</p>
<p>Цель: выяснить, какой алгоритм спрятан во встроенной сортировке Python, Java, C#, JavaScript и C++, и на одних и тех же массивах сравнить время и устойчивость.</p>
<h2>2. Алгоритмы</h2>
<p>Python 3.14, list.sort. Устойчивая адаптивная сортировка слиянием семейства Timsort. С версии 3.11 порядок слияния серий выбирает Powersort. На полностью упорядоченном массиве время близко к линейному.</p>
<p>Java 17. Arrays.sort для int, long и чисел с плавающей точкой: Dual-Pivot Quicksort, не устойчивый. Arrays.sort для объектов: устойчивый Timsort.</p>
<p>C#, Array.Sort. Introsort: быстрая сортировка, вставки на кусках не длиннее 16 и пирамида при глубокой рекурсии. Не устойчивый. Устойчивый вариант: LINQ OrderBy, при равенстве сравнивается исходный номер.</p>
<p>JavaScript. ES2019 требует устойчивость, алгоритм не назначает. Node.js 24 работает на V8, там Timsort. Без функции сравнения числа сортируются как строки.</p>
<p>C++, MSVC. std::sort: introsort, на месте, не устойчивый. std::stable_sort: слияние, устойчивый, нужна дополнительная память.</p>
<h2>3. Сложность</h2>
<p>Для случайных данных все семь вызовов имеют порядок n log n. При росте n в 10 раз время растёт примерно в 12 раз. На уже упорядоченных данных Timsort и Dual-Pivot, который замечает готовые серии, уходят к линейному проходу. Introsort тоже быстро заканчивает, но запасной пирамидой держит худший случай в границе O(n log n). Устойчивые слияния просят дополнительную память O(n). Introsort и быстрая сортировка живут почти на месте, память O(log n) на стек.</p>
<h2>4. Как измеряли</h2>
<p>Один генератор с зерном 7 построил пять видов массивов: случайный, по возрастанию, по убыванию, из 10 разных чисел и почти упорядоченный. Размеры: 10 тысяч, 100 тысяч, 1 миллион. Все языки читали один и тот же файл. Первая попытка отбрасывалась, дальше бралась медиана пяти замеров. В время не входит чтение файла.</p>
<p>Устойчивость: 400 пар «значение, исходный номер» сортируются только по значению. Если номера внутри равного значения идут по порядку, алгоритм устойчивый.</p>
<h2>5. Результаты, n = 1 000 000, миллисекунды</h2>
<table>
{''.join(body)}
</table>
<p>На случайном миллионе Java для int, C# и C++ std::sort близки: 48, 48 и 55 мс. Python тратит 277 мс, Java для объектов 260 мс, JavaScript 175 мс. Это цена сравнения объектов и устройства языка, а не приговор Timsort.</p>
<p>На упорядоченном миллионе Java для int показывает 0,11 мс против 48 мс на случайных числах. Python показывает 5,86 мс против 277 мс. Готовый порядок адаптивные реализации используют.</p>
<p>Проверка устойчивости совпала с теорией. Python, JavaScript, объекты Java и std::stable_sort порядок сохранили. Array.Sort и std::sort сломали.</p>
<h2>6. Выводы</h2>
<p>Выбор зависит от двух вещей: важен ли порядок равных элементов и есть ли в данных готовый порядок. Числа и скорость: std::sort, Array.Sort или Arrays.sort для int. Прежний порядок равных записей: list.sort, сортировка объектов в Java, Array.prototype.sort с числовым компаратором, std::stable_sort или OrderBy. В JavaScript вызов без функции сравнения для чисел является ошибкой.</p>
<p class="small">Источники: CPython listsort.txt и Powersort с версии 3.11; документация Java SE 17 Arrays; Microsoft Array.Sort; блог V8 «Getting things sorted»; MDN, устойчивость с ES2019; стандарт C++ для std::sort и std::stable_sort.</p>
</body></html>"""
    path = ROOT / "Отчет_команда7.html"
    path.write_text(document, encoding="utf-8")
    return path


def to_pdf(report_html):
    candidates = [
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    ]
    edge = next((path for path in candidates if path.exists()), None)
    if edge is None:
        print("EDGE_NOT_FOUND")
        return
    pdf = ROOT / "Отчет_команда7.pdf"
    uri = report_html.resolve().as_uri()
    subprocess.run(
        [str(edge), "--headless", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", uri],
        check=True,
    )
    print("PDF", pdf, pdf.stat().st_size)


def main():
    times, stable = parse()
    print("STABLE", stable)
    RESULTS.mkdir(exist_ok=True)
    chart(times, "random", "Случайные числа, n = 1 000 000", RESULTS / "fig_random.png")
    chart(times, "sorted", "Уже упорядоченные числа, n = 1 000 000", RESULTS / "fig_sorted.png")
    build_report(times)
    for person in PEOPLE:
        build_person(person)
        build_self(person)
    build_roles()
    build_pptx(times)
    report_html = build_report_html(times)
    to_pdf(report_html)
    print("MATERIALS_OK")


if __name__ == "__main__":
    main()
