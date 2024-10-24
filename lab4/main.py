import requests
import re
import time

# Функция для удаления HTML-тегов с использованием регулярных выражений
def remove_html_tags(text):
    clean = re.sub('<.*?>', '', text)
    return clean

# Наивный алгоритм поиска подстроки
def naive_search(text, pattern):
    positions = []
    n = len(text)
    m = len(pattern)
    for i in range(n - m + 1):
        if text[i:i + m] == pattern:
            positions.append(i)
    return positions

# Функция для построения префикс-функции для алгоритма Кнута-Морриса-Пратта
def build_kmp_table(pattern):
    m = len(pattern)
    kmp_table = [0] * m
    j = 0
    for i in range(1, m):
        while j > 0 and pattern[i] != pattern[j]:
            j = kmp_table[j - 1]
        if pattern[i] == pattern[j]:
            j += 1
            kmp_table[i] = j
    return kmp_table

# Алгоритм Кнута-Морриса-Пратта (КМП) для поиска подстроки
def kmp_search(text, pattern):
    positions = []
    n = len(text)
    m = len(pattern)
    kmp_table = build_kmp_table(pattern)
    j = 0
    for i in range(n):
        while j > 0 and text[i] != pattern[j]:
            j = kmp_table[j - 1]
        if text[i] == pattern[j]:
            j += 1
        if j == m:
            positions.append(i - m + 1)
            j = kmp_table[j - 1]
    return positions

# Функция для измерения времени выполнения поиска
def measure_time_search(search_func, text, pattern):
    start_time = time.time()
    positions = search_func(text, pattern)
    end_time = time.time()
    elapsed_time = end_time - start_time
    return positions, elapsed_time

# Загрузка веб-страницы и удаление HTML-тегов
def fetch_and_clean_text(url):
    response = requests.get(url)
    html_content = response.text
    cleaned_text = remove_html_tags(html_content)
    return cleaned_text

# Пример использования
url = "https://en.m.wikipedia.org/wiki/List_of_Glagolitic_books"
pattern = "Glagolitic"

# Получаем очищенный текст
text = fetch_and_clean_text(url)

# Наивный поиск
naive_positions, naive_time = measure_time_search(naive_search, text, pattern)
print(f"Наивный поиск нашел {len(naive_positions)} вхождений за {naive_time:.6f} секунд.")

# Поиск с помощью КМП
kmp_positions, kmp_time = measure_time_search(kmp_search, text, pattern)
print(f"КМП поиск нашел {len(kmp_positions)} вхождений за {kmp_time:.6f} секунд.")

# Сравнение результатов
print(f"Позиции, найденные наивным поиском: {naive_positions}")
print(f"Позиции, найденные КМП поиском: {kmp_positions}")
