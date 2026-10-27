#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

static std::vector<int> readBin(const std::string& file) {
    std::ifstream input(file, std::ios::binary);
    std::int32_t n = 0;
    input.read(reinterpret_cast<char*>(&n), 4);
    std::vector<int> values(static_cast<std::size_t>(n));
    input.read(reinterpret_cast<char*>(values.data()), static_cast<std::streamsize>(4) * n);
    return values;
}

static double medianOf(double* samples, int count) {
    std::sort(samples, samples + count);
    return samples[(count - 1) / 2];
}

template <typename Func>
static double timeSort(const std::vector<int>& values, Func func) {
    double times[5];
    std::vector<int> work(values.size());
    for (int attempt = 0; attempt < 6; attempt++) {
        work = values;
        const auto started = std::chrono::steady_clock::now();
        func(work);
        const auto elapsed = std::chrono::steady_clock::now() - started;
        if (attempt) {
            times[attempt - 1] = std::chrono::duration<double, std::milli>(elapsed).count();
        }
    }
    if (!std::is_sorted(work.begin(), work.end())) {
        std::cerr << "cpp sort failed\n";
        std::exit(1);
    }
    return medianOf(times, 5);
}

struct Item {
    int value;
    int id;
};

static bool stableOk(bool stable) {
    Item items[400];
    for (int i = 0; i < 400; i++) items[i] = Item{i % 5, i};
    auto less = [](const Item& left, const Item& right) { return left.value < right.value; };
    if (stable) std::stable_sort(items, items + 400, less);
    else std::sort(items, items + 400, less);
    for (int i = 1; i < 400; i++) {
        if (items[i].value == items[i - 1].value && items[i].id < items[i - 1].id) return false;
    }
    return true;
}

int main(int argc, char** argv) {
    std::ifstream manifest(argv[1]);
    std::string line;
    while (std::getline(manifest, line)) {
        if (line.empty()) continue;
        std::istringstream parts(line);
        std::string pattern, size, file;
        parts >> pattern >> size >> file;
        const std::vector<int> values = readBin(file);
        const double quick = timeSort(values, [](std::vector<int>& work) { std::sort(work.begin(), work.end()); });
        const double merge = timeSort(values, [](std::vector<int>& work) { std::stable_sort(work.begin(), work.end()); });
        std::cout << "TIME\tcpp_sort\t" << pattern << "\t" << size << "\t" << quick << "\n";
        std::cout << "TIME\tcpp_stable\t" << pattern << "\t" << size << "\t" << merge << "\n";
    }
    std::cout << "STABLE\tcpp_sort\t" << (stableOk(false) ? "yes" : "no") << "\n";
    std::cout << "STABLE\tcpp_stable\t" << (stableOk(true) ? "yes" : "no") << "\n";
    return 0;
}
