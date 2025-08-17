"""
Export models for MasterSpeak-AI.
Provides PDF export and sharing functionality for analyses.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from enum import Enum


class ExportFormat(str, Enum):
    """Supported export formats."""
    PDF = "pdf"
    JSON = "json"
    CSV = "csv"


class ExportRequest(BaseModel):
    """Request model for analysis export."""
    analysis_ids: List[UUID] = Field(..., description="List of analysis IDs to export")
    format: ExportFormat = Field(default=ExportFormat.PDF, description="Export format")
    include_transcript: bool = Field(default=False, description="Include transcript in export")
    include_metrics: bool = Field(default=True, description="Include metrics in export")
    include_summary: bool = Field(default=True, description="Include summary in export")
    include_feedback: bool = Field(default=True, description="Include feedback in export")
    custom_title: Optional[str] = Field(None, description="Custom title for export")


class ExportResponse(BaseModel):
    """Response model for export operations."""
    export_id: UUID = Field(..., description="Unique export identifier")
    download_url: str = Field(..., description="URL to download the export")
    filename: str = Field(..., description="Generated filename")
    file_size: int = Field(..., description="File size in bytes")
    format: ExportFormat = Field(..., description="Export format")
    created_at: datetime = Field(..., description="Export creation timestamp")
    expires_at: datetime = Field(..., description="Download URL expiration")


class ShareTokenRequest(BaseModel):
    """Request model for creating share tokens."""
    analysis_id: UUID = Field(..., description="Analysis ID to share")
    expires_in_hours: int = Field(default=24, ge=1, le=168, description="Token expiration in hours (max 168)")
    allow_download: bool = Field(default=False, description="Allow PDF download via share link")


class ShareTokenResponse(BaseModel):
    """Response model for share token creation."""
    token: str = Field(..., description="Share token for public access")
    share_url: str = Field(..., description="Public share URL")
    analysis_id: UUID = Field(..., description="Shared analysis ID")
    expires_at: datetime = Field(..., description="Token expiration timestamp")
    allow_download: bool = Field(..., description="Download permission")
    created_at: datetime = Field(..., description="Token creation timestamp")


class PublicAnalysisView(BaseModel):
    """Public view of analysis for sharing (no PII)."""
    analysis_id: UUID = Field(..., description="Analysis identifier")
    speech_title: str = Field(..., description="Speech title")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Analysis metrics")
    summary: Optional[str] = Field(None, description="Analysis summary")
    feedback: str = Field(..., description="Analysis feedback")
    created_at: datetime = Field(..., description="Analysis creation date")
    # Note: No transcript field - PII protection


class ExportMetadata(BaseModel):
    """Metadata for export tracking."""
    export_id: UUID
    user_id: UUID
    analysis_count: int
    format: ExportFormat
    file_size: int
    created_at: datetime
    downloaded_at: Optional[datetime] = None
    download_count: int = 0


class PDFExportOptions(BaseModel):
    """Options for PDF export generation."""
    include_cover_page: bool = Field(default=True, description="Include cover page")
    include_table_of_contents: bool = Field(default=True, description="Include table of contents")
    include_charts: bool = Field(default=True, description="Include metric visualizations")
    font_size: int = Field(default=11, ge=8, le=16, description="Base font size")
    page_margins: Dict[str, float] = Field(
        default={"top": 1.0, "bottom": 1.0, "left": 1.0, "right": 1.0},
        description="Page margins in inches"
    )
    branding: bool = Field(default=True, description="Include MasterSpeak AI branding")


class CSVExportRow(BaseModel):
    """Row model for CSV export."""
    analysis_id: str
    speech_title: str
    created_at: str
    word_count: Optional[int]
    clarity_score: Optional[float]
    structure_score: Optional[float]
    filler_word_count: Optional[int]
    overall_score: Optional[float]
    summary: Optional[str]
    feedback: str


class ExportStatistics(BaseModel):
    """Statistics for export usage."""
    total_exports: int
    pdf_exports: int
    csv_exports: int
    json_exports: int
    total_downloads: int
    average_file_size: float
    most_popular_format: ExportFormat