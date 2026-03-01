"""中国创业团队真实数据源 - RSS/API/爬虫"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import asyncio
import httpx
import os
import json
import re

from app.core.models import StartupTeam, FundingStage


@dataclass
class LieyunwangRSSSource:
    base_url: str = "https://www.lieyunwang.com/newrss/feed.xml"
    
    async def get_startups(self, limit: int = 20) -> list[dict]:
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.get(self.base_url, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                })
                resp.raise_for_status()
                
                items = self._parse_rss(resp.text)
                funding_items = self._filter_funding_news(items)
                
                print(f"📡 猎云网RSS: 获取 {len(funding_items)} 条融资相关资讯")
                return funding_items[:limit]
            except Exception as e:
                print(f"❌ 猎云网RSS获取失败: {e}")
                return []
    
    def _parse_rss(self, xml_text: str) -> list[dict]:
        items = []
        item_pattern = r'<item>(.*?)</item>'
        for match in re.finditer(item_pattern, xml_text, re.DOTALL):
            item_xml = match.group(1)
            
            title = self._extract_tag(item_xml, 'title')
            link = self._extract_tag(item_xml, 'link')
            description = self._extract_tag(item_xml, 'description')
            pub_date = self._extract_tag(item_xml, 'pubDate')
            
            items.append({
                "title": title,
                "url": link,
                "description": description,
                "pub_date": pub_date,
                "source": "猎云网"
            })
        
        return items
    
    def _extract_tag(self, xml: str, tag: str) -> str:
        pattern = rf'<{tag}><!\[CDATA\[(.*?)\]\]></{tag}>'
        match = re.search(pattern, xml, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        pattern = rf'<{tag}>(.*?)</{tag}>'
        match = re.search(pattern, xml, re.DOTALL)
        return match.group(1).strip() if match else ""
    
    def _filter_funding_news(self, items: list[dict]) -> list[dict]:
        keywords = ["融资", "投资", "获投", "轮", "美元", "人民币", "完成", "领投", "创投"]
        filtered = []
        for item in items:
            title = item.get("title", "")
            desc = item.get("description", "")
            if any(kw in title or kw in desc for kw in keywords):
                filtered.append(item)
        return filtered


@dataclass
class Kr36Source:
    base_url: str = "https://36kr.com/newsflashes"
    
    async def get_startups(self, limit: int = 20) -> list[dict]:
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.get(self.base_url, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                })
                resp.raise_for_status()
                
                items = self._parse_newsflashes(resp.text)
                funding_items = self._filter_funding_news(items)
                
                print(f"📡 36氪: 获取 {len(funding_items)} 条融资相关资讯")
                return funding_items[:limit]
            except Exception as e:
                print(f"❌ 36氪获取失败: {e}")
                return []
    
    def _parse_newsflashes(self, html: str) -> list[dict]:
        items = []
        item_pattern = r'<a[^>]*class="[^"]*item-title[^"]*"[^>]*href="([^"]*)"[^>]*>([^<]*)</a>'
        
        for match in re.finditer(item_pattern, html, re.DOTALL):
            url = match.group(1)
            title = match.group(2).strip()
            
            if title and url:
                items.append({
                    "title": title,
                    "url": f"https://36kr.com{url}" if url.startswith("/") else url,
                    "description": "",
                    "source": "36氪"
                })
        
        return items
    
    def _filter_funding_news(self, items: list[dict]) -> list[dict]:
        keywords = ["融资", "投资", "获投", "轮", "美元", "人民币", "完成", "领投"]
        filtered = []
        for item in items:
            title = item.get("title", "")
            if any(kw in title for kw in keywords):
                filtered.append(item)
        return filtered


@dataclass
class ItjuziSource:
    base_url: str = "https://www.itjuzi.com/api/nicorn"
    
    async def get_startups(self, limit: int = 20) -> list[dict]:
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.get(
                    self.base_url,
                    params={"page": 1, "com_prov": "", "cat_id": "", "order_id": ""},
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Referer": "https://www.itjuzi.com/"
                    }
                )
                resp.raise_for_status()
                data = resp.json()
                
                items = []
                for company in data.get("data", {}).get("data", [])[:limit]:
                    items.append({
                        "name": company.get("com_name", ""),
                        "description": company.get("com_des", ""),
                        "industry": company.get("cat_name", ""),
                        "funding_stage": company.get("invst_stage", ""),
                        "funding_amount": company.get("money", ""),
                        "location": company.get("com_prov", ""),
                        "url": f"https://www.itjuzi.com/company/{company.get('com_id', '')}",
                        "source": "IT桔子"
                    })
                
                print(f"📡 IT桔子: 获取 {len(items)} 家独角兽公司")
                return items
            except Exception as e:
                print(f"❌ IT桔子获取失败: {e}")
                return []


@dataclass
class ZhipuAnalyzer:
    api_key: str = field(default_factory=lambda: os.getenv("ZHIPU_API_KEY", ""))
    base_url: str = "https://open.bigmodel.cn/api/paas/v4/"
    model: str = "glm-4-flash"
    
    async def analyze_team(self, team_data: dict) -> dict:
        if not self.api_key:
            return team_data
        
        prompt = f"""分析以下中国创业团队/融资资讯，提取关键信息。

标题/名称: {team_data.get("name") or team_data.get("title", "")}
描述: {team_data.get("description", "")}
行业: {team_data.get("industry", "")}
融资阶段: {team_data.get("funding_stage", "")}

请以JSON格式返回:
- summary: 一句话总结（20字以内）
- potential: 投资潜力（高/中/低）
- company_name: 公司名称（如果能识别）
- tags: 3-5个标签（数组）

只返回JSON。"""

        async with httpx.AsyncClient(timeout=60) as client:
            try:
                resp = await client.post(
                    f"{self.base_url}chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7,
                        "max_tokens": 500,
                    }
                )
                resp.raise_for_status()
                data = resp.json()
                
                content = data["choices"][0]["message"]["content"]
                
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                ai_result = json.loads(content.strip())
                
                team_data["ai_summary"] = ai_result.get("summary", "")
                team_data["ai_potential"] = ai_result.get("potential", "中")
                team_data["ai_tags"] = ai_result.get("tags", [])
                team_data["ai_company_name"] = ai_result.get("company_name", "")
                team_data["ai_analyzed"] = True
                
                print(f"✅ AI分析: {ai_result.get('summary', '')[:30]}")
                return team_data
                
            except Exception as e:
                print(f"⚠️ AI分析失败: {e}")
                team_data["ai_analyzed"] = False
                return team_data
    
    async def test_connection(self) -> bool:
        if not self.api_key:
            print("⚠️ ZHIPU_API_KEY 未设置")
            return False
        
        print(f"🔑 API Key: {self.api_key[:10]}...")
        
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.post(
                    f"{self.base_url}chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": "OK"}],
                        "max_tokens": 5,
                    }
                )
                resp.raise_for_status()
                print(f"✅ 智谱AI连接成功")
                return True
            except Exception as e:
                print(f"❌ 智谱AI连接失败: {e}")
                return False


@dataclass
class ChinaStartupAggregator:
    lieyunwang: LieyunwangRSSSource = field(default_factory=LieyunwangRSSSource)
    kr36: Kr36Source = field(default_factory=Kr36Source)
    itjuzi: ItjuziSource = field(default_factory=ItjuziSource)
    analyzer: ZhipuAnalyzer = field(default_factory=ZhipuAnalyzer)
    
    async def collect_all(self, limit_per_source: int = 10) -> list[StartupTeam]:
        print("🚀 开始从真实数据源收集中国创业团队...")
        
        api_ok = await self.analyzer.test_connection()
        
        tasks = [
            self.lieyunwang.get_startups(limit_per_source),
            self.kr36.get_startups(limit_per_source),
            self.itjuzi.get_startups(limit_per_source),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_data = []
        for result in results:
            if isinstance(result, list):
                all_data.extend(result)
        
        print(f"📊 共获取 {len(all_data)} 条原始数据")
        
        teams = []
        for i, data in enumerate(all_data, 1):
            if api_ok:
                enhanced_data = await self.analyzer.analyze_team(data)
            else:
                enhanced_data = data.copy()
                enhanced_data["ai_analyzed"] = False
            
            team = self._parse_to_startup(enhanced_data)
            if team:
                teams.append(team)
        
        print(f"✅ 共处理 {len(teams)} 个团队")
        return teams
    
    async def search(self, query: str, limit: int = 20) -> list[StartupTeam]:
        return []
    
    def _parse_to_startup(self, data: dict) -> StartupTeam | None:
        if not data:
            return None
        
        name = (
            data.get("ai_company_name") or 
            data.get("name") or 
            data.get("title") or 
            ""
        )
        if not name:
            return None
        
        return StartupTeam(
            company_name=name[:100],
            description=data.get("description") or "",
            industry=data.get("industry") or "",
            funding_stage=self._parse_funding_stage(data),
            last_funding_round=data.get("funding_amount") or "",
            location=data.get("location") or "中国",
            sources=[data.get("source", "未知")],
            website=data.get("url") or "",
            discovered_at=datetime.now(),
            last_updated=datetime.now(),
        )
    
    def _parse_funding_stage(self, data: dict) -> FundingStage:
        stage_str = (data.get("funding_stage") or "").lower()
        
        if "天使" in stage_str or "种子" in stage_str:
            return FundingStage.SEED
        elif "pre-a" in stage_str:
            return FundingStage.SEED
        elif "a轮" in stage_str:
            return FundingStage.SERIES_A
        elif "b轮" in stage_str:
            return FundingStage.SERIES_B
        elif "c轮" in stage_str:
            return FundingStage.SERIES_C
        elif "d轮" in stage_str or "e轮" in stage_str:
            return FundingStage.SERIES_D
        else:
            return FundingStage.SEED
