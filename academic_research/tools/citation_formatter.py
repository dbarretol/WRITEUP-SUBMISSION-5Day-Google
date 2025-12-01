"""Citation formatter for academic references."""

from typing import Dict, Optional
from datetime import datetime


class CitationFormatter:
    """Format search results as academic citations in various styles."""
    
    @staticmethod
    def format_apa(
        title: str,
        authors: Optional[str] = None,
        year: Optional[int] = None,
        url: Optional[str] = None,
        source: Optional[str] = None
    ) -> str:
        """
        Format citation in APA style.
        
        Args:
            title: Paper title
            authors: Author names (optional)
            year: Publication year (optional)
            url: URL or DOI (optional)
            source: Source/publisher (optional)
        
        Returns:
            APA-formatted citation string
        """
        parts = []
        
        # Authors
        if authors:
            parts.append(f"{authors}.")
        else:
            parts.append("Author unknown.")
        
        # Year
        if year:
            parts.append(f"({year}).")
        else:
            parts.append(f"(n.d.).")
        
        # Title (italicized conceptually)
        parts.append(f"{title}.")
        
        # Source
        if source:
            parts.append(f"{source}.")
        
        # URL/DOI
        if url:
            if "doi.org" in url:
                parts.append(f"https://doi.org/{url.split('doi.org/')[-1]}")
            else:
                parts.append(f"Retrieved from {url}")
        
        return " ".join(parts)
    
    @staticmethod
    def format_ieee(
        title: str,
        authors: Optional[str] = None,
        year: Optional[int] = None,
        url: Optional[str] = None,
        source: Optional[str] = None
    ) -> str:
        """
        Format citation in IEEE style.
        
        Args:
            title: Paper title
            authors: Author names (optional)
            year: Publication year (optional)
            url: URL or DOI (optional)
            source: Source/publisher (optional)
        
        Returns:
            IEEE-formatted citation string
        """
        parts = []
        
        # Authors (abbreviated)
        if authors:
            # Simplified: just use as-is (proper IEEE would abbreviate first names)
            parts.append(f'{authors},')
        
        # Title in quotes
        parts.append(f'"{title},"')
        
        # Source in italics (conceptually)
        if source:
            parts.append(f"{source},")
        
        # Year
        if year:
            parts.append(f"{year}.")
        
        # URL/DOI
        if url:
            parts.append(f"[Online]. Available: {url}")
        
        return " ".join(parts)
    
    @staticmethod
    def format_chicago(
        title: str,
        authors: Optional[str] = None,
        year: Optional[int] = None,
        url: Optional[str] = None,
        source: Optional[str] = None
    ) -> str:
        """
        Format citation in Chicago style (author-date).
        
        Args:
            title: Paper title
            authors: Author names (optional)
            year: Publication year (optional)
            url: URL or DOI (optional)
            source: Source/publisher (optional)
        
        Returns:
            Chicago-formatted citation string
        """
        parts = []
        
        # Authors (Last, First)
        if authors:
            parts.append(f"{authors}.")
        
        # Year
        if year:
            parts.append(f"{year}.")
        
        # Title in quotes
        parts.append(f'"{title}."')
        
        # Source
        if source:
            parts.append(f"{source}.")
        
        # URL
        if url:
            parts.append(url + ".")
        
        return " ".join(parts)
    
    @staticmethod
    def format_harvard(
        title: str,
        authors: Optional[str] = None,
        year: Optional[int] = None,
        url: Optional[str] = None,
        source: Optional[str] = None
    ) -> str:
        """
        Format citation in Harvard style.
        
        Args:
            title: Paper title
            authors: Author names (optional)
            year: Publication year (optional)
            url: URL or DOI (optional)
            source: Source/publisher (optional)
        
        Returns:
            Harvard-formatted citation string
        """
        parts = []
        
        # Authors
        if authors:
            parts.append(f"{authors}")
        else:
            parts.append("Author unknown")
        
        # Year in parentheses
        if year:
            parts.append(f"({year})")
        else:
            parts.append("(n.d.)")
        
        # Title in italics (conceptually)
        parts.append(f"{title}.")
        
        # Source
        if source:
            parts.append(f"{source}.")
        
        # Available from
        if url:
            parts.append(f"Available at: {url}")
            access_date = datetime.now().strftime("%d %B %Y")
            parts.append(f"(Accessed: {access_date}).")
        
        return " ".join(parts)
    
    @staticmethod
    def format_citation(
        title: str,
        style: str = "APA",
        authors: Optional[str] = None,
        year: Optional[int] = None,
        url: Optional[str] = None,
        source: Optional[str] = None
    ) -> str:
        """
        Format citation in specified style.
        
        Args:
            title: Paper title
            style: Citation style (APA, IEEE, Chicago, Harvard)
            authors: Author names (optional)
            year: Publication year (optional)
            url: URL or DOI (optional)
            source: Source/publisher (optional)
        
        Returns:
            Formatted citation string
        """
        style_upper = style.upper()
        
        formatters = {
            "APA": CitationFormatter.format_apa,
            "IEEE": CitationFormatter.format_ieee,
            "CHICAGO": CitationFormatter.format_chicago,
            "HARVARD": CitationFormatter.format_harvard,
        }
        
        formatter = formatters.get(style_upper, CitationFormatter.format_apa)
        
        return formatter(
            title=title,
            authors=authors,
            year=year,
            url=url,
            source=source
        )
