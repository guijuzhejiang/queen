#!/usr/bin/env bash

run_with_log() {
    local script_path=$1
    shift

    # 检查脚本文件是否存在
    if [ ! -f "$script_path" ]; then
        echo "错误: 脚本文件 '$script_path' 不存在"
        return 1
    fi

    # 创建logs目录（如果不存在）
    mkdir -p logs

    local script_name=$(basename "$script_path" .sh)
    local log_file="logs/${script_name}_$(date +%Y%m%d%H%M%S).log"

    echo "开始执行: $script_path"
    echo "日志文件: $log_file"
    echo "参数: $@"

    # 执行脚本并记录日志
    nohup "$script_path" "$@" > "$log_file" 2>&1 &
    local pid=$!

    echo "进程PID: $pid"
    echo "Started $script_path, log: $log_file, PID: $pid"

    return 0
}

# 调用函数
run_with_log ./queen_data_preprocess/train2render.sh /home/zzg/data/CV/dynerf/cut_roasted_beef 1
#run_with_log ./queen_data_preprocess/preprocess2render.sh /home/zzg/data/CV/dynerf/cut_roasted_beef 1