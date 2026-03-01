"""中国创业团队数据源 - 36氪、IT桔子、创业邦等"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import asyncio
import httpx
from bs4 import BeautifulSoup
import re
import json

from app.core import settings, StartupTeam, FundingStage


@dataclass
class Kr36Source:
    """36氪 - 中国领先的新经济媒体"""
    base_url: str = "https://36kr.com"
    
    async def get_hot_startups(self, limit: int = 20) -> list[dict]:
        """获取热门创业公司"""
        url = f"{self.base_url}/api/newsflash"
        params = {"per_page": limit}
        
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.get(url, params=params, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                })
                resp.raise_for_status()
                data = resp.json()
                return data.get("data", {}).get("items", [])[:limit]
            except Exception:
                return []
    
    async def search_startups(self, query: str, limit: int = 10) -> list[dict]:
        """搜索创业公司"""
        url = f"{self.base_url}/api/search"
        params = {"keyword": query, "per_page": limit}
        
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.get(url, params=params, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                })
                resp.raise_for_status()
                data = resp.json()
                return data.get("data", {}).get("items", [])[:limit]
            except Exception:
                return []
    
    async def get_funding_news(self, days: int = 7) -> list[dict]:
        """获取融资快讯"""
        url = f"{self.base_url}/api/newsflash"
        params = {"per_page": 30}
        
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.get(url, params=params, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                })
                resp.raise_for_status()
                data = resp.json()
                items = data.get("data", {}).get("items", [])
                # 过滤融资相关
                funding_keywords = ["融资", "投资", "获投", "轮", "美元", "人民币"]
                return [
                    item for item in items 
                    if any(kw in item.get("title", "") or kw in item.get("description", "") for kw in funding_keywords)
                ][:20]
            except Exception:
                return []


@dataclass
class ItjuziSource:
    """IT桔子 - 创投数据平台"""
    base_url: str = "https://www.itjuzi.com"
    
    async def get_hot_investments(self, limit: int = 20) -> list[dict]:
        """获取热门投资事件"""
        url = f"{self.base_url}/api/datacenter/investmentEvents"
        
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.get(url, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                })
                resp.raise_for_status()
                data = resp.json()
                return data.get("data", {}).get("list", [])[:limit]
            except Exception:
                return []
    
    async def search_company(self, query: str, limit: int = 10) -> list[dict]:
        """搜索公司"""
        url = f"{self.base_url}/api/search"
        params = {"keyword": query, "type": "company"}
        
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.get(url, params=params, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                })
                resp.raise_for_status()
                data = resp.json()
                return data.get("data", {}).get("list", [])[:limit]
            except Exception:
                return []


@dataclass
class LieyunwangSource:
    """猎云网 - 创业媒体"""
    base_url: str = "https://www.lieyunwang.com"
    
    async def get_latest_news(self, limit: int = 20) -> list[dict]:
        """获取最新创业资讯"""
        url = f"{self.base_url}/latest/p"
        
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.get(url, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                })
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "lxml")
                
                articles = []
                for item in soup.select("li.article-item")[:limit]:
                    title_elem = item.select_one("h3 a")
                    if not title_elem:
                        continue
                    
                    articles.append({
                        "title": title_elem.get_text(strip=True),
                        "url": title_elem.get("href", ""),
                        "source": "猎云网"
                    })
                
                return articles
            except Exception:
                return []


@dataclass
class CyzoneSource:
    """创业邦 - 创业服务平台"""
    base_url: str = "https://www.cyzone.cn"
    
    async def get_startups(self, limit: int = 20) -> list[dict]:
        """获取创业公司"""
        url = f"{self.base_url}/company"
        
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.get(url, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                })
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "lxml")
                
                companies = []
                for item in soup.select(".company-item")[:limit]:
                    name_elem = item.select_one(".company-name a")
                    if not name_elem:
                        continue
                    
                    desc_elem = item.select_one(".company-desc")
                    tag_elem = item.select_one(".company-tag")
                    
                    companies.append({
                        "name": name_elem.get_text(strip=True),
                        "url": name_elem.get("href", ""),
                        "description": desc_elem.get_text(strip=True) if desc_elem else "",
                        "tags": tag_elem.get_text(strip=True) if tag_elem else "",
                        "source": "创业邦"
                    })
                
                return companies
            except Exception:
                return []


@dataclass
class WeixinSource:
    """微信公众号文章搜索"""
    
    async def search_articles(self, query: str, limit: int = 10) -> list[dict]:
        """搜索微信文章"""
        # 使用搜狗微信搜索
        url = "https://weixin.sogou.com/weixin"
        params = {"type": 2, "query": query, "page": 1}
        
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.get(url, params=params, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                })
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "lxml")
                
                articles = []
                for item in soup.select(".news-box .txt-box")[:limit]:
                    title_elem = item.select_one("h3 a")
                    if not title_elem:
                        continue
                    
                    account_elem = item.select_one(".account")
                    date_elem = item.select_one(".s2")
                    
                    articles.append({
                        "title": title_elem.get_text(strip=True),
                        "url": title_elem.get("href", ""),
                        "account": account_elem.get_text(strip=True) if account_elem else "",
                        "date": date_elem.get_text(strip=True) if date_elem else "",
                        "source": "微信公众号"
                    })
                
                return articles
            except Exception:
                return []


@dataclass
class ChinaStartupAggregator:
    """中国创业团队聚合器"""
    kr36: Kr36Source = field(default_factory=Kr36Source)
    itjuzi: ItjuziSource = field(default_factory=ItjuziSource)
    lieyunwang: LieyunwangSource = field(default_factory=LieyunwangSource)
    cyzone: CyzoneSource = field(default_factory=CyzoneSource)
    weixin: WeixinSource = field(default_factory=WeixinSource)
    
    async def collect_all(self, limit_per_source: int = 10) -> list[StartupTeam]:
        """从所有来源收集创业团队"""
        tasks = [
            self.kr36.get_funding_news(limit_per_source),
            self.itjuzi.get_hot_investments(limit_per_source),
            self.lieyunwang.get_latest_news(limit_per_source),
            self.cyzone.get_startups(limit_per_source),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        teams = []
        for result in results:
            if isinstance(result, list):
                for item in result:
                    team = self._parse_to_startup(item)
                    if team:
                        teams.append(team)
        
        return teams
    
    async def search(self, query: str, limit: int = 20) -> list[StartupTeam]:
        """搜索创业团队"""
        tasks = [
            self.kr36.search_startups(query, limit),
            self.itjuzi.search_company(query, limit),
            self.weixin.search_articles(query + " 融资", limit),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        teams = []
        for result in results:
            if isinstance(result, list):
                for item in result:
                    team = self._parse_to_startup(item)
                    if team:
                        teams.append(team)
        
        return teams[:limit]
    
    def _parse_to_startup(self, data: dict) -> StartupTeam | None:
        """解析数据为StartupTeam"""
        if not data:
            return None
        
        try:
            name = data.get("name") or data.get("title") or data.get("com_name") or ""
            if not name:
                return None
            
            return StartupTeam(
                name=name[:100],
                description=data.get("description") or data.get("intro") or data.get("excerpt") or "",
                industry=data.get("industry") or data.get("scope") or "",
                funding_stage=self._parse_funding_stage(data),
                funding_amount=data.get("money") or data.get("funding") or "",
                location=data.get("city") or data.get("location") or "中国",
                source=data.get("source") or "36氪",
                url=data.get("url") or data.get("link") or "",
                collected_at=datetime.now(),
            )
        except Exception:
            return None
    
    def _parse_funding_stage(self, data: dict) -> FundingStage:
        """解析融资阶段"""
        stage_str = (data.get("round") or data.get("funding_stage") or "").lower()
        
        if "天使" in stage_str or "种子" in stage_str:
            return FundingStage.SEED
        elif "pre-a" in stage_str or "pre a" in stage_str:
            return FundingStage.PRE_SEED
        elif "a轮" in stage_str:
            return FundingStage.SERIES_A
        elif "b轮" in stage_str:
            return FundingStage.SERIES_B
        elif "c轮" in stage_str:
            return FundingStage.SERIES_C
        elif "d轮" in stage_str or "e轮" in stage_str:
            return FundingStage.SERIES_D
        elif "ipo" in stage_str or "上市" in stage_str:
            return FundingStage.IPO
        elif "并购" in stage_str:
            return FundingStage.ACQUIRED
        else:
            return FundingStage.UNKNOWN
