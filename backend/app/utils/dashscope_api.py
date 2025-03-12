import os
import requests
import json
import time
from flask import current_app

class DashScopeAPI:
    """
    DashScope API 调用工具类
    """
    
    def __init__(self, api_key=None):
        self.api_key = api_key or current_app.config['DASHSCOPE_API_KEY']
        self.base_url = 'https://dashscope.aliyuncs.com/api/v1'
        self.headers = {
            'X-DashScope-Async': 'enable',
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def generate_surname_art(self, payload):
        """
        提交百家姓生成任务
        
        Args:
            payload (dict): 请求参数
            
        Returns:
            dict: 任务ID和状态
        """
        if not self.api_key:
            raise ValueError("API Key is required")
        
        url = f"{self.base_url}/services/aigc/wordart/surnames"
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error submitting task: {str(e)}")
            if hasattr(e, 'response') and e.response:
                current_app.logger.error(f"Response: {e.response.text}")
            raise
    
    def get_task_status(self, task_id):
        """
        获取任务状态
        
        Args:
            task_id (str): 任务ID
            
        Returns:
            dict: 任务状态和结果
        """
        if not self.api_key:
            raise ValueError("API Key is required")
        
        url = f"{self.base_url}/tasks/{task_id}"
        
        try:
            response = requests.get(url, headers={
                'Authorization': f'Bearer {self.api_key}'
            })
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error checking task status: {str(e)}")
            if hasattr(e, 'response') and e.response:
                current_app.logger.error(f"Response: {e.response.text}")
            raise
    
    def wait_for_task_completion(self, task_id, max_attempts=30, interval=2):
        """
        等待任务完成
        
        Args:
            task_id (str): 任务ID
            max_attempts (int): 最大尝试次数
            interval (int): 轮询间隔（秒）
            
        Returns:
            dict: 任务结果
        """
        attempts = 0
        
        while attempts < max_attempts:
            task_data = self.get_task_status(task_id)
            
            if task_data['output']['task_status'] == 'SUCCEEDED':
                return task_data
            elif task_data['output']['task_status'] == 'FAILED':
                error_message = task_data['output'].get('message', '任务执行失败')
                raise Exception(error_message)
            
            time.sleep(interval)
            attempts += 1
        
        raise Exception("任务执行超时") 