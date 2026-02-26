"""
缓存管理模块
"""
import json
import hashlib
from datetime import datetime, timedelta


class LocalCache:
    """本地内存缓存（不依赖 Redis）"""
    
    def __init__(self, max_size=100, ttl_hours=24):
        self.cache = {}
        self.max_size = max_size
        self.ttl = timedelta(hours=ttl_hours)
    
    def get(self, key):
        """获取缓存"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            # 检查是否过期
            if datetime.now() - timestamp < self.ttl:
                return value
            else:
                # 删除过期缓存
                del self.cache[key]
                return None
        return None
    
    def set(self, key, value):
        """设置缓存"""
        # 如果缓存已满，删除最旧的项
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        
        self.cache[key] = (value, datetime.now())
    
    def delete(self, key):
        """删除缓存"""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, use_redis=False, redis_config=None):
        self.use_redis = use_redis
        self.redis_client = None
        
        if use_redis and redis_config:
            try:
                import redis
                self.redis_client = redis.Redis(
                    host=redis_config.get('host', 'localhost'),
                    port=redis_config.get('port', 6379),
                    db=redis_config.get('db', 0),
                    decode_responses=True
                )
                self.redis_client.ping()
            except Exception as e:
                print(f"Redis 连接失败: {e}，使用本地缓存")
                self.use_redis = False
        
        # 使用本地缓存作为备选
        self.local_cache = LocalCache()
    
    @staticmethod
    def generate_key(prefix, data):
        """
        生成缓存键
        """
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        hash_value = hashlib.md5(data_str.encode()).hexdigest()
        return f"{prefix}:{hash_value}"
    
    def get(self, key):
        """获取缓存"""
        if self.use_redis and self.redis_client:
            try:
                return self.redis_client.get(key)
            except Exception as e:
                print(f"Redis 获取缓存失败: {e}")
                return self.local_cache.get(key)
        else:
            return self.local_cache.get(key)
    
    def set(self, key, value, ttl_hours=24):
        """设置缓存"""
        if self.use_redis and self.redis_client:
            try:
                # 转换为 JSON 字符串
                value_str = json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value)
                self.redis_client.setex(key, int(ttl_hours * 3600), value_str)
            except Exception as e:
                print(f"Redis 设置缓存失败: {e}")
                self.local_cache.set(key, value)
        else:
            self.local_cache.set(key, value)
    
    def delete(self, key):
        """删除缓存"""
        if self.use_redis and self.redis_client:
            try:
                self.redis_client.delete(key)
            except Exception as e:
                print(f"Redis 删除缓存失败: {e}")
                self.local_cache.delete(key)
        else:
            self.local_cache.delete(key)
    
    def clear(self):
        """清空缓存"""
        if self.use_redis and self.redis_client:
            try:
                self.redis_client.flushdb()
            except Exception as e:
                print(f"Redis 清空缓存失败: {e}")
                self.local_cache.clear()
        else:
            self.local_cache.clear()
