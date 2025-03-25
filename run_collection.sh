#!/bin/bash

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 激活 Conda 环境（如果你使用 conda 的话）
source ~/opt/anaconda3/etc/profile.d/conda.sh
conda activate base

# 运行数据采集脚本
python run_data_collection.py

# 如果数据采集成功，提交到 Git
if [ $? -eq 0 ]; then
    # 添加所有更改
    git add .
    
    # 提交更改，使用当前日期作为提交信息
    git commit -m "自动更新: $(date '+%Y-%m-%d %H:%M:%S')"
    
    # 推送到远程仓库
    git push
fi 