# %%
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import os
from tqdm import tqdm  # 添加进度条显示

# 完整品牌ID映射
brandid = {
    '小鹏': '275',
    '小米': '489',
    '理想': '345',
    '蔚来': '284',
    '特斯拉': '133',
    '零跑': '318',
    '比亚迪': '75',
    '极氪': '456',
    '奇瑞': '26',
    '埃安': '313',
    '华为': '509',
    '宝马': '15',
    '奔驰': '36',
    '奥迪': '33'
}

def get_sales_data(brand_id, date, retry_count=3):
    url = f"https://cars.app.autohome.com.cn/carext/recrank/all/getrecranklistpageresult2"
    params = {
        'from': '28',
        'pm': '2',
        'pluginversion': '11.65.0',
        'model': '1',
        'channel': '0',
        'pageindex': '1',
        'pagesize': '50',
        'typeid': '1',
        'subranktypeid': '2',  # 周度数据
        'levelid': '0',
        'price': '0-9000',
        'brandid': brand_id,
        'week': date
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for attempt in range(retry_count):
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.RequestException as e:
            if attempt == retry_count - 1:
                print(f"网络请求最终失败: {str(e)}")
                return None
            print(f"第{attempt + 1}次请求失败，正在重试...")
            time.sleep(2)  # 失败后等待2秒再重试
        except ValueError as e:
            print(f"JSON解析出错: {str(e)}")
            return None

def extract_car_info(data, brand_name, week_id):
    cars_list = []
    if data and 'result' in data and 'list' in data['result']:
        for car in data['result']['list']:
            car_info = {
                '汽车品牌': brand_name,
                '车型': car.get('seriesname', ''),
                '售价': car.get('priceinfo', ''),
                week_id: car.get('salecount', 0)
            }
            cars_list.append(car_info)
    return cars_list

def generate_week_dates():
    week_dates = []
    start_date = datetime(2025, 1, 1)  # 从2025年开始
    current_date = datetime.now()
    
    # 调整start_date到第一周的周二
    while start_date.weekday() != 1:  # 0是周一，1是周二
        start_date += timedelta(days=1)
    
    current_date = start_date
    while current_date <= datetime.now():
        week_dates.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(weeks=1)
    
    return week_dates

def main():
    # 创建一个空的DataFrame来存储所有品牌的数据
    all_brands_data = pd.DataFrame()
    
    # 获取周度日期列表
    week_dates = generate_week_dates()
    print(f"将获取从 {week_dates[0]} 到 {week_dates[-1]} 的周度数据")
    
    # 遍历每个品牌
    for brand_name, brand_id in tqdm(brandid.items(), desc="处理品牌"):
        brand_data_list = []
        print(f"\n开始处理品牌: {brand_name}")
        
        # 遍历每个周度获取数据
        for week_date in tqdm(week_dates, desc=f"处理{brand_name}的周度数据", leave=False):
            try:
                # 获取数据
                data = get_sales_data(brand_id, week_date)
                if data:
                    # 提取数据
                    week_data = extract_car_info(data, brand_name, week_date)
                    if week_data:  # 确保有数据再处理
                        # 转换为DataFrame
                        week_df = pd.DataFrame(week_data)
                        brand_data_list.append(week_df)
                
                time.sleep(1.5)  # 适当增加延时
            except Exception as e:
                print(f"处理品牌 {brand_name} 的 {week_date} 数据时出错: {str(e)}")
                continue
        
        # 合并当前品牌的所有周度数据
        if brand_data_list:
            brand_data = pd.concat(brand_data_list, ignore_index=True)
            # 按汽车品牌、车型、售价分组，对每个周的销量求和
            brand_data = brand_data.groupby(['汽车品牌', '车型', '售价'], as_index=False).sum()
            
            # 将当前品牌数据合并到总的DataFrame中
            all_brands_data = pd.concat([all_brands_data, brand_data], ignore_index=True)
            print(f"品牌 {brand_name} 的数据提取成功。")
        else:
            print(f"品牌 {brand_name} 的数据提取失败。")
    
    # 处理缺失值，将缺失的销量数据填充为0
    all_brands_data = all_brands_data.fillna(0)
    
    # 如果同文件夹下已经有这个excel文件，读取文件在基础上更新数据
    if os.path.exists('汽车销量数据_autohome_周度.xlsx'):
        try:
            old_data = pd.read_excel('汽车销量数据_autohome_周度.xlsx')
            # 合并新旧数据，根据汽车品牌、车型、售价进行合并
            merged_data = pd.merge(old_data, all_brands_data, on=['汽车品牌', '车型', '售价'], how='outer')
            # 找出新旧数据中相同周度的列
            common_columns = set(old_data.columns).intersection(set(all_brands_data.columns))
            common_columns = [col for col in common_columns if col not in ['汽车品牌', '车型', '售价']]
            # 更新相同周度的数据，使用新数据覆盖旧数据
            for col in common_columns:
                merged_data[col] = merged_data[col + '_y'].fillna(merged_data[col + '_x'])
                merged_data.drop([col + '_x', col + '_y'], axis=1, inplace=True)
            all_brands_data = merged_data
            print("已更新现有数据文件")
        except Exception as e:
            print(f"更新现有数据文件时出错: {str(e)}")
    
    # 分离固定列和周度列
    fixed_columns = ['汽车品牌', '车型', '售价']
    week_columns = [col for col in all_brands_data.columns if col not in fixed_columns]
    
    # 对周度列进行排序
    sorted_week_columns = sorted(week_columns, key=lambda x: pd.to_datetime(x))
    
    # 合并固定列和排序后的周度列
    sorted_columns = fixed_columns + sorted_week_columns
    
    # 按排序后的列重新排列 DataFrame
    all_brands_data = all_brands_data[sorted_columns]
    
    try:
        # 保存到Excel
        all_brands_data.to_excel('汽车销量数据_autohome_周度.xlsx', index=False)
        print("数据已保存到 汽车销量数据_autohome_周度.xlsx")
    except Exception as e:
        print(f"保存数据文件时出错: {str(e)}")
        # 尝试使用备份文件名保存
        try:
            backup_filename = f'汽车销量数据_autohome_周度_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            all_brands_data.to_excel(backup_filename, index=False)
            print(f"数据已保存到备份文件: {backup_filename}")
        except Exception as e:
            print(f"保存备份文件也失败: {str(e)}")
    
    return all_brands_data

if __name__ == "__main__":
    df = main() 
    
    


