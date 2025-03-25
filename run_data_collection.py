import subprocess
import logging
from datetime import datetime
import os

# 设置日志
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    filename=os.path.join(log_dir, f"data_collection_{datetime.now().strftime('%Y%m%d')}.log"),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_script(script_name):
    try:
        logging.info(f"开始运行 {script_name}")
        result = subprocess.run(['python', script_name], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        logging.info(f"{script_name} 运行成功")
        logging.debug(f"输出: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logging.error(f"{script_name} 运行失败")
        logging.error(f"错误信息: {e.stderr}")
    except Exception as e:
        logging.error(f"{script_name} 运行时发生异常: {str(e)}")

def main():
    logging.info("开始数据采集任务")
    
    # 运行汽车之家数据采集
    run_script("汽车销售数据采集_汽车之家.py")
    
    # 运行懂车帝数据采集
    run_script("汽车销量数据采集_懂车帝.py")
    
    logging.info("数据采集任务完成")

if __name__ == "__main__":
    main() 