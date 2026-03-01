from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import asyncio
import httpx
from bs4 import BeautifulSoup
import re

from app.core import settings, StartupTeam, FundingStage


@dataclass
class CrunchbaseSource:
    api_key: str = field(default_factory=lambda: settings.crunchbase_api_key)
    base_url: str = "https://api.crunchbase.com/api/v4"
    
    async def search_organizations(
        self,
        query: str,
        funding_stages: list[str] | None = None,
        industries: list[str] | None = None,
        limit: int = 20,
    ) -> list[dict]:
        if not self.api_key:
            return []
        
        endpoint = f"{self.base_url}/searches/organizations"
        payload = {
            "field_ids": [
                "identifier", "name", "short_description", "categories",
                "funding_total", "funding_stage", "founded_on", "location_identifiers",
                "num_employees_enum", "linkedin", "website", "last_funding_at"
            ],
            "order": [{"field_id": "funding_total", "sort": "desc"}],
            "limit": limit,
            "query": query,
        }
        
        if funding_stages:
            payload["filters"] = {"funding_stage": funding_stages}
        if industries:
            payload["filters"] = payload.get("filters", {})
            payload["filters"]["categories"] = industries
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                endpoint,
                params={"user_key": self.api_key},
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("entities", [])
    
    async def get_organization(self, uuid: str) -> dict | None:
        if not self.api_key:
            return None
        
        endpoint = f"{self.base_url}/entities/organizations/{uuid}"
        params = {
            "user_key": self.api_key,
            "card_ids": ["founders", "investors", "press", "jobs"],
        }
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(endpoint, params=params)
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.json()


@dataclass
class TechCrunchSource:
    base_url: str = "https://techcrunch.com"
    
    async def search_startups(self, query: str, limit: int = 10) -> list[dict]:
        search_url = f"{self.base_url}/?s={query}"
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(search_url, follow_redirects=True)
            resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, "lxml")
        articles = []
        
        for article in soup.select("article")[:limit]:
            title_elem = article.select_one("h2 a, h3 a")
            if not title_elem:
                continue
            
            excerpt_elem = article.select_one(".excerpt")
            date_elem = article.select_one("time")
            
            articles.append({
                "title": title_elem.get_text(strip=True),
                "url": title_elem.get("href", ""),
                "excerpt": excerpt_elem.get_text(strip=True) if excerpt_elem else "",
                "date": date_elem.get("datetime", "") if date_elem else "",
            })
        
        return articles
    
    async def get_funding_news(self, days: int = 7) -> list[dict]:
        funding_url = f"{self.base_url}/tag/funding-rounds/"
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(funding_url, follow_redirects=True)
            resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, "lxml")
        articles = []
        
        for article in soup.select("article")[:20]:
            title_elem = article.select_one("h2 a, h3 a")
            if not title_elem:
                continue
            
            excerpt_elem = article.select_one(".excerpt")
            
            articles.append({
                "title": title_elem.get_text(strip=True),
                "url": title_elem.get("href", ""),
                "excerpt": excerpt_elem.get_text(strip=True) if excerpt_elem else "",
            })
        
        return articles


@dataclass  
class ProductHuntSource:
    base_url: str = "https://www.producthunt.com"
    
    async def get_trending_startups(self, limit: int = 20) -> list[dict]:
        url = f"{self.base_url}/v1/posts"
        params = {"days_ago": 0, "per_page": limit}
        
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
                return data.get("posts", [])
            except Exception:
                return []
    
    async def search_products(self, query: str, limit: int = 10) -> list[dict]:
        url = f"{self.base_url}/v1/posts/all"
        params = {"search[query]": query, "per_page": limit}
        
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
                return data.get("posts", [])
            except Exception:
                return []


@dataclass
class GitHubTrendingSource:
    base_url: str = "https://github.com"
    
    async def get_trending_repos(self, language: str = "", since: str = "weekly") -> list[dict]:
        url = f"{self.base_url}/trending/{language}"
        params = {"since": since}
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, "lxml")
        repos = []
        
        for repo in soup.select("article.Box-row")[:25]:
            name_elem = repo.select_one("h2 a")
            if not name_elem:
                continue
            
            name = name_elem.get("href", "").strip("/")
            description = repo.select_one("p")
            stars_elem = repo.select_one("a[href*='/stargazers']")
            lang_elem = repo.select_one("span[itemprop='programmingLanguage']")
            
            repos.append({
                "name": name,
                "url": f"{self.base_url}/{name}",
                "description": description.get_text(strip=True) if description else "",
                "stars": stars_elem.get_text(strip=True) if stars_elem else "0",
                "language": lang_elem.get_text(strip=True) if lang_elem else "",
            })
        
        return repos
    
    async def get_startup_repos(self, keywords: list[str], limit: int = 20) -> list[dict]:
        query = "+".join(keywords)
        url = f"{self.base_url}/search"
        params = {"q": query, "type": "repositories"}
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, "lxml")
        repos = []
        
        for repo in soup.select("div.repo-list-item")[:limit]:
            name_elem = repo.select_one("a.v-align-middle")
            if not name_elem:
                continue
            
            desc_elem = repo.select_one("p")
            
            repos.append({
                "name": name_elem.get_text(strip=True),
                "url": f"{self.base_url}{name_elem.get('href', '')}",
                "description": desc_elem.get_text(strip=True) if desc_elem else "",
            })
        
        return repos
