"""团队收集器 - 简化版，专注收集中国创业团队"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from app.sources.china_sources import ChinaStartupAggregator
from app.core.models import StartupTeam


class TeamCollector:
    """创业团队收集器"""
    
    def __init__(self, output_dir: str = "data"):
        self.aggregator = ChinaStartupAggregator()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    async def collect_all(self, limit_per_source: int = 15) -> list[dict]:
        """从所有来源收集团队"""
        print(f"🔍 开始收集中国创业团队 (每源 {limit_per_source} 个)...")
        
        teams = await self.aggregator.collect_all(limit_per_source)
        
        result = []
        for t in teams:
            result.append({
                "name": t.name,
                "description": t.description,
                "industry": t.industry,
                "funding_stage": t.funding_stage.value,
                "funding_amount": t.funding_amount,
                "location": t.location,
                "source": t.source,
                "url": t.url,
                "collected_at": t.collected_at.isoformat() if t.collected_at else None,
            })
        
        print(f"✅ 共收集 {len(result)} 个团队")
        return result
    
    async def search(self, query: str, limit: int = 20) -> list[dict]:
        """搜索团队"""
        print(f"🔍 搜索: {query}")
        
        teams = await self.aggregator.search(query, limit)
        
        result = []
        for t in teams:
            result.append({
                "name": t.name,
                "description": t.description,
                "industry": t.industry,
                "funding_stage": t.funding_stage.value,
                "funding_amount": t.funding_amount,
                "location": t.location,
                "source": t.source,
                "url": t.url,
                "collected_at": t.collected_at.isoformat() if t.collected_at else None,
            })
        
        print(f"✅ 找到 {len(result)} 个相关团队")
        return result
    
    def save(self, teams: list[dict], filename: str = "collected_teams.json") -> Path:
        """保存到JSON文件"""
        filepath = self.output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(teams, f, ensure_ascii=False, indent=2)
        print(f"💾 已保存到: {filepath}")
        return filepath
    
    def load(self, filename: str = "collected_teams.json") -> list[dict]:
        """加载已收集的团队"""
        filepath = self.output_dir / filename
        if not filepath.exists():
            return []
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def merge(self, new_teams: list[dict], filename: str = "collected_teams.json") -> list[dict]:
        """合并新旧数据，去重"""
        existing = self.load(filename)
        existing_names = {t["name"] for t in existing}
        
        added = 0
        for t in new_teams:
            if t["name"] not in existing_names:
                existing.append(t)
                existing_names.add(t["name"])
                added += 1
        
        self.save(existing, filename)
        print(f"📝 新增 {added} 个团队，总计 {len(existing)} 个")
        return existing
    
    def stats(self, teams: list[dict]) -> dict:
        """统计信息"""
        if not teams:
            return {"total": 0}
        
        industries = {}
        stages = {}
        sources = {}
        locations = {}
        
        for t in teams:
            ind = t.get("industry") or "未知"
            industries[ind] = industries.get(ind, 0) + 1
            
            stage = t.get("funding_stage") or "未知"
            stages[stage] = stages.get(stage, 0) + 1
            
            source = t.get("source") or "未知"
            sources[source] = sources.get(source, 0) + 1
            
            loc = t.get("location") or "未知"
            locations[loc] = locations.get(loc, 0) + 1
        
        return {
            "total": len(teams),
            "industries": dict(sorted(industries.items(), key=lambda x: -x[1])[:10]),
            "stages": dict(sorted(stages.items(), key=lambda x: -x[1])),
            "sources": dict(sorted(sources.items(), key=lambda x: -x[1])),
            "locations": dict(sorted(locations.items(), key=lambda x: -x[1])[:10]),
        }
    
    def print_stats(self, teams: list[dict]):
        """打印统计"""
        s = self.stats(teams)
        
        print("\n" + "=" * 50)
        print("📊 收集统计")
        print("=" * 50)
        print(f"总计: {s['total']} 个团队\n")
        
        if s.get("industries"):
            print("行业分布 (Top 10):")
            for k, v in list(s["industries"].items())[:10]:
                print(f"  - {k}: {v}")
        
        if s.get("stages"):
            print("\n融资阶段:")
            for k, v in s["stages"].items():
                print(f"  - {k}: {v}")
        
        if s.get("sources"):
            print("\n数据来源:")
            for k, v in s["sources"].items():
                print(f"  - {k}: {v}")
        
        if s.get("locations"):
            print("\n地区分布 (Top 10):")
            for k, v in list(s["locations"].items())[:10]:
                print(f"  - {k}: {v}")
        
        print("=" * 50)


async def main():
    collector = TeamCollector()
    
    teams = await collector.collect_all(limit_per_source=15)
    collector.merge(teams)
    collector.print_stats(collector.load())


if __name__ == "__main__":
    asyncio.run(main())
