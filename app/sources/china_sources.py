"""中国创业团队数据源 - 带模拟数据和智谱AI分析"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import asyncio
import httpx
import os
import json

from app.core.models import StartupTeam, FundingStage


MOCK_STARTUPS = [
    {
        "name": "智谱AI",
        "description": "清华大学出身的AI大模型公司，专注于通用人工智能研究",
        "industry": "人工智能",
        "funding_stage": "D轮",
        "funding_amount": "25亿人民币",
        "location": "北京",
        "source": "模拟数据",
        "url": "https://www.zhipuai.cn",
    },
    {
        "name": "月之暗面",
        "description": "专注于长文本处理的大模型公司，Kimi智能助手开发商",
        "industry": "人工智能",
        "funding_stage": "B轮",
        "funding_amount": "10亿美元",
        "location": "北京",
        "source": "模拟数据",
        "url": "https://www.moonshot.cn",
    },
    {
        "name": "MiniMax",
        "description": "通用大模型公司，海螺AI和星野产品开发商",
        "industry": "人工智能",
        "funding_stage": "B轮",
        "funding_amount": "6亿美元",
        "location": "上海",
        "source": "模拟数据",
        "url": "https://www.minimaxi.com",
    },
    {
        "name": "百川智能",
        "description": "由前搜狗CEO王小川创立的大模型公司",
        "industry": "人工智能",
        "funding_stage": "A轮",
        "funding_amount": "3亿美元",
        "location": "北京",
        "source": "模拟数据",
        "url": "https://www.baichuan-ai.com",
    },
    {
        "name": "智元机器人",
        "description": "人形机器人公司，专注于具身智能研发",
        "industry": "机器人",
        "funding_stage": "A轮",
        "funding_amount": "6亿人民币",
        "location": "上海",
        "source": "模拟数据",
        "url": "https://www.zhiyuan-robot.com",
    },
]


@dataclass
class ZhipuAnalyzer:
    api_key: str = field(default_factory=lambda: os.getenv("ZHIPU_API_KEY", ""))
    base_url: str = "https://open.bigmodel.cn/api/paas/v4/"
    model: str = "glm-4-flash"
    
    async def analyze_team(self, team_data: dict) -> dict:
        if not self.api_key:
            print("⚠️ ZHIPU_API_KEY 未设置，跳过AI分析")
            return team_data
        
        prompt = f"""分析以下中国创业团队信息，提取关键信息并评估投资价值。

团队名称: {team_data.get("name", "")}
描述: {team_data.get("description", "")}
行业: {team_data.get("industry", "")}
融资阶段: {team_data.get("funding_stage", "")}
融资金额: {team_data.get("funding_amount", "")}

请以JSON格式返回分析结果，包含以下字段：
- summary: 一句话总结（20字以内）
- potential: 投资潜力评估（高/中/低）
- tags: 3-5个标签（数组）
- recommendation: 是否值得关注的简短理由（50字以内）

只返回JSON，不要其他内容。"""

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
                print(f"🤖 AI分析响应: {content[:100]}...")
                
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                ai_result = json.loads(content.strip())
                
                team_data["ai_summary"] = ai_result.get("summary", "")
                team_data["ai_potential"] = ai_result.get("potential", "中")
                team_data["ai_tags"] = ai_result.get("tags", [])
                team_data["ai_recommendation"] = ai_result.get("recommendation", "")
                team_data["ai_analyzed"] = True
                
                print(f"✅ AI分析完成: {team_data['name']} - {ai_result.get('summary', '')}")
                return team_data
                
            except Exception as e:
                print(f"❌ AI分析失败: {e}")
                team_data["ai_analyzed"] = False
                team_data["ai_error"] = str(e)
                return team_data
    
    async def test_connection(self) -> bool:
        if not self.api_key:
            print("❌ ZHIPU_API_KEY 未设置")
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
                        "messages": [{"role": "user", "content": "你好，请回复OK"}],
                        "max_tokens": 10,
                    }
                )
                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                print(f"✅ 智谱AI连接成功! 响应: {content}")
                return True
            except Exception as e:
                print(f"❌ 智谱AI连接失败: {e}")
                return False


@dataclass
class MockChinaSource:
    async def get_startups(self, limit: int = 10) -> list[dict]:
        print(f"📦 使用模拟数据 (limit={limit})")
        return MOCK_STARTUPS[:limit]


@dataclass
class ChinaStartupAggregator:
    mock_source: MockChinaSource = field(default_factory=MockChinaSource)
    analyzer: ZhipuAnalyzer = field(default_factory=ZhipuAnalyzer)
    
    async def collect_all(self, limit_per_source: int = 10) -> list[StartupTeam]:
        print("🚀 开始收集中国创业团队...")
        
        api_ok = await self.analyzer.test_connection()
        if not api_ok:
            print("⚠️ API测试失败，将跳过AI分析")
        
        raw_data = await self.mock_source.get_startups(limit_per_source)
        print(f"📊 获取到 {len(raw_data)} 条原始数据")
        
        teams = []
        for i, data in enumerate(raw_data, 1):
            print(f"\n[{i}/{len(raw_data)}] 分析: {data.get('name', '未知')}")
            
            if api_ok:
                enhanced_data = await self.analyzer.analyze_team(data)
            else:
                enhanced_data = data.copy()
                enhanced_data["ai_analyzed"] = False
            
            team = self._parse_to_startup(enhanced_data)
            if team:
                teams.append(team)
        
        print(f"\n✅ 共处理 {len(teams)} 个团队")
        return teams
    
    async def search(self, query: str, limit: int = 20) -> list[StartupTeam]:
        print(f"🔍 搜索: {query}")
        
        filtered = [
            s for s in MOCK_STARTUPS
            if query.lower() in s.get("name", "").lower() 
            or query.lower() in s.get("description", "").lower()
            or query.lower() in s.get("industry", "").lower()
        ]
        
        teams = []
        for data in filtered[:limit]:
            team = self._parse_to_startup(data)
            if team:
                teams.append(team)
        
        print(f"✅ 找到 {len(teams)} 个相关团队")
        return teams
    
    def _parse_to_startup(self, data: dict) -> StartupTeam | None:
        if not data:
            return None
        
        try:
            name = data.get("name") or data.get("title") or ""
            if not name:
                return None
            
            return StartupTeam(
                company_name=name[:100],
                description=data.get("description") or "",
                industry=data.get("industry") or "",
                funding_stage=self._parse_funding_stage(data),
                last_funding_round=data.get("funding_amount") or "",
                location=data.get("location") or "中国",
                sources=[data.get("source", "模拟数据")],
                website=data.get("url") or "",
                discovered_at=datetime.now(),
                last_updated=datetime.now(),
            )
        except Exception as e:
            print(f"❌ 解析失败: {e}")
            return None
    
    def _parse_funding_stage(self, data: dict) -> FundingStage:
        stage_str = (data.get("funding_stage") or data.get("round") or "").lower()
        
        if "天使" in stage_str or "种子" in stage_str:
            return FundingStage.SEED
        elif "pre-a" in stage_str or "pre a" in stage_str:
            return FundingStage.SEED
        elif "a轮" in stage_str:
            return FundingStage.SERIES_A
        elif "b轮" in stage_str:
            return FundingStage.SERIES_B
        elif "c轮" in stage_str:
            return FundingStage.SERIES_C
        elif "d轮" in stage_str or "e轮" in stage_str:
            return FundingStage.SERIES_D
        elif "ipo" in stage_str or "上市" in stage_str:
            return FundingStage.PUBLIC
        else:
            return FundingStage.SEED
