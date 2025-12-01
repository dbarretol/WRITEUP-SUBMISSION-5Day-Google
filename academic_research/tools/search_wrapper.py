"""Academic search wrapper for optimizing Google Search queries and results."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re
from datetime import datetime


@dataclass
class SearchResult:
    """Structured search result for academic literature."""
    title: str
    url: str
    snippet: str
    source: Optional[str] = None
    year: Optional[int] = None
    authors: Optional[str] = None
    relevance_score: float = 0.0


class AcademicSearchWrapper:
    """Wrapper for google_search with academic optimization."""
    
    # Academic sources with higher authority
    ACADEMIC_SOURCES = [
        'arxiv.org',
        'scholar.google.com',
        'ieee.org',
        'acm.org',
        'springer.com',
        'sciencedirect.com',
        'ncbi.nlm.nih.gov',
        'researchgate.net',
        'semanticscholar.org',
        'jstor.org',
        'wiley.com',
        'nature.com',
        'science.org',
    ]
    
    def __init__(self):
        """Initialize the academic search wrapper."""
        self.current_year = datetime.now().year
    
    def build_academic_query(
        self,
        research_area: str,
        field_of_study: str,
        keywords: Optional[List[str]] = None,
        year_constraint: Optional[int] = None
    ) -> str:
        """
        Build an optimized search query for academic literature.
        
        Args:
            research_area: The specific research area (e.g., "Multi-Agent Systems")
            field_of_study: Broader field (e.g., "Computer Science")
            keywords: Additional keywords to include
            year_constraint: Optional year to constrain results (e.g., 2024)
        
        Returns:
            Optimized search query string
        """
        # Base query with research area
        query_parts = [f'"{research_area}"']
        
        # Add field context
        query_parts.append(field_of_study)
        
        # Add academic qualifiers
        query_parts.append("research OR paper OR study")
        
        # Add keywords if provided
        if keywords:
            keyword_str = " OR ".join(keywords[:3])  # Limit to top 3 keywords
            query_parts.append(f"({keyword_str})")
        
        # Add year constraint if specified
        if year_constraint:
            query_parts.append(f"after:{year_constraint-1}")
        
        # Prefer academic sources
        source_constraint = " OR ".join([f"site:{src}" for src in self.ACADEMIC_SOURCES[:5]])
        query_parts.append(f"({source_constraint})")
        
        return " ".join(query_parts)
    
    def parse_search_results(
        self,
        raw_results: List[Dict[str, Any]]
    ) -> List[SearchResult]:
        """
        Parse and structure raw search results.
        
        Args:
            raw_results: Raw results from google_search tool
        
        Returns:
            List of structured SearchResult objects
        """
        parsed_results = []
        
        for result in raw_results:
            # Extract basic fields
            title = result.get('title', 'Untitled')
            url = result.get('link', result.get('url', ''))
            snippet = result.get('snippet', result.get('description', ''))
            
            # Try to extract year from snippet or URL
            year = self._extract_year(snippet, url)
            
            # Identify source domain
            source = self._extract_source(url)
            
            # Create structured result
            search_result = SearchResult(
                title=title,
                url=url,
                snippet=snippet,
                source=source,
                year=year,
                authors=None,  # Could be enhanced with author extraction
                relevance_score=0.0  # Will be scored separately
            )
            
            parsed_results.append(search_result)
        
        return parsed_results
    
    def _extract_year(self, snippet: str, url: str) -> Optional[int]:
        """Extract publication year from snippet or URL."""
        # Look for 4-digit year in snippet
        text = f"{snippet} {url}"
        year_matches = re.findall(r'\b(19|20)\d{2}\b', text)
        
        if year_matches:
            # Get most recent plausible year
            years = [int(y) for y in year_matches]
            valid_years = [y for y in years if 1990 <= y <= self.current_year]
            if valid_years:
                return max(valid_years)
        
        return None
    
    def _extract_source(self, url: str) -> Optional[str]:
        """Extract source domain from URL."""
        if not url:
            return None
        
        try:
            # Extract domain
            domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
            if domain_match:
                domain = domain_match.group(1)
                
                # Check if it's a known academic source
                for academic_source in self.ACADEMIC_SOURCES:
                    if academic_source in domain:
                        return domain
                
                return domain
        except:
            pass
        
        return None
    
    def score_relevance(
        self,
        result: SearchResult,
        research_area: str,
        keywords: Optional[List[str]] = None
    ) -> float:
        """
        Score the relevance of a search result for academic purposes.
        
        Scoring breakdown:
        - Domain relevance (40%): Match to research area in title/snippet
        - Recency (20%): Publication year weight
        - Source authority (20%): Academic vs general source
        - Keyword density (20%): Presence of key terms
        
        Args:
            result: SearchResult to score
            research_area: The research area to match against
            keywords: Additional keywords for matching
        
        Returns:
            Relevance score between 0.0 and 1.0
        """
        score = 0.0
        
        # Combine searchable text
        text = f"{result.title} {result.snippet}".lower()
        research_area_lower = research_area.lower()
        
        # 1. Domain relevance (40%)
        if research_area_lower in text:
            score += 0.4
        elif any(word in text for word in research_area_lower.split()):
            score += 0.2  # Partial match
        
        # 2. Recency (20%)
        if result.year:
            year_diff = self.current_year - result.year
            if year_diff <= 1:
                score += 0.20
            elif year_diff <= 3:
                score += 0.15
            elif year_diff <= 5:
                score += 0.10
            else:
                score += 0.05
        
        # 3. Source authority (20%)
        if result.source:
            if any(academic in result.source for academic in self.ACADEMIC_SOURCES):
                score += 0.20
            else:
                score += 0.05  # Some credit for having a source
        
        # 4. Keyword density (20%)
        if keywords:
            keyword_matches = sum(1 for kw in keywords if kw.lower() in text)
            keyword_score = min(keyword_matches / len(keywords), 1.0) * 0.20
            score += keyword_score
        
        return min(score, 1.0)
    
    def filter_and_rank_results(
        self,
        results: List[SearchResult],
        research_area: str,
        keywords: Optional[List[str]] = None,
        top_n: int = 10,
        min_score: float = 0.3
    ) -> List[SearchResult]:
        """
        Score, filter, and rank search results by relevance.
        
        Args:
            results: List of SearchResult objects
            research_area: Research area for scoring
            keywords: Optional keywords for scoring
            top_n: Number of top results to return
            min_score: Minimum relevance score threshold
        
        Returns:
            Filtered and ranked list of top results
        """
        # Score all results
        for result in results:
            result.relevance_score = self.score_relevance(
                result,
                research_area,
                keywords
            )
        
        # Filter by minimum score
        filtered = [r for r in results if r.relevance_score >= min_score]
        
        # Sort by score (descending)
        ranked = sorted(filtered, key=lambda r: r.relevance_score, reverse=True)
        
        # Return top N
        return ranked[:top_n]
    
    def format_for_literature(
        self,
        results: List[SearchResult]
    ) -> List[Dict[str, str]]:
        """
        Format search results for the preliminary_literature field.
        
        Args:
            results: List of SearchResult objects
        
        Returns:
            List of dictionaries with title, relevance, and link
        """
        formatted = []
        
        for result in results:
            # Create relevance note
            relevance_parts = []
            if result.year:
                relevance_parts.append(f"Recent publication ({result.year})")
            if result.source:
                source_name = result.source.replace('.com', '').replace('.org', '').replace('www.', '')
                relevance_parts.append(f"from {source_name}")
            
            # Add snippet context
            snippet_preview = result.snippet[:100] + "..." if len(result.snippet) > 100 else result.snippet
            relevance_parts.append(snippet_preview)
            
            relevance = ". ".join(relevance_parts) if relevance_parts else "Relevant to research area"
            
            formatted.append({
                "title": result.title,
                "relevance": relevance,
                "link": result.url
            })
        
        return formatted
