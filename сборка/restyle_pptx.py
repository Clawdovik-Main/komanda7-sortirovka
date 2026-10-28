# -*- coding: utf-8 -*-
"""Презентация команды 7 в той же палитре, что и страница. 15 слайдов."""
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Cm, Emu, Pt

ROOT = Path(__file__).resolve().parent.parent if Path(__file__).resolve().parent.name == "сборка" else Path(__file__).resolve().parent
INK = "8D4330"
PINK = "FF8BA6"
CREAM = "FFF6EE"
GOLD = "FFC179"
PAPER = "FFE7D4"
WHITE = "FFFFFF"


def rgb(value):
    return RGBColor.from_string(value)


def add_text(slide, text, left, top, width, height, size=20, bold=False, color=INK, align=PP_ALIGN.LEFT, font="Calibri"):
    box = slide.shapes.add_textbox(Cm(left), Cm(top), Cm(width), Cm(height))
    frame = box.text_frame
    frame.word_wrap = True
    paragraph = frame.paragraphs[0]
    paragraph.alignment = align
    run = paragraph.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = rgb(color)
    run.font.name = font
    return frame


def add_lines(frame, lines, size=18, color=INK):
    first = True
    for line in lines:
        paragraph = frame.paragraphs[0] if first and not frame.paragraphs[0].text else frame.add_paragraph()
        first = False
        paragraph.text = line
        paragraph.font.size = Pt(size)
        paragraph.font.color.rgb = rgb(color)
        paragraph.font.name = "Calibri"
        paragraph.level = 0


def blob(slide, left, top, width, height, fill):
    shape = slide.shapes.add_shape(MSO_SHAPE.OVAL, Cm(left), Cm(top), Cm(width), Cm(height))
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb(fill)
    shape.line.fill.background()


def new(prs, blank, bg=CREAM):
    slide = prs.slides.add_slide(blank)
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = rgb(bg)
    blob(slide, -2.2, -2.4, 7, 7, PINK)
    blob(slide, 29.5, 14.2, 6, 6, GOLD)
    blob(slide, 30.5, -1.8, 4.2, 4.2, "FFD6B7")
    return slide


def title_bar(slide, text):
    add_text(slide, text, 1.1, 0.45, 28, 1.3, 30, True, INK, font="Georgia")


def build():
    prs = Presentation()
    prs.slide_width = Cm(33.867)
    prs.slide_height = Cm(19.05)
    blank = prs.slide_layouts[6]

    slide = new(prs, blank, PAPER)
    add_text(slide, "КОМАНДА 7  ·  КИПУ", 1.3, 1.3, 22, 0.8, 16, True, INK)
    add_text(slide, "Сортировка\nв современных языках", 1.3, 2.3, 22, 5.2, 40, True, INK, font="Georgia")
    add_text(slide, "Python, Java, C#, JavaScript, C++\n28 октября 2026", 1.3, 8.2, 20, 1.8, 18, color=INK)
    add_text(slide, "Подъячий Глеб\nКеримов Андрей\nМамбетов Родион\nЧеракаев Антон\nКулиш Артём", 1.3, 10.6, 16, 6, 18, color=INK)
    faces = ["faces/chain.jpg", "faces/wavy.jpg", "faces/curly.jpg", "faces/kid.jpg", "faces/shrimp.jpg"]
    for index, name in enumerate(faces):
        slide.shapes.add_picture(str(ROOT / name), Cm(20.2 + (index % 3) * 4.2), Cm(3.2 + (index // 3) * 5.4), Cm(3.8), Cm(4.6))

    slide = new(prs, blank)
    title_bar(slide, "Зачем этот проект")
    frame = add_text(slide, "", 1.3, 2.4, 30, 14, 22)
    add_lines(frame, [
        "Одинаковое имя sort прячет разные алгоритмы.",
        "Где-то устойчивый Timsort, где-то быстрая сортировка с пирамидой на подхвате.",
        "Мы мерили встроенные функции на одних и тех же массивах.",
        "Два вопроса до выбора: нужна ли устойчивость и есть ли в данных готовый порядок.",
        "Лидер: Подъячий Глеб. Каждый говорит не меньше минуты про свой язык.",
    ], 24)

    slide = new(prs, blank)
    title_bar(slide, "Семь вызовов")
    rows = [
        ["Вызов", "Алгоритм", "Порядок равных"],
        ["Python list.sort", "Timsort, Powersort", "хранит"],
        ["Java int[]", "Dual-Pivot Quicksort", "для чисел неразличим"],
        ["Java Integer[]", "Timsort", "хранит"],
        ["C# Array.Sort", "introsort", "не хранит"],
        ["JavaScript, V8", "Timsort", "язык требует хранить"],
        ["C++ std::sort", "introsort", "не хранит"],
        ["C++ stable_sort", "слияние", "хранит"],
    ]
    table_shape = slide.shapes.add_table(len(rows), 3, Cm(1.2), Cm(2.2), Cm(31.2), Cm(15.2))
    table = table_shape.table
    table.columns[0].width = Cm(10)
    table.columns[1].width = Cm(12)
    table.columns[2].width = Cm(9.2)
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            cell = table.cell(r, c)
            cell.text = value
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            for paragraph in cell.text_frame.paragraphs:
                paragraph.font.size = Pt(16)
                paragraph.font.name = "Calibri"
                paragraph.font.bold = r == 0
                paragraph.font.color.rgb = rgb(WHITE if r == 0 else INK)
            cell.fill.solid()
            cell.fill.fore_color.rgb = rgb(INK if r == 0 else (PINK if r % 2 == 0 else WHITE))

    slide = new(prs, blank)
    title_bar(slide, "Устойчивость на двух двойках")
    frame = add_text(slide, "", 1.3, 2.3, 30, 14, 22)
    add_lines(frame, [
        "2 А стояла левее 2 Б. Обе меньше восьмёрки.",
        "Устойчивая сортировка ставит числа по возрастанию и не меняет А и Б местами.",
        "Неустойчивая может поставить 2 Б левее, хотя значения равны.",
        "Проверка была на 400 парах, не на десятке: короткий кусок introsort добивает вставками и случайно сохраняет порядок.",
        "Сохранили: Python, JavaScript, объекты Java, std::stable_sort.",
        "Сломали: C# Array.Sort и C++ std::sort.",
    ], 22)

    slide = new(prs, blank)
    title_bar(slide, "Timsort и Powersort")
    frame = add_text(slide, "", 1.3, 2.3, 30, 15, 22)
    add_lines(frame, [
        "Timsort ищет уже готовые серии: вверх или вниз.",
        "Нисходящую серию разворачивает. Короткую добирает вставками до minrun, обычно 32-64.",
        "Потом серии сливает. Равные забирает из левой серии, поэтому порядок хранится.",
        "Память O(n). На полностью готовом массиве серия одна, время близко к линейному.",
        "С Python 3.11 порядок слияния выбирает Powersort: не клеить крошку к гиганту, если рядом ровнее пара.",
        "Так устроены Python list.sort, Java для объектов и V8.",
    ], 22)

    def language(heading, who, lines):
        slide = new(prs, blank)
        title_bar(slide, heading)
        add_text(slide, who, 1.3, 1.9, 30, 0.8, 20, True, "C45B78")
        frame = add_text(slide, "", 1.3, 2.9, 30, 14, 22)
        add_lines(frame, lines, 22)

    language("Python", "Подъячий Глеб", [
        "list.sort и sorted. Устойчивая адаптивная сортировка слиянием.",
        "Случайный миллион: 277 мс. Уже упорядоченный: 5,86 мс.",
        "Порядок равных в проверке сохранился.",
        "277 мс рядом с Java для объектов (260) и далеко от Java для int (48).",
        "Это цена языка и сравнения, не приговор Timsort.",
    ])
    language("Java, две функции", "Керимов Андрей", [
        "int[]: Dual-Pivot Quicksort. Два опорных, три части, вставки на коротком куске.",
        "Готовые серии реализация замечает. Поэтому упорядоченный миллион: 0,11 мс против 48 мс.",
        "Integer[]: устойчивый Timsort, на случайном миллионе 260 мс.",
        "У голых чисел нет «кто был левее». У объектов есть, и Java это хранит.",
    ])
    language("C#", "Мамбетов Родион", [
        "Array.Sort это introsort. Кусок короче 17 элементов уходит во вставки.",
        "Слишком глубокая рекурсия уходит в пирамиду, худший случай остаётся n log n.",
        "Случайный миллион: 48 мс. Порядок равных в проверке сломался.",
        "Если порядок важен: LINQ OrderBy. При равенстве сравнивается исходный номер.",
    ])
    language("JavaScript", "Кулиш Артём", [
        "С ES2019 сортировка обязана быть устойчивой. Алгоритм стандарт не назначает.",
        "Node 24 и Chrome, движок V8, используют Timsort. Замер сделан там.",
        "Случайный миллион: 175 мс. Упорядоченный: 8,88 мс. Порядок равных сохранился.",
        "Без функции сравнения [10, 2, 1] становится [1, 10, 2]: строки, не числа.",
        "Нужный вызов: array.sort((a, b) => a - b).",
    ])
    language("C++", "Черакаев Антон", [
        "Замер на MSVC 2022. std::sort это introsort, на месте, без устойчивости.",
        "Вставки до 32 элементов. Плохая глубина уходит в пирамиду.",
        "Случайный миллион: std::sort 55 мс, std::stable_sort 52 мс.",
        "stable_sort это слияние и в проверке порядок сохранил.",
        "Числа и скорость: std::sort. Прежний порядок равных записей: stable_sort.",
    ])

    slide = new(prs, blank)
    title_bar(slide, "Как мерили")
    frame = add_text(slide, "", 1.3, 2.3, 30, 14, 22)
    add_lines(frame, [
        "Один генератор, зерно 7. Пять рисунков: случайный, вверх, вниз, 10 разных значений, почти упорядоченный.",
        "Размеры: 10 тысяч, 100 тысяч, 1 миллион. Все языки читали один файл.",
        "Первая попытка выбрасывалась. Дальше медиана пяти. Чтение файла в время не входит.",
        "От 100 тысяч к миллиону на случайных данных время выросло примерно в 12-14 раз. Это n log n.",
        "Сборка Java шла из латинской временной папки: javac на этой машине портит кириллицу в пути.",
    ], 22)

    slide = new(prs, blank)
    title_bar(slide, "Случайный миллион")
    slide.shapes.add_picture(str(ROOT / "results" / "fig_random.png"), Cm(3.2), Cm(2.1), Cm(27), Cm(15.4))

    slide = new(prs, blank)
    title_bar(slide, "Уже упорядоченный миллион")
    slide.shapes.add_picture(str(ROOT / "results" / "fig_sorted.png"), Cm(1.1), Cm(2.0), Cm(21), Cm(15.6))
    add_text(slide, "Java int\n0,11 мс\nвместо 48", 22.6, 3.2, 9, 4, 22, True, INK)
    add_text(slide, "Python\n5,86 мс\nвместо 277", 22.6, 8.4, 9, 4, 22, True, INK)
    add_text(slide, "Готовый порядок\nадаптивные\nиспользуют", 22.6, 13.4, 9, 4, 18, color=INK)

    slide = new(prs, blank)
    title_bar(slide, "Коротко по цифрам")
    frame = add_text(slide, "", 1.3, 2.3, 30, 15, 20)
    add_lines(frame, [
        "C++ не «быстрее как алгоритм». 48 мс и 277 мс это цена языка и объектов.",
        "Java int на убывании тоже почти мгновенный, 0,64 мс: видит длинную серию вниз.",
        "Стандарт C++ не обязывает именно introsort. Это выбор MSVC. Гарантия: среднее n log n и нет устойчивости.",
        "Стандарт JavaScript не обязывает Timsort. Обязывает устойчивость. Timsort здесь потому, что движок V8.",
        "Порядок равных у int не проверяли: две одинаковые пятёрки неразличимы.",
    ], 22)

    slide = new(prs, blank, INK)
    add_text(slide, "Выводы", 1.3, 0.7, 30, 1.4, 32, True, WHITE, font="Georgia")
    frame = add_text(slide, "", 1.3, 2.5, 30, 14, 22, color=WHITE)
    add_lines(frame, [
        "sort в разных языках не означает один алгоритм.",
        "Хранят порядок и любят готовые серии: Python, V8, объекты Java, std::stable_sort.",
        "Быстрые и почти на месте: std::sort, Array.Sort, Java int[].",
        "Короткий кусок везде добирают вставками. Квадрат у introsort обрывает пирамида.",
        "Выбор зависит от двух вещей: порядок равных и готовые куски в данных.",
        "В JavaScript для чисел нужен компаратор (a, b) => a - b.",
    ], 22, WHITE)

    stickers = [
        "gifcity/icon_3a551453.gif",
        "gifcity/icon_9b7cb59e.gif",
        "gifcity/icon_6fa3ef35.gif",
        "gifcity/icon_58000a7d.gif",
        "gifcity/icon_f060a0f0.gif",
        "gifcity/icon_3a8f55d3.gif",
        "gifcity/icon_e791ba55.gif",
        "gifcity/icon_d94fd6a7.gif",
        "gifcity/icon_199d08cc.gif",
        "gifcity/icon_afcf929d.gif",
        "gifcity/icon_07d05094.gif",
        "gifcity/gallery249_fc75801a.gif",
    ]
    buttons = [
        "gifcity/gallery26_de8642bf.png",
        "gifcity/gallery26_2a7fa783.gif",
        "gifcity/gallery26_72115e16.png",
        "gifcity/gallery26_2aa577e6.gif",
        "gifcity/gallery26_95c38f58.png",
        "gifcity/gallery28_33ade54c.png",
    ]
    corners = [
        (0.15, 0.12, 1.15),
        (32.35, 0.15, 1.05),
        (0.15, 8.4, 1.1),
        (32.4, 8.6, 1.05),
        (0.2, 17.45, 1.1),
        (32.3, 17.4, 1.05),
    ]
    for index, slide in enumerate(prs.slides):
        for spot, (left, top, width) in enumerate(corners):
            picture = stickers[(index * 3 + spot) % len(stickers)]
            slide.shapes.add_picture(str(ROOT / picture), Cm(left), Cm(top), Cm(width))
        badge = buttons[index % len(buttons)]
        slide.shapes.add_picture(str(ROOT / badge), Cm(14.2), Cm(17.85), Cm(3.4), Cm(1.15))

    out = ROOT / "сдача" / "презентация" / "Презентация_команда7.pptx"
    prs.save(out)
    print(len(prs.slides), out)


if __name__ == "__main__":
    build()
