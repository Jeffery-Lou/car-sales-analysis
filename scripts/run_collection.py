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
        logging.StreamHandler(sys.stdout)
    ]
)

def run_script(script_path):
    """运行指定的Python脚本并返回执行状态"""
    try:
        logging.info(f"开始运行脚本: {script_path}")
        # 获取脚本的绝对路径
        abs_script_path = os.path.abspath(script_path)
        # 获取脚本所在目录
        script_dir = os.path.dirname(abs_script_path)
        
        # 设置工作目录为脚本所在目录
        current_dir = os.getcwd()
        os.chdir(script_dir)
        
        result = subprocess.run(
            [sys.executable, abs_script_path],
            check=True,
            capture_output=True,
            text=True
        )
        
        # 恢复原来的工作目录
        os.chdir(current_dir)
        
        logging.info(f"脚本 {script_path} 执行成功")
        if result.stdout:
            logging.info(f"输出: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"脚本 {script_path} 执行失败: {str(e)}")
        if e.stderr:
            logging.error(f"错误输出: {e.stderr}")
        return False
    except Exception as e:
        logging.error(f"运行脚本 {script_path} 时发生错误: {str(e)}")
        return False

def main():
    # 记录开始时间
    start_time = datetime.now()
    logging.info(f"开始数据采集任务 - {start_time}")
    
    # 获取项目根目录
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root_dir)
    
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
            logging.error(f"脚本 {script} 执行失败")
        else:
            logging.info(f"脚本 {script} 执行成功")
    
    # 记录结束时间和总用时
    end_time = datetime.now()
    duration = end_time - start_time
    logging.info(f"数据采集任务结束 - 总用时: {duration}")
    
    # 如果有脚本失败，返回非零状态码
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main() 