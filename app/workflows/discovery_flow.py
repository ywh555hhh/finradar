from datetime import datetime, timedelta
from typing import Any
from pathlib import Path
import json

from prefect import flow, task, get_run_logger
from prefect.cache_policies import NONE

from app.core import settings, StartupTeam, FundingStage
from app.sources import CrunchbaseSource, TechCrunchSource, ProductHuntSource, GitHubTrendingSource
from app.agents.dspy_signatures import StartupDiscoveryAgent, configure_dspy
from app.agents.outreach_agent import OutreachAgent, CandidateProfile
from app.processors import NotificationManager


CANDIDATE_PROFILE = CandidateProfile(
    name="Your Name",
    email="your.email@example.com",
    linkedin_url="https://linkedin.com/in/yourprofile",
    github_url="https://github.com/yourusername",
    current_role="Software Engineer",
    skills=["Python", "TypeScript", "React", "Node.js", "Machine Learning", "AWS", "Docker"],
    experience_years=3,
    education="BS Computer Science",
    interests=["AI/ML", "Fintech", "Developer Tools", "Open Source"],
    target_roles=["Software Engineer", "ML Engineer", "Full-Stack Developer"],
    preferred_locations=["Remote", "San Francisco", "New York", "Singapore"],
    seeking=["Full-time", "Internship"],
)


@task(cache_policy=NONE, retries=2, retry_delay_seconds=30)
async def discover_startups_from_sources(
    industries: list[str],
    stages: list[str],
    limit_per_source: int = 20,
) -> list[dict]:
    cb = CrunchbaseSource()
    tc = TechCrunchSource()
    ph = ProductHuntSource()
    gh = GitHubTrendingSource()
    
    all_startups = []
    
    for industry in industries:
        for stage in stages:
            try:
                cb_results = await cb.search_organizations(
                    query=industry,
                    funding_stages=[stage],
                    limit=limit_per_source,
                )
                all_startups.extend(cb_results)
            except Exception:
                pass
    
    try:
        funding_news = await tc.get_funding_news(days=7)
        for article in funding_news:
            all_startups.append({
                "name": article.get("title", "").split(" Raises ")[0].split(" raises ")[0],
                "source": "TechCrunch",
                "discovery_reason": "Recent funding news",
                "url": article.get("url", ""),
            })
    except Exception:
        pass
    
    try:
        trending = await ph.get_trending_startups(limit=limit_per_source)
        for product in trending:
            all_startups.append({
                "name": product.get("name", ""),
                "description": product.get("tagline", ""),
                "source": "ProductHunt",
                "discovery_reason": "Trending on ProductHunt",
                "url": f"https://producthunt.com/posts/{product.get('slug', '')}",
            })
    except Exception:
        pass
    
    seen = set()
    unique = []
    for s in all_startups:
        name = s.get("name", "").lower()
        if name and name not in seen:
            seen.add(name)
            unique.append(s)
    
    return unique


@task(cache_policy=NONE)
async def assess_startup_fit(startup_data: dict) -> dict:
    configure_dspy()
    agent = OutreachAgent(CANDIDATE_PROFILE)
    
    fit_result = agent.assess_fit(startup_data)
    
    return {
        "startup": startup_data,
        "fit_score": fit_result["fit_score"],
        "matching_skills": fit_result["matching_skills"],
        "recommended_role": fit_result["recommended_role"],
        "conversation_starters": fit_result["conversation_starters"],
    }


@task(cache_policy=NONE)
async def notify_startup(startup_data: dict, fit_score: float) -> dict:
    if fit_score < 60:
        return {"status": "skipped", "reason": "Fit score too low"}
    
    configure_dspy()
    agent = OutreachAgent(CANDIDATE_PROFILE)
    
    notification = agent.generate_notification(startup_data)
    
    notifier = NotificationManager()
    results = await notifier.notify_startup(startup_data, notification)
    
    return {
        "status": "notified",
        "notification": notification,
        "channels": results,
        "team_notified": any(results.values()),
    }


@task(cache_policy=NONE)
async def notify_user_of_discovery(
    startup_data: dict,
    fit_score: float,
    outreach_results: dict,
) -> bool:
    notifier = NotificationManager()
    return await notifier.notify_user(startup_data, fit_score, outreach_results)


@task(cache_policy=NONE)
async def generate_outreach_materials(startup_data: dict, position: str) -> dict:
    configure_dspy()
    agent = OutreachAgent(CANDIDATE_PROFILE)
    
    email = agent.generate_email(startup_data, position)
    
    founders = startup_data.get("founders", [])
    linkedin_messages = []
    for founder in founders[:3]:
        msg = agent.generate_linkedin_message(founder)
        linkedin_messages.append({
            "recipient": founder.get("name", "Founder"),
            "message": msg,
        })
    
    return {
        "email": email,
        "linkedin_messages": linkedin_messages,
        "ready_to_send": True,
    }


@flow(name="Continuous Startup Discovery and Outreach", log_prints=True)
async def continuous_discovery(
    industries: list[str] | None = None,
    funding_stages: list[str] | None = None,
    min_fit_score: float = 65.0,
    notify_startups: bool = True,
    notify_user: bool = True,
    max_discoveries: int = 30,
) -> dict[str, Any]:
    logger = get_run_logger()
    
    if not industries:
        industries = ["AI", "Developer Tools", "Fintech", "Infrastructure"]
    if not funding_stages:
        funding_stages = ["Seed", "Series A", "Series B"]
    
    results = {
        "discovered_count": 0,
        "high_fit_count": 0,
        "startups_notified": 0,
        "user_notifications_sent": 0,
        "top_startups": [],
        "outreach_materials": {},
        "errors": [],
    }
    
    startups = await discover_startups_from_sources(
        industries=industries,
        stages=funding_stages,
        limit_per_source=max_discoveries // 4,
    )
    results["discovered_count"] = len(startups)
    logger.info(f"Discovered {len(startups)} startups")
    
    assessed = []
    for startup in startups[:max_discoveries]:
        try:
            fit = await assess_startup_fit(startup)
            assessed.append(fit)
            
            if fit["fit_score"] >= min_fit_score:
                results["high_fit_count"] += 1
        except Exception as e:
            results["errors"].append(f"Assessment error: {str(e)}")
    
    assessed.sort(key=lambda x: x["fit_score"], reverse=True)
    top_startups = assessed[:10]
    results["top_startups"] = [
        {
            "name": s["startup"].get("name", "Unknown"),
            "fit_score": s["fit_score"],
            "recommended_role": s["recommended_role"],
            "matching_skills": s["matching_skills"],
        }
        for s in top_startups
    ]
    
    for assessment in top_startups[:5]:
        startup = assessment["startup"]
        fit_score = assessment["fit_score"]
        
        try:
            outreach = await notify_startup(startup, fit_score)
            
            if notify_user:
                user_notified = await notify_user_of_discovery(
                    startup, fit_score, outreach
                )
                if user_notified:
                    results["user_notifications_sent"] += 1
            
            if outreach.get("team_notified"):
                results["startups_notified"] += 1
            
            position = assessment.get("recommended_role", "Software Engineer")
            materials = await generate_outreach_materials(startup, position)
            
            startup_name = startup.get("name", "unknown").lower().replace(" ", "_")
            results["outreach_materials"][startup_name] = materials
            
        except Exception as e:
            results["errors"].append(f"Outreach error for {startup.get('name', 'unknown')}: {str(e)}")
    
    logger.info(
        f"Discovery complete: {results['discovered_count']} found, "
        f"{results['high_fit_count']} high-fit, "
        f"{results['startups_notified']} notified"
    )
    
    return results


@flow(name="Weekly Deep Scan", log_prints=True)
async def weekly_deep_scan(
    target_sectors: list[str] | None = None,
) -> dict[str, Any]:
    if not target_sectors:
        target_sectors = [
            "Artificial Intelligence",
            "Machine Learning Infrastructure",
            "Developer Tools",
            "Cloud Infrastructure",
            "Fintech",
            "Healthcare AI",
        ]
    
    results = await continuous_discovery(
        industries=target_sectors,
        funding_stages=["Seed", "Series A", "Series B"],
        min_fit_score=70.0,
        notify_startups=True,
        notify_user=True,
        max_discoveries=50,
    )
    
    return results


if __name__ == "__main__":
    import asyncio
    result = asyncio.run(continuous_discovery())
    print(json.dumps(result, indent=2, default=str))
