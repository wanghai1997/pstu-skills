# -*- coding: utf-8 -*-
"""
数据缓存管理模块
将AKShare获取的财务数据缓存到本地，避免重复API调用
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from .config import DATA_CONFIG


class CacheManager:
    """
    缓存管理器

    用于缓存从AKShare获取的财务数据，避免重复调用API
    支持JSON格式存储DataFrame数据
    """

    def __init__(self, cache_dir=None):
        """
        初始化缓存管理器

        Args:
            cache_dir: 缓存目录路径，默认使用配置中的路径
        """
        self.cache_dir = cache_dir or DATA_CONFIG["cache_dir"]
        self.valid_days = DATA_CONFIG["cache_valid_days"]

        # 确保缓存目录存在
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, symbol, data_type):
        """
        生成缓存文件路径

        Args:
            symbol: 股票代码，如 "600519"
            data_type: 数据类型，如 "balance_sheet", "income_statement"

        Returns:
            缓存文件的完整路径
        """
        # 文件命名格式：{股票代码}_{数据类型}.json
        filename = f"{symbol}_{data_type}.json"
        return os.path.join(self.cache_dir, filename)

    def _get_meta_path(self, symbol, data_type):
        """
        生成元数据文件路径（存储缓存时间等信息）

        Args:
            symbol: 股票代码
            data_type: 数据类型

        Returns:
            元数据文件的完整路径
        """
        filename = f"{symbol}_{data_type}_meta.json"
        return os.path.join(self.cache_dir, filename)

    def is_cache_valid(self, symbol, data_type):
        """
        检查缓存是否有效

        Args:
            symbol: 股票代码
            data_type: 数据类型

        Returns:
            bool: 缓存是否有效
        """
        meta_path = self._get_meta_path(symbol, data_type)

        # 元数据文件不存在，缓存无效
        if not os.path.exists(meta_path):
            return False

        # 数据文件不存在，缓存无效
        cache_path = self._get_cache_path(symbol, data_type)
        if not os.path.exists(cache_path):
            return False

        try:
            # 读取元数据
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            # 获取缓存时间
            cache_time = datetime.fromisoformat(meta['cache_time'])
            current_time = datetime.now()

            # 计算缓存有效期
            valid_days = self.valid_days.get(data_type, 7)
            expiration_time = cache_time + timedelta(days=valid_days)

            # 检查是否过期
            return current_time < expiration_time

        except Exception as e:
            print(f"检查缓存有效性时出错: {e}")
            return False

    def get_cache(self, symbol, data_type):
        """
        从缓存读取数据

        Args:
            symbol: 股票代码
            data_type: 数据类型

        Returns:
            DataFrame: 缓存的数据，如果缓存无效返回None
        """
        if not self.is_cache_valid(symbol, data_type):
            return None

        cache_path = self._get_cache_path(symbol, data_type)

        try:
            # 读取JSON并转换为DataFrame
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # JSON转换为DataFrame
            df = pd.DataFrame(data)
            return df

        except Exception as e:
            print(f"读取缓存时出错: {e}")
            return None

    def set_cache(self, symbol, data_type, data):
        """
        将数据写入缓存

        Args:
            symbol: 股票代码
            data_type: 数据类型
            data: DataFrame数据

        Returns:
            bool: 是否成功写入缓存
        """
        cache_path = self._get_cache_path(symbol, data_type)
        meta_path = self._get_meta_path(symbol, data_type)

        try:
            # DataFrame转换为JSON可序列化的格式
            # 处理可能的NaN和特殊值
            json_data = data.where(pd.notnull(data), None).to_dict(orient='records')

            # 写入数据文件
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)

            # 写入元数据文件
            meta = {
                'cache_time': datetime.now().isoformat(),
                'symbol': symbol,
                'data_type': data_type,
                'rows': len(data),
                'columns': list(data.columns) if hasattr(data, 'columns') else []
            }

            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            print(f"写入缓存时出错: {e}")
            return False

    def clear_cache(self, symbol=None, data_type=None):
        """
        清除缓存

        Args:
            symbol: 股票代码，为None则清除所有
            data_type: 数据类型，为None则清除该股票所有类型

        Returns:
            int: 清除的文件数量
        """
        count = 0

        try:
            if symbol is None:
                # 清除所有缓存
                for filename in os.listdir(self.cache_dir):
                    file_path = os.path.join(self.cache_dir, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        count += 1
            elif data_type is None:
                # 清除特定股票的所有缓存
                prefix = f"{symbol}_"
                for filename in os.listdir(self.cache_dir):
                    if filename.startswith(prefix):
                        file_path = os.path.join(self.cache_dir, filename)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                            count += 1
            else:
                # 清除特定股票特定类型的缓存
                cache_path = self._get_cache_path(symbol, data_type)
                meta_path = self._get_meta_path(symbol, data_type)

                if os.path.exists(cache_path):
                    os.remove(cache_path)
                    count += 1

                if os.path.exists(meta_path):
                    os.remove(meta_path)
                    count += 1

            return count

        except Exception as e:
            print(f"清除缓存时出错: {e}")
            return count

    def get_cache_info(self):
        """
        获取缓存统计信息

        Returns:
            dict: 缓存信息
        """
        try:
            files = os.listdir(self.cache_dir)
            json_files = [f for f in files if f.endswith('.json') and not f.endswith('_meta.json')]

            # 统计各类型缓存数量
            type_count = {}
            for filename in json_files:
                # 文件名格式：{symbol}_{data_type}.json
                parts = filename.replace('.json', '').split('_')
                if len(parts) >= 2:
                    data_type = parts[-1]
                    type_count[data_type] = type_count.get(data_type, 0) + 1

            return {
                'total_files': len(json_files),
                'total_meta_files': len([f for f in files if f.endswith('_meta.json')]),
                'by_type': type_count,
                'cache_dir': self.cache_dir
            }

        except Exception as e:
            print(f"获取缓存信息时出错: {e}")
            return {'error': str(e)}
