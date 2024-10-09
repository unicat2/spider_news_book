import os
import re
import math
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
import jieba


# 清洗中文文本，保留中文字符
def clean_text_chinese(text):
    return re.sub(r'[^\u4e00-\u9fff]', '', text) 

# 使用jieba分词进行中文词频统计
def tokenize_and_count_words(text):
    words = jieba.lcut(text)  
    return words

# 清洗英文文本
def clean_text_english(text):
    text = text.lower()  # 转小写
    text = re.sub(r'[^a-z\s]', '', text)  # 仅保留字母和空格
    text = re.sub(r'\s+', ' ', text).strip()  # 去除多余空格
    return text


# 去除标点符号
def remove_punctuation(text):
    return re.sub(r'[^\w\s]', '', text)

# 去除停用词
def remove_stopwords(text, stopwords):
    return ' '.join([word for word in text.split() if word not in stopwords])

# 去除数字
def remove_digits(text):
    return re.sub(r'\d+', '', text)

# 去除多余的空格
def remove_extra_spaces(text):
    return re.sub(r'\s+', ' ', text)

# 去除特殊字符
def remove_special_characters(text):
    return re.sub(r'[^a-zA-Z\s]', '', text)

# 读取txt文件
def read_txt_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

# 读取文件夹中的所有txt文件
def read_multiple_txt_files(directory):
    all_texts = []
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            filepath = os.path.join(directory, filename)
            print(f"正在读取文件: {filepath}")
            all_texts.append(read_txt_file(filepath))
    return all_texts

# 统计文本信息：清洗前后的字符数量
def report_text_statistics(original_text, cleaned_text):
    original_length = len(original_text)
    cleaned_length = len(cleaned_text)
    
    print(f"清洗前的文本规模（字符数）：{original_length}")
    print(f"清洗后的文本规模（字符数）：{cleaned_length}")
    
    return original_length, cleaned_length

# 计算熵
def calculate_entropy(text):
    letter_counts = Counter(text)
    total_letters = sum(letter_counts.values())
    entropy = 0
    for letter, count in letter_counts.items():
        p_x = count / total_letters
        entropy -= p_x * math.log2(p_x)
    return entropy

# 计算不同规模下的熵并输出每个规模对应的熵
def calculate_entropy_by_scale(text, scale_intervals):
    entropy_results = []
    
    for scale in scale_intervals:
        if len(text) >= scale:
            partial_text = text[:scale]
            entropy = calculate_entropy(partial_text)
            entropy_results.append((scale, entropy))
            print(f"文本规模: {scale} 字符, 熵: {entropy:.4f}")
    
    return entropy_results

# 计算齐夫定律（以词为单位）
def calculate_zipf_law(words):
    word_counts = Counter(words)
    sorted_word_counts = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_word_counts

# 绘制熵随规模变化图
def plot_entropy_variation(entropy_results, language, filename="entropy_variation.png"):
    scales = [scale for scale, entropy in entropy_results]
    entropies = [entropy for scale, entropy in entropy_results]

    plt.figure(figsize=(10, 6))
    plt.plot(scales, entropies, marker='o', linestyle='-', color='b')
    plt.title(f"Entropy Variation with Text Scale ({language})")
    plt.xlabel("Text Scale (number of characters)")
    plt.ylabel("Entropy")
    plt.grid(True)
    plt.savefig(filename)
    plt.show()

# 绘制齐夫定律验证图
def plot_zipf_law(word_counts, language, filename="zipf_law.png"):
    ranks = np.log(range(1, len(word_counts) + 1))
    frequencies = np.log([freq for word, freq in word_counts])

    plt.figure(figsize=(10, 6))
    plt.plot(ranks, frequencies, linestyle='-', color='b')
    plt.title(f"Zipf's Law Verification ({language})")
    plt.xlabel("Rank (log)")
    plt.ylabel("Frequency (log)")
    plt.grid(True)
    plt.savefig(filename)
    plt.show()

# 保存熵和齐夫定律的结果
def save_results(entropy_results, zipf_results, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("熵的变化:\n")
        for scale, entropy in entropy_results:
            f.write(f"文本规模: {scale}, 熵: {entropy:.4f}\n")

        f.write("\n齐夫定律验证:\n")
        for rank, (word, count) in enumerate(zipf_results, 1):
            f.write(f"Rank: {rank}, 词: {word}, 出现次数: {count}\n")








