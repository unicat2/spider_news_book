from utils.common_fun import *



if __name__ == "__main__":
    directory = "english_data"  
    texts = read_multiple_txt_files(directory)
    
    # 合并所有文本并进行清洗
    original_text = " ".join(texts)
    cleaned_text = clean_text_english(original_text)
    
    # 统计文本规模
    original_length, cleaned_length = report_text_statistics(original_text, cleaned_text)
    
    # 定义文本规模间隔
    scale_intervals = list(range(100000000, cleaned_length, 10000000))
    
    # 计算熵随文本规模的变化
    entropy_results = calculate_entropy_by_scale(cleaned_text, scale_intervals)
    
    # 验证齐夫定律（以词为单位）
    zipf_results = calculate_zipf_law(cleaned_text.split())
    
    # 绘制熵随文本规模变化图
    plot_entropy_variation(entropy_results, "English", "english_entropy_variation.png")
    
    # 绘制齐夫定律图
    plot_zipf_law(zipf_results, "English", "english_zipf_law.png")
    
    # 保存结果
    save_results(entropy_results, zipf_results, "english_analysis_results.txt")
