import subprocess
import sys
import logging
from datetime import datetime
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_collection.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def run_script(script_path):
    """运行指定的Python脚本并返回执行状态"""
    try:
        logging.info(f"开始运行脚本: {script_path}")
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            capture_output=True,
            text=True
        )
        logging.info(f"脚本 {script_path} 执行成功")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"脚本 {script_path} 执行失败: {str(e)}")
        logging.error(f"错误输出: {e.stderr}")
        return False

def main():
    # 确保数据目录存在
    os.makedirs('data', exist_ok=True)
    
    # 记录开始时间
    start_time = datetime.now()
    logging.info(f"开始数据采集任务 - {start_time}")
    
    # 定义要运行的脚本列表
    scripts = [
        'scripts/汽车销售数据采集_汽车之家.py',
        'scripts/汽车销量数据采集_懂车帝.py'
    ]
    
    # 运行所有脚本
    success = True
    for script in scripts:
        if not run_script(script):
            success = False
    
    # 记录结束时间和总用时
    end_time = datetime.now()
    duration = end_time - start_time
    logging.info(f"数据采集任务结束 - 总用时: {duration}")
    
    # 如果有脚本失败，返回非零状态码
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main() 