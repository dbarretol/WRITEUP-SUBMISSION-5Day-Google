"""
Demo script showing how to use the AcademicSearchWrapper.

This demonstrates:
1. Building optimized academic search queries
2. Parsing and structuring search results
3. Scoring relevance
4. Filtering and ranking results
5. Formatting citations
"""

import asyncio
from academic_research.tools.search_wrapper import AcademicSearchWrapper, SearchResult
from academic_research.tools.citation_formatter import CitationFormatter


def demo_query_building():
    """Demonstrate query optimization."""
    print("=" * 80)
    print("QUERY BUILDING DEMO")
    print("=" * 80)
    
    wrapper = AcademicSearchWrapper()
    
    # Example 1: Basic query
    query1 = wrapper.build_academic_query(
        research_area="Multi-Agent Systems",
        field_of_study="Computer Science"
    )
    print(f"\n1. Basic Query:\n   {query1}\n")
    
    # Example 2: With keywords
    query2 = wrapper.build_academic_query(
        research_area="Multi-Agent Systems",
        field_of_study="Computer Science",
        keywords=["coordination", "cooperation", "game theory"]
    )
    print(f"2. With Keywords:\n   {query2}\n")
    
    # Example 3: With year constraint
    query3 = wrapper.build_academic_query(
        research_area="Multi-Agent Systems",
        field_of_study="Computer Science",
        keywords=["reinforcement learning"],
        year_constraint=2023
    )
    print(f"3. With Year Constraint:\n   {query3}\n")


def demo_result_parsing():
    """Demonstrate result parsing and scoring."""
    print("\n" + "=" * 80)
    print("RESULT PARSING & SCORING DEMO")
    print("=" * 80)
    
    wrapper = AcademicSearchWrapper()
    
    # Simulate search results
    mock_results = [
        {
            "title": "Multi-Agent Coordination: A Survey",
            "link": "https://arxiv.org/abs/2024.12345",
            "snippet": "This 2024 survey explores coordination mechanisms in multi-agent systems..."
        },
        {
            "title": "Game Theory for Multi-Agent Systems",
            "link": "https://ieeexplore.ieee.org/document/9876543",
            "snippet": "Published in 2023, this paper examines game-theoretic approaches..."
        },
        {
            "title": "Introduction to Agents",
            "link": "https://example.com/blog/agents",
            "snippet": "A general overview of software agents from 2015..."
        }
    ]
    
    # Parse results
    parsed = wrapper.parse_search_results(mock_results)
    
    print(f"\nParsed {len(parsed)} results:\n")
    for i, result in enumerate(parsed, 1):
        print(f"{i}. {result.title}")
        print(f"   Source: {result.source}")
        print(f"   Year: {result.year}")
        print(f"   URL: {result.url[:60]}...")
        print()
    
    # Score and rank
    ranked = wrapper.filter_and_rank_results(
        parsed,
        research_area="Multi-Agent Systems",
        keywords=["coordination", "game theory"],
        top_n=3
    )
    
    print("\nRanked by Relevance:\n")
    for i, result in enumerate(ranked, 1):
        print(f"{i}. {result.title}")
        print(f"   Relevance Score: {result.relevance_score:.2f}")
        print(f"   Why: Year={result.year}, Source={result.source}")
        print()


def demo_citation_formatting():
    """Demonstrate citation formatting."""
    print("\n" + "=" * 80)
    print("CITATION FORMATTING DEMO")
    print("=" * 80)
    
    # Sample paper
    title = "Multi-Agent Reinforcement Learning: A Survey"
    authors = "Smith, J., & Jones, A."
    year = 2024
    url = "https://arxiv.org/abs/2024.12345"
    source = "arXiv preprint"
    
    print(f"\nOriginal Paper:")
    print(f"  Title: {title}")
    print(f"  Authors: {authors}")
    print(f"  Year: {year}")
    print(f"  URL: {url}")
    print(f"  Source: {source}\n")
    
    print("Formatted Citations:\n")
    
    # APA
    apa = CitationFormatter.format_apa(title, authors, year, url, source)
    print(f"APA:\n  {apa}\n")
    
    # IEEE
    ieee = CitationFormatter.format_ieee(title, authors, year, url, source)
    print(f"IEEE:\n  {ieee}\n")
    
    # Chicago
    chicago = CitationFormatter.format_chicago(title, authors, year, url, source)
    print(f"Chicago:\n  {chicago}\n")
    
    # Harvard
    harvard = CitationFormatter.format_harvard(title, authors, year, url, source)
    print(f"Harvard:\n  {harvard}\n")


def demo_literature_formatting():
    """Demonstrate formatting for preliminary_literature."""
    print("\n" + "=" * 80)
    print("LITERATURE FORMATTING DEMO")
    print("=" * 80)
    
    wrapper = AcademicSearchWrapper()
    
    # Create sample results
    sample_results = [
        SearchResult(
            title="Multi-Agent Coordination: Foundations and Applications",
            url="https://arxiv.org/abs/2024.11111",
            snippet="This comprehensive survey reviews coordination mechanisms in multi-agent systems, covering game-theoretic approaches and distributed algorithms.",
            source="arxiv.org",
            year=2024,
            relevance_score=0.85
        ),
        SearchResult(
            title="Recent Advances in Multi-Agent Reinforcement Learning",
            url="https://ieeexplore.ieee.org/document/9999999",
            snippet="We present recent developments in MARL, focusing on cooperative settings and communication protocols.",
            source="ieee.org",
            year=2023,
            relevance_score=0.78
        )
    ]
    
    # Format for literature
    formatted = wrapper.format_for_literature(sample_results)
    
    print("\nFormatted for preliminary_literature field:\n")
    import json
    print(json.dumps(formatted, indent=2))


if __name__ == "__main__":
    print("🔬 ACADEMIC SEARCH WRAPPER DEMO")
    print("=" * 80)
    
    demo_query_building()
    demo_result_parsing()
    demo_citation_formatting()
    demo_literature_formatting()
    
    print("\n" + "=" * 80)
    print("✅ Demo Complete!")
    print("=" * 80)
