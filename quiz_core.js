/* Контрольная: пошаговые разборы.
   Индексы в тексте с 1, как в методичке лабораторных.
   Столбцы таблицы a0..a9 это те же числа слева направо: A[1] = a0.
*/
(function (root, factory) {
  const api = factory();
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (typeof root !== "undefined") root.QuizCore = api;
})(typeof window !== "undefined" ? window : globalThis, function () {
  function clone(xs) {
    return xs.slice();
  }

  function fmt(xs) {
    return xs.map(function (x) { return x === null || x === undefined ? "." : String(x); }).join(" ");
  }

  function blank(n) {
    return Array(n).fill("");
  }

  function logB(pa, pb) {
    return Math.log(pa) / Math.log(pb);
  }

  function logLabel(pa, pb) {
    if (pa === pb) return "1";
    return logB(pa, pb).toFixed(4).replace(".", ",");
  }

  function push(frames, frame) {
    frames.push(frame);
  }

  function insertion(src) {
    const a = clone(src);
    const n = a.length;
    const frames = [];
    let comps = 0;
    push(frames, {
      kind: "array", title: "Старт",
      text: "Идём слева направо. Кусок слева уже стоит по неубыванию. Очередное число, ключ, несём влево, пока левый сосед строго больше. Равного соседа не перепрыгиваем, поэтому вставки устойчивые. Индексы с 1.",
      a: clone(a), marks: blank(n)
    });
    for (let i = 1; i < n; i++) {
      const key = a[i];
      let j = i - 1;
      const take = blank(n);
      for (let t = 0; t < i; t++) take[t] = "sorted";
      take[i] = "key";
      push(frames, {
        kind: "array",
        title: "Ключ A[" + (i + 1) + "] = " + key,
        text: (i === 1 ? "Слева пока одно число A[1]." : "A[1.." + i + "] уже упорядочен.") + " Берём ключ " + key + " и ищем ему место левее.",
        a: clone(a), marks: take
      });
      while (j >= 0) {
        comps++;
        if (a[j] <= key) break;
        const moving = a[j];
        const from = j + 1;
        a[j + 1] = moving;
        const shift = blank(n);
        for (let t = 0; t <= i; t++) shift[t] = "sorted";
        shift[j] = "hot";
        shift[j + 1] = "key";
        push(frames, {
          kind: "array",
          title: "Сдвиг " + moving + " вправо",
          text: "A[" + from + "] = " + moving + " больше ключа " + key + ". Ключ пока лежит отдельно, а " + moving + " сдвигается на одну клетку вправо. На картинке он виден дважды, пока ключ не встанет на своё место.",
          a: clone(a), marks: shift
        });
        j--;
      }
      a[j + 1] = key;
      const done = blank(n);
      for (let t = 0; t <= i; t++) done[t] = "sorted";
      done[j + 1] = "written";
      const why = j < 0
        ? "Слева клетки кончились, ключ становится новым началом."
        : "A[" + (j + 1) + "] = " + a[j] + " уже не больше ключа, дальше не несём.";
      push(frames, {
        kind: "array",
        title: "Ключ " + key + " на месте A[" + (j + 2) + "]",
        text: why + " Кусок A[1.." + (i + 1) + "] упорядочен: " + fmt(a.slice(0, i + 1)) + ".",
        a: clone(a), marks: done
      });
    }
    push(frames, {
      kind: "array", title: "Вставки готовы",
      text: "Итог: " + fmt(a) + ". Сравнений: " + comps + ". На длинном массиве это около n^2/2 в худшем случае. Здесь n = 10, поэтому шагов мало.",
      a: clone(a), marks: Array(n).fill("sorted")
    });
    return frames;
  }

  function mergeSort(src) {
    const a = clone(src);
    const n = a.length;
    const frames = [];
    let comps = 0;
    function marksRange(lo, hi, cls) {
      const m = blank(n);
      for (let t = lo; t <= hi; t++) m[t] = cls;
      return m;
    }
    function rec(p, r) {
      if (p > r) return;
      if (p === r) {
        const m = blank(n);
        m[p] = "sorted";
        push(frames, {
          kind: "array",
          title: "A[" + (p + 1) + "] делить некуда",
          text: "В куске один элемент " + a[p] + ". Он уже упорядочен, слияние не нужно.",
          a: clone(a), marks: m
        });
        return;
      }
      const q = Math.floor((p + r) / 2);
      const split = blank(n);
      for (let t = p; t <= q; t++) split[t] = "left";
      for (let t = q + 1; t <= r; t++) split[t] = "right";
      push(frames, {
        kind: "array",
        title: "Делим A[" + (p + 1) + ".." + (r + 1) + "]",
        text: "Середина q = " + (q + 1) + ". Левая половина A[" + (p + 1) + ".." + (q + 1) + "], правая A[" + (q + 2) + ".." + (r + 1) + "]. Сначала упорядочиваем обе, потом сливаем.",
        a: clone(a), marks: split
      });
      rec(p, q);
      rec(q + 1, r);
      const C = a.slice(p, q + 1);
      let i = 0;
      let j = q + 1;
      let k = p;
      push(frames, {
        kind: "array",
        title: "Слияние A[" + (p + 1) + ".." + (q + 1) + "] и A[" + (q + 2) + ".." + (r + 1) + "]",
        text: "Левую половину копируем в буфер: " + fmt(C) + ". Правая остаётся в массиве: " + fmt(a.slice(q + 1, r + 1)) + ". Сравниваем головы. Если равны, берём левую, поэтому слияние устойчивое.",
        a: clone(a), marks: split
      });
      while (i < C.length && j <= r) {
        comps++;
        const leftHead = C[i];
        const rightHead = a[j];
        const takeLeft = leftHead <= rightHead;
        const chosen = takeLeft ? leftHead : rightHead;
        a[k] = chosen;
        if (takeLeft) i++; else j++;
        const look = blank(n);
        for (let t = p; t <= k; t++) look[t] = "written";
        push(frames, {
          kind: "array",
          title: "В A[" + (k + 1) + "] пишем " + chosen,
          text: takeLeft
            ? leftHead + " не больше " + rightHead + ". Берём его из левого буфера."
            : rightHead + " меньше " + leftHead + ". Берём голову правой половины.",
          a: clone(a), marks: look
        });
        k++;
      }
      while (i < C.length) {
        a[k] = C[i];
        const m = marksRange(p, k, "written");
        push(frames, {
          kind: "array",
          title: "Дописываем левый остаток " + C[i],
          text: "Правая половина уже кончилась. Оставшиеся числа буфера идут в конец куска по порядку.",
          a: clone(a), marks: m
        });
        i++;
        k++;
      }
      const done = marksRange(p, r, "written");
      push(frames, {
        kind: "array",
        title: "Кусок A[" + (p + 1) + ".." + (r + 1) + "] слит",
        text: "Получилось: " + fmt(a.slice(p, r + 1)) + ". Правый остаток, если он был, уже лежал на месте и его не копировали.",
        a: clone(a), marks: done
      });
    }
    push(frames, {
      kind: "array", title: "Старт",
      text: "Делим массив пополам, пока не останутся одиночные числа, потом сливаем упорядоченные половины. Дополнительная память нужна на левую половину. Итог по неубыванию.",
      a: clone(a), marks: blank(n)
    });
    rec(0, n - 1);
    push(frames, {
      kind: "array", title: "Слияние готово",
      text: "Итог: " + fmt(a) + ". Сравнений голов: " + comps + ". Время Θ(n log n), память Θ(n).",
      a: clone(a), marks: Array(n).fill("sorted")
    });
    return frames;
  }

  function counting(src) {
    const a = clone(src);
    const n = a.length;
    const k = Math.max.apply(null, a);
    const C = Array(k + 1).fill(0);
    const B = Array(n).fill(null);
    const frames = [];
    function snap(title, text, markA, markC, markB) {
      push(frames, {
        kind: "count", title: title, text: text,
        a: clone(a), c: clone(C), b: B.slice(),
        markA: markA, markC: markC, markB: markB
      });
    }
    snap(
      "Старт",
      "Ключи целые от 0 до k = " + k + ". Массив C[0.." + k + "] считает, сколько раз встретился каждый ключ. B это ответ, пока пустой. Порядок неубывающий, как в базовом алгоритме. В лабораторной 6 отдельно просили невозрастающий порядок, здесь такого условия нет.",
      -1, -1, -1
    );
    for (let j = 0; j < n; j++) {
      C[a[j]]++;
      snap(
        "Частота A[" + (j + 1) + "] = " + a[j],
        "C[" + a[j] + "] становится " + C[a[j]] + ". Это пока просто число повторов, ещё не позиция.",
        j, a[j], -1
      );
    }
    snap(
      "Частоты готовы",
      "C = " + fmt(C) + ". Здесь все числа разные, поэтому каждая частота равна 1. Дальше из частот собираем позиции.",
      -1, -1, -1
    );
    for (let i = 1; i <= k; i++) {
      const old = C[i];
      C[i] = old + C[i - 1];
      snap(
        "Накопление C[" + i + "]",
        "C[" + i + "] = " + old + " + C[" + (i - 1) + "] = " + C[i] + ". Теперь C[i] говорит, сколько элементов не больше i, и это номер места, считая с 1.",
        -1, i, -1
      );
    }
    for (let j = n - 1; j >= 0; j--) {
      const value = a[j];
      const place = C[value];
      B[place - 1] = value;
      C[value]--;
      snap(
        "Пишем B[" + place + "] = " + value,
        "Идём по входу с конца, так сохраняется устойчивость. A[" + (j + 1) + "] = " + value + ", место C[" + value + "] было " + place + ". После записи счётчик уменьшен до " + C[value] + ". Следующий такой же ключ сядет левее.",
        j, value, place - 1
      );
    }
    snap(
      "Подсчёт готов",
      "Итог B: " + fmt(B) + ". Время Θ(n + k). Здесь n = 10 и k = 9, оба массива короткие. Сравнений между элементами нет: алгоритм смотрит на сам ключ как на номер клетки.",
      -1, -1, -1
    );
    return frames;
  }

  function heapSort(src, kind) {
    const isMax = kind === "max";
    const a = [null].concat(src);
    const n = src.length;
    let heapSize = n;
    const frames = [];
    let comps = 0;
    const titleKind = isMax ? "Невозрастающая пирамида" : "Неубывающая пирамида";
    const rule = isMax
      ? "У родителя значение не меньше, чем у детей: A[i] >= A[2i] и A[i] >= A[2i+1]. В корне максимум."
      : "У родителя значение не больше, чем у детей: A[i] <= A[2i] и A[i] <= A[2i+1]. В корне минимум.";

    function view() {
      return a.slice(1);
    }
    function marks(extra) {
      const m = blank(n);
      for (let i = heapSize + 1; i <= n; i++) m[i - 1] = "sorted";
      Object.keys(extra || {}).forEach(function (idx) {
        m[Number(idx) - 1] = extra[idx];
      });
      return m;
    }
    function snap(title, text, extra) {
      push(frames, {
        kind: "heap", title: title, text: text,
        a: view(), marks: marks(extra), heapSize: heapSize, heapMax: isMax
      });
    }
    function better(x, y) {
      comps++;
      return isMax ? a[x] > a[y] : a[x] < a[y];
    }
    function heapify(i) {
      const l = 2 * i;
      const r = 2 * i + 1;
      let best = i;
      const kids = {};
      kids[i] = "hot";
      if (l <= heapSize) kids[l] = "left";
      if (r <= heapSize) kids[r] = "right";
      if (l <= heapSize && better(l, best)) best = l;
      if (r <= heapSize && better(r, best)) best = r;
      const leftName = l <= heapSize ? String(l) : "нет";
      const rightName = r <= heapSize ? String(r) : "нет";
      const who = isMax ? "Наибольший" : "Наименьший";
      snap(
        titleKind + ", узел " + i,
        "Смотрим узел " + i + ". Левый ребёнок: " + leftName + ". Правый ребёнок: " + rightName + ". " + who + " среди них сейчас в позиции " + best + ", значение " + a[best] + ". " + rule,
        kids
      );
      if (best === i) return;
      const from = a[i];
      const to = a[best];
      const tmp = a[i];
      a[i] = a[best];
      a[best] = tmp;
      snap(
        "Меняем " + i + " и " + best,
        "Родитель " + from + " нарушал порядок. Меняем его с " + to + " и проверяем пирамиду уже ниже, в узле " + best + ".",
        { [i]: "written", [best]: "hot" }
      );
      heapify(best);
    }

    snap(
      titleKind + ", исходный массив",
      rule + " Каждый лист уже пирамида из одного узла. Строим снизу: от узла floor(n/2) = " + Math.floor(n / 2) + " до корня 1. Индексы с 1, левый ребёнок 2i, правый 2i+1, родитель floor(i/2).",
      {}
    );
    for (let i = Math.floor(n / 2); i >= 1; i--) heapify(i);
    snap(
      "Пирамида построена",
      "Свойство выполнено во всех узлах. Корень A[1] = " + a[1] + ". Дальше забираем корень в конец ещё живой части и чиним пирамиду.",
      { 1: "key" }
    );
    for (let end = n; end >= 2; end--) {
      const root = a[1];
      const back = a[end];
      a[1] = back;
      a[end] = root;
      heapSize--;
      snap(
        "Корень " + root + " уходит на место " + end,
        isMax
          ? "В корне был максимум " + root + ". Ставим его в конец живой части. Слева остаётся пирамида из " + heapSize + " узлов, справа уже готовый хвост по возрастанию."
          : "В корне был минимум " + root + ". Ставим его в конец живой части. Слева пирамида из " + heapSize + " узлов, справа хвост по убыванию: мелкие числа выходят первыми и садятся правее.",
        { 1: "hot", [end]: "sorted" }
      );
      heapify(1);
    }
    snap(
      titleKind + " готова",
      "Итог: " + fmt(view()) + ". Сравнений с детьми: " + comps + ". " + (isMax
        ? "Невозрастающая пирамида сортирует по неубыванию."
        : "Неубывающая пирамида сортирует по невозрастанию. Это не перевёрнутый ответ первой пирамиды: дерево строилось заново, родитель каждый раз был не больше детей."),
      {}
    );
    return frames;
  }

  function quick(src) {
    const a = clone(src);
    const n = a.length;
    const frames = [];
    let comps = 0;
    function snap(title, text, marks) {
      push(frames, { kind: "array", title: title, text: text, a: clone(a), marks: marks });
    }
    function paint(p, r, extra) {
      const m = blank(n);
      for (let t = 0; t < p; t++) m[t] = "dim";
      for (let t = r + 1; t < n; t++) m[t] = "dim";
      Object.keys(extra || {}).forEach(function (idx) { m[Number(idx)] = extra[idx]; });
      return m;
    }
    function partition(p, r) {
      const x = a[r];
      let i = p - 1;
      snap(
        "Partition A[" + (p + 1) + ".." + (r + 1) + "], опора " + x,
        "Опора x = A[" + (r + 1) + "] = " + x + " уже стоит в конце отрезка. i начинает с " + p + " в нумерации методички (на 1 левее левой границы). Всё, что не больше x, собираем слева.",
        paint(p, r, { [r]: "pivot" })
      );
      for (let j = p; j < r; j++) {
        comps++;
        const goLeft = a[j] <= x;
        if (goLeft) {
          i++;
          const aj = a[j];
          const ai = a[i];
          if (i !== j) {
            const tmp = a[i];
            a[i] = a[j];
            a[j] = tmp;
          }
          snap(
            "A[" + (j + 1) + "] = " + aj + " идёт влево",
            aj + " не больше опоры " + x + ". Граница i становится " + (i + 1) + ". " + (i === j ? "Обмен не нужен, элемент уже на границе." : "Меняем A[" + (i + 1) + "] и A[" + (j + 1) + "]: " + ai + " и " + aj + "."),
            paint(p, r, { [i]: "left", [j]: "hot", [r]: "pivot" })
          );
        } else {
          snap(
            "A[" + (j + 1) + "] = " + a[j] + " остаётся справа",
            a[j] + " больше опоры " + x + ". Границу i не двигаем.",
            paint(p, r, { [j]: "right", [r]: "pivot", [Math.max(i, p)]: i >= p ? "left" : "" })
          );
        }
      }
      const q = i + 1;
      const pivot = a[r];
      const at = a[q];
      const tmp = a[q];
      a[q] = a[r];
      a[r] = tmp;
      snap(
        "Опора встаёт на A[" + (q + 1) + "]",
        "Меняем A[" + (q + 1) + "] = " + at + " и опору " + pivot + ". Слева от опоры числа не больше неё, справа больше. q = " + (q + 1) + ".",
        paint(p, r, { [q]: "pivot" })
      );
      return q;
    }
    function qs(p, r) {
      if (p > r) return;
      if (p === r) {
        snap(
          "A[" + (p + 1) + "] уже один",
          "В отрезке один элемент " + a[p] + ". Делить нечего.",
          paint(p, r, { [p]: "sorted" })
        );
        return;
      }
      const first = a[p];
      const last = a[r];
      const tmp = a[p];
      a[p] = a[r];
      a[r] = tmp;
      snap(
        "QuickSort A[" + (p + 1) + ".." + (r + 1) + "]",
        "Опора это первый элемент отрезка, A[" + (p + 1) + "] = " + first + ". Как в лабораторной, переносим его в конец и меняем с A[" + (r + 1) + "] = " + last + ". Дальше обычный Partition.",
        paint(p, r, { [r]: "pivot" })
      );
      const q = partition(p, r);
      qs(p, q - 1);
      qs(q + 1, r);
    }
    snap(
      "Старт",
      "Быстрая сортировка по неубыванию. На каждом отрезке опора равна первому элементу. Её переносим в конец и разрезаем массив: слева не больше опоры, справа больше. Потом так же сортируем обе стороны. Это тот же Partition, что в лабораторных 4-5.",
      blank(n)
    );
    qs(0, n - 1);
    snap(
      "Быстрая сортировка готова",
      "Итог: " + fmt(a) + ". Сравнений с опорой: " + comps + ". В среднем порядок n log n. Если опора каждый раз крайняя, худший случай около n^2. Устойчивости нет: равные могут разъехаться при разрезании. В этом массиве равных нет.",
      Array(n).fill("sorted")
    );
    return frames;
  }

  function selection(src, k) {
    const a = clone(src);
    const n = a.length;
    const frames = [];
    let comps = 0;
    function snap(title, text, marks) {
      push(frames, { kind: "array", title: title, text: text, a: clone(a), marks: marks });
    }
    snap(
      "Старт, k = " + k,
      "Сортировка выбором. Проход i ищет минимум на хвосте A[i..n] и ставит его на место i. Задание просит k = 5: после пяти проходов слева стоят пять наименьших. Ниже показан и хвост, если досортировать весь массив. Индексы с 1.",
      blank(n)
    );
    for (let i = 0; i < n - 1; i++) {
      if (i === k) {
        snap(
          "Граница k = " + k,
          "Пять проходов сделаны. A[1.." + k + "] = " + fmt(a.slice(0, k)) + ". Это и есть ответ задания. Дальше алгоритм тем же правилом добирает оставшиеся места, чтобы был виден весь ход.",
          (function () {
            const m = blank(n);
            for (let t = 0; t < k; t++) m[t] = "sorted";
            return m;
          })()
        );
      }
      let minI = i;
      const head = blank(n);
      for (let t = 0; t < i; t++) head[t] = "sorted";
      head[i] = "hot";
      snap(
        "Проход " + (i + 1) + ", ищем минимум справа",
        "Место A[" + (i + 1) + "] пока занято числом " + a[i] + ". Смотрим хвост A[" + (i + 1) + ".." + n + "] и запоминаем позицию минимума.",
        head
      );
      for (let j = i + 1; j < n; j++) {
        comps++;
        const m = blank(n);
        for (let t = 0; t < i; t++) m[t] = "sorted";
        m[minI] = "key";
        m[j] = "hot";
        if (a[j] < a[minI]) {
          snap(
            "A[" + (j + 1) + "] = " + a[j] + " меньше текущего минимума " + a[minI],
            "Новый минимум на позиции " + (j + 1) + ".",
            m
          );
          minI = j;
        } else {
          snap(
            "A[" + (j + 1) + "] = " + a[j] + " не меньше " + a[minI],
            "Минимум пока остаётся A[" + (minI + 1) + "] = " + a[minI] + ".",
            m
          );
        }
      }
      const m2 = blank(n);
      for (let t = 0; t <= i; t++) m2[t] = "sorted";
      if (minI !== i) {
        const left = a[i];
        const right = a[minI];
        const tmp = a[i];
        a[i] = a[minI];
        a[minI] = tmp;
        m2[i] = "written";
        snap(
          "Меняем A[" + (i + 1) + "] и A[" + (minI + 1) + "]",
          "Минимум хвоста " + right + " встаёт на место " + (i + 1) + ". Число " + left + " уезжает на его старое место.",
          m2
        );
      } else {
        snap(
          "Проход " + (i + 1) + ", обмен не нужен",
          "Минимум уже стоит на A[" + (i + 1) + "].",
          m2
        );
      }
    }
    snap(
      "Выбор готов",
      "Весь массив: " + fmt(a) + ". Сравнений: " + comps + ". Для сдачи задания достаточно первых " + k + " проходов. Полная сортировка выбором делает n - 1 проход и в худшем случае около n^2/2 сравнений. Устойчивой она не является: обмен может перенести ранний равный элемент через другой такой же. Здесь равных нет.",
      Array(n).fill("sorted")
    );
    return frames;
  }

  function recurrence(pa, pb) {
    const frames = [];
    const r = pa / pb;
    const lg = logLabel(pa, pb);
    const exactLog = pa === pb ? "1" : "log_" + pb + "(" + pa + ")";
    let closed;
    let theta;
    let master;
    if (pa < pb) {
      const coef = pb + "c / " + (pb - pa);
      closed = "T(n) = (" + coef + ") n + (T(1) - " + coef + ") n^" + exactLog;
      theta = "Θ(n)";
      master = "Случай 3. f(n) = cn растёт строго быстрее, чем n^" + exactLog + ", потому что 1 > " + lg + ". Берём ε = 1 - " + exactLog + " > 0, тогда f(n) = Ω(n^{" + exactLog + " + ε}). Регулярность: a*f(n/b) = " + pa + "*c*(n/" + pb + ") = (" + pa + "/" + pb + ") f(n). Дробь " + pa + "/" + pb + " меньше 1, условие выполнено. Теорема даёт T(n) = Θ(f(n)) = Θ(n).";
    } else if (pa > pb) {
      const coef = pb + "c / " + (pa - pb);
      closed = "T(n) = (T(1) + " + coef + ") n^" + exactLog + " - (" + coef + ") n";
      theta = "Θ(n^" + exactLog + ")";
      master = "Случай 1. log_" + pb + "(" + pa + ") = " + lg + " больше 1, поэтому n^" + exactLog + " растёт быстрее линейной функции. Есть ε > 0, при котором f(n) = cn = O(n^{" + exactLog + " - ε}). Теорема даёт T(n) = Θ(n^" + exactLog + "). Регулярность в случае 1 не нужна.";
    } else {
      closed = "T(n) = cn log_" + pb + "(n) + T(1) n";
      theta = "Θ(n log n)";
      master = "Случай 2. log_" + pb + "(" + pa + ") = 1 точно, f(n) = cn = Θ(n^{log_b(a)}) = Θ(n). Теорема даёт T(n) = Θ(n^{log_b(a)} log n) = Θ(n log n). Основание логарифма на границу Θ не влияет.";
    }
    const nCheck = pb * pb;
    const leafPow = Math.pow(pa, 2);
    const level0 = nCheck;
    const level1 = pa * pb;
    push(frames, {
      kind: "recur",
      title: "Формула варианта",
      text: "T(n) = " + pa + " T(n/" + pb + ") + cn, c > 1. Задача размера n порождает " + pa + " " + (pa >= 5 ? "задач" : "задачи") + " размера n/" + pb + ", и помимо них делается линейная работа cn. Константа c больше 1 и от n не зависит: на границу Θ она влияет только как множитель.",
      recur: { pa: pa, pb: pb, phase: 0 }
    });
    push(frames, {
      kind: "recur",
      title: "Корень дерева",
      text: "В корне стоимость cn: это работа вне рекурсии. Из корня выходит " + pa + " ребер к подзадачам размера n/" + pb + ".",
      recur: { pa: pa, pb: pb, phase: 1 }
    });
    push(frames, {
      kind: "recur",
      title: "Второй уровень",
      text: "Каждая из " + pa + " подзадач стоит c(n/" + pb + "). Весь уровень стоит " + pa + " * c * n / " + pb + " = cn * (" + pa + "/" + pb + "). Знаменатель геометрической прогрессии r = a/b = " + pa + "/" + pb + ".",
      recur: { pa: pa, pb: pb, phase: 2 }
    });
    push(frames, {
      kind: "recur",
      title: "Любой уровень и листья",
      text: "На уровне i задач " + pa + "^i, размер каждой n/" + pb + "^i, стоимость уровня cn * (" + pa + "/" + pb + ")^i. Высота до размера 1 равна h = log_" + pb + "(n). Листьев " + pa + "^h = n^" + exactLog + ". Каждый лист это константа T(1), все листья вместе Θ(n^" + exactLog + "). log_" + pb + "(" + pa + ") = " + lg + ".",
      recur: { pa: pa, pb: pb, phase: 3 }
    });
    push(frames, {
      kind: "recur",
      title: "Сумма по дереву",
      text: "Складываем уровни i от 0 до h-1 и прибавляем листья. " + closed + ". Это решение при n = " + pb + "^k и постоянном T(1).",
      recur: { pa: pa, pb: pb, phase: 4 }
    });
    push(frames, {
      kind: "recur",
      title: "Проверка на n = " + pb + "^2 = " + nCheck,
      text: "Два внутренних уровня: корень c*" + nCheck + " и " + pa + " узлов по c*" + pb + ". Сумма внутренних коэффициентов при c: " + level0 + " + " + level1 + " = " + (level0 + level1) + ". Листьев " + leafPow + ", их вклад T(1)*" + leafPow + ". Формула выше на этом n даёт ту же внутреннюю сумму. Дерево посчитано без пропусков.",
      recur: { pa: pa, pb: pb, phase: 5 }
    });
    push(frames, {
      kind: "recur",
      title: "Точная асимптотическая граница",
      text: "Меньшую степень отбрасываем. Точная граница, и сверху и снизу: " + theta + ". Запись Θ как раз это и означает.",
      recur: { pa: pa, pb: pb, phase: 6, theta: theta }
    });
    push(frames, {
      kind: "recur",
      title: "Основная теорема",
      text: master + " Итог совпадает с деревом: " + theta + ".",
      recur: { pa: pa, pb: pb, phase: 7, theta: theta }
    });
    return frames;
  }

  function buildWork(student) {
    const arr = student.arr.map(Number);
    const k = 5;
    return {
      student: student,
      tasks: [
        {
          id: "1", points: 2,
          title: "1. Сортировка вставками",
          frames: insertion(arr)
        },
        {
          id: "2", points: 2,
          title: "2. Сортировка слиянием",
          frames: mergeSort(arr)
        },
        {
          id: "3", points: 2,
          title: "3. Сортировка подсчётом",
          frames: counting(arr)
        },
        {
          id: "4", points: 3,
          title: "4. Пирамида, два случая",
          parts: [
            { title: "Невозрастающая", frames: heapSort(arr, "max") },
            { title: "Неубывающая", frames: heapSort(arr, "min") }
          ]
        },
        {
          id: "5", points: 2,
          title: "5. Быстрая сортировка",
          frames: quick(arr)
        },
        {
          id: "6", points: 2,
          title: "6. Сортировка выбором, k = " + k,
          frames: selection(arr, k)
        },
        {
          id: "7", points: 5,
          title: "7. Рекуррентность, a = " + student.pa + ", b = " + student.pb,
          frames: recurrence(Number(student.pa), Number(student.pb))
        }
      ]
    };
  }

  function flatFrames(task) {
    if (task.frames) return task.frames;
    const out = [];
    task.parts.forEach(function (part) {
      part.frames.forEach(function (frame) { out.push(frame); });
    });
    return out;
  }

  return { buildWork: buildWork, flatFrames: flatFrames, fmt: fmt };
});
