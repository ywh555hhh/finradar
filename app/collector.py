"""团队收集器 - 使用真实数据源和智谱AI分析"""
import asyncio
import json
from datetime import datetime
from pathlib import Path

from app.sources.china_sources import ChinaStartupAggregator
from app.core.models import StartupTeam


class TeamCollector:
    def __init__(self, output_dir: str = "data"):
        self.aggregator = ChinaStartupAggregator()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    async def collect_all(self, limit_per_source: int = 10) -> list[dict]:
        print(f"🔍 开始收集中国创业团队 (每源 {limit_per_source} 个)...")
        
        teams = await self.aggregator.collect_all(limit_per_source)
        
        result = []
        for t in teams:
            team_dict = {
                "name": t.company_name,
                "description": t.description,
                "industry": t.industry,
                "funding_stage": t.funding_stage.value,
                "funding_amount": t.last_funding_round,
                "location": t.location,
                "sources": t.sources,
                "website": t.website,
                "discovered_at": t.discovered_at.isoformat() if t.discovered_at else None,
            }
            result.append(team_dict)
        
        print(f"✅ 共收集 {len(result)} 个团队")
        return result
    
    async def search(self, query: str, limit: int = 20) -> list[dict]:
        print(f"🔍 搜索: {query}")
        
        teams = await self.aggregator.search(query, limit)
        
        result = []
        for t in teams:
            result.append({
                "name": t.company_name,
                "description": t.description,
                "industry": t.industry,
                "funding_stage": t.funding_stage.value,
                "funding_amount": t.last_funding_round,
                "location": t.location,
                "sources": t.sources,
                "website": t.website,
                "discovered_at": t.discovered_at.isoformat() if t.discovered_at else None,
            })
        
        print(f"✅ 找到 {len(result)} 个相关团队")
        return result
    
    def save(self, teams: list[dict], filename: str = "collected_teams.json") -> Path:
        filepath = self.output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(teams, f, ensure_ascii=False, indent=2)
        print(f"💾 已保存到: {filepath}")
        return filepath
    
    def load(self, filename: str = "collected_teams.json") -> list[dict]:
        filepath = self.output_dir / filename
        if not filepath.exists():
            return []
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def merge(self, new_teams: list[dict], filename: str = "collected_teams.json") -> list[dict]:
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
            
            src_list = t.get("sources", [])
            for src in src_list:
                sources[src] = sources.get(src, 0) + 1
            
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
    
    teams = await collector.collect_all(limit_per_source=10)
    
    if teams:
        collector.save(teams)
        collector.print_stats(teams)
        
        print("\n📋 收集结果示例:")
        for t in teams[:5]:
            print(f"\n--- {t['name'][:50]} ---")
            print(f"  行业: {t.get('industry', 'N/A')}")
            print(f"  融资: {t.get('funding_stage', 'N/A')} - {t.get('funding_amount', 'N/A')}")
            print(f"  地点: {t.get('location', 'N/A')}")
            print(f"  来源: {t.get('sources', [])}")
    else:
        print("❌ 未收集到任何团队")


if __name__ == "__main__":
    asyncio.run(main())
