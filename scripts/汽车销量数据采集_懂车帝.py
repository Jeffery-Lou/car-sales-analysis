import requests
import pandas as pd
from datetime import datetime, timedelta
import os
# 设置请求头，模拟浏览器访问
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

url_header = 'https://www.dongchedi.com/motor/pc/car/rank_data?'

def get_car_data(url, headers):
    try:
        # 发送 GET 请求
        response = requests.get(url, headers=headers)
        # 检查响应状态码
        if response.status_code == 200:
            # 解析 JSON 数据
            json_data = response.json()
            return json_data
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"网络请求出错: {str(e)}")
        return None
    except ValueError as e:
        print(f"JSON解析出错: {str(e)}")
        return None

def extract_car_data(json_data, month_id):
    try:
        # 创建一个空列表来存储数据
        data_list = []
        # 遍历json数据提取所需信息
        if json_data and 'data' in json_data and 'list' in json_data['data']:
            for item in json_data['data']['list']:
                car_data = {
                    '汽车品牌': item.get('brand_name', ''),
                    '车型': item.get('series_name', ''),
                    '售价': item.get('price', ''),
                    month_id: item.get('count', 0)
                }
                data_list.append(car_data)
        return data_list
    except Exception as e:
        print(f"数据提取出错: {str(e)}")
        return []

brand_id = {'小鹏': '195',
            '小米': '535',
            '理想': '202',
            '蔚来': '112',
            '特斯拉': '63',
            '零跑': '207',
            '比亚迪': '16',
            '智界': '883',
            '极氪': '426',
            '奇瑞': '18',
            '埃安': '242',
            'AITO': '483',
            '宝马': '4',
            '奔驰': '3',
            '奥迪': '2'
            }

# 获取当前日期
current_date = datetime.now()

# 获取当前月份的上一个月
last_month_date = current_date.replace(day=1) - timedelta(days=1)

month_ids = []
start_date = datetime(2022, 2, 1)

while start_date <= last_month_date:
    month_ids.append(start_date.strftime('%Y%m'))
    start_date = start_date + timedelta(days=32)  # 加32天确保跨月
    start_date = start_date.replace(day=1)  # 重置为下月1号
    
# 创建一个空的DataFrame来存储所有品牌的数据
all_brands_data = pd.DataFrame()

# 遍历每个品牌
for brand_name, brand_id_value in brand_id.items():
    brand_data_list = []

    # 遍历每个月份获取数据
    for month_id in month_ids:
        try:
            # 定义目标 URL
            url = url_header + 'brand_id=' + brand_id_value + '&month=' + month_id + '&rank_data_type=11&new_energy_type=1%2C2%2C3'

            # 获取数据
            json_data = get_car_data(url, headers)
            if json_data:
                # 提取数据
                month_data = extract_car_data(json_data, month_id)
                if month_data:  # 确保有数据再处理
                    # 转换为DataFrame
                    month_df = pd.DataFrame(month_data)
                    brand_data_list.append(month_df)
        except Exception as e:
            print(f"处理品牌 {brand_name} 的 {month_id} 数据时出错: {str(e)}")
            continue

    # 合并当前品牌的所有月份数据
    if brand_data_list:
        brand_data = pd.concat(brand_data_list, ignore_index=True)
        # 按汽车品牌、车型、售价分组，对每个月的销量求和
        brand_data = brand_data.groupby(['汽车品牌', '车型', '售价'], as_index=False).sum()

        # 将当前品牌数据合并到总的DataFrame中
        all_brands_data = pd.concat([all_brands_data, brand_data], ignore_index=True)
        print(f"品牌 {brand_name} 的数据提取成功。")
    else:
        print(f"品牌 {brand_name} 的数据提取失败。")

# 处理缺失值，将缺失的销量数据填充为0
all_brands_data = all_brands_data.fillna(0)

# 如果同文件夹下已经有这个CSV文件，读取文件在基础上更新数据
if os.path.exists('汽车销量数据.csv'):
    old_data = pd.read_csv('汽车销量数据.csv', encoding='utf-8-sig')
    # 合并新旧数据，根据汽车品牌、车型、售价进行合并
    merged_data = pd.merge(old_data, all_brands_data, on=['汽车品牌', '车型', '售价'], how='outer')
    # 找出新旧数据中相同月份的列
    common_columns = set(old_data.columns).intersection(set(all_brands_data.columns))
    common_columns = [col for col in common_columns if col not in ['汽车品牌', '车型', '售价']]
    # 更新相同月份的数据，使用新数据覆盖旧数据
    for col in common_columns:
        merged_data[col] = merged_data[col + '_y'].fillna(merged_data[col + '_x'])
        merged_data.drop([col + '_x', col + '_y'], axis=1, inplace=True)
    all_brands_data = merged_data

# 分离固定列和月份列
fixed_columns = ['汽车品牌', '车型', '售价']
month_columns = [col for col in all_brands_data.columns if col not in fixed_columns]

# 对月份列进行排序
sorted_month_columns = sorted(month_columns, key=lambda x: pd.to_datetime(x, format='%Y%m'))

# 合并固定列和排序后的月份列
sorted_columns = fixed_columns + sorted_month_columns

# 按排序后的列重新排列 DataFrame
all_brands_data = all_brands_data[sorted_columns]

# 保存为CSV文件，使用UTF-8编码
all_brands_data.to_csv('汽车销量数据.csv', index=False, encoding='utf-8-sig')