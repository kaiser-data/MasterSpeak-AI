"""
Export service for MasterSpeak-AI.
Provides PDF generation and data export functionality for analysis results.
"""

from io import BytesIO
from datetime import datetime
from typing import Optional, Dict, Any
import json
import logging

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import black, blue, gray
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.platypus.flowables import HRFlowable
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

logger = logging.getLogger(__name__)


class ExportService:
    """
    Service for exporting analysis data in various formats.
    
    Features:
    - PDF report generation with professional styling
    - JSON data export with structured format
    - Configurable content inclusion (transcript, metrics, etc.)
    - Error handling and graceful degradation
    """
    
    def __init__(self):
        self.styles = None
        if REPORTLAB_AVAILABLE:
            self._setup_pdf_styles()
    
    def _setup_pdf_styles(self):
        """Initialize PDF styling for consistent document formatting."""
        if not REPORTLAB_AVAILABLE:
            return
        
        self.styles = getSampleStyleSheet()
        
        # Custom styles for better presentation
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=blue,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=12,
            textColor=black
        ))
        
        self.styles.add(ParagraphStyle(
            name='MetricLabel',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=gray,
            spaceBefore=6
        ))
        
        self.styles.add(ParagraphStyle(
            name='MetricValue',
            parent=self.styles['Normal'],
            fontSize=18,
            textColor=black,
            spaceBefore=3,
            spaceAfter=12
        ))
    
    async def render_pdf(self, analysis: Dict[str, Any], include_transcript: bool = True) -> bytes:
        """
        Generate a PDF report for an analysis.
        
        Args:
            analysis: Analysis data dictionary
            include_transcript: Whether to include transcript in the PDF
            
        Returns:
            bytes: PDF document as byte stream
            
        Raises:
            RuntimeError: If PDF generation dependencies are not available
        """
        if not REPORTLAB_AVAILABLE:
            raise RuntimeError("PDF generation requires reportlab. Install with: pip install reportlab")
        
        # Create PDF buffer
        buffer = BytesIO()
        
        # Create document with professional layout
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build document content
        story = []
        
        # Title
        story.append(Paragraph("Speech Analysis Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Analysis metadata
        created_date = datetime.fromisoformat(analysis['created_at'].replace('Z', '+00:00')).strftime("%B %d, %Y at %I:%M %p")
        story.append(Paragraph(f"<b>Generated:</b> {created_date}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Analysis ID:</b> {analysis['analysis_id']}", self.styles['Normal']))
        
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=gray))
        story.append(Spacer(1, 20))
        
        # Metrics Section
        story.append(Paragraph("Analysis Metrics", self.styles['SectionHeader']))
        
        # Create metrics table
        metrics_data = []
        if analysis.get('metrics'):
            metrics = analysis['metrics']
            metrics_data = [
                ["Word Count", str(metrics.get('word_count', 'N/A'))],
                ["Clarity Score", f"{metrics.get('clarity_score', 'N/A')}/10"],
                ["Structure Score", f"{metrics.get('structure_score', 'N/A')}/10"],
                ["Filler Words", str(metrics.get('filler_word_count', 'N/A'))]
            ]
        
        if metrics_data:
            metrics_table = Table(metrics_data, colWidths=[2*inch, 2*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), gray),
                ('TEXTCOLOR', (0, 0), (-1, 0), black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), '#f8f9fa'),
                ('GRID', (0, 0), (-1, -1), 1, black)
            ]))
            story.append(metrics_table)
        
        story.append(Spacer(1, 20))
        
        # Summary Section
        if analysis.get('summary'):
            story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
            story.append(Paragraph(analysis['summary'], self.styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Feedback Section
        story.append(Paragraph("Detailed Feedback", self.styles['SectionHeader']))
        story.append(Paragraph(analysis['feedback'], self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Transcript Section (if requested and available)
        if include_transcript and analysis.get('transcript'):
            story.append(Paragraph("Transcript", self.styles['SectionHeader']))
            story.append(Paragraph(analysis['transcript'], self.styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Footer
        story.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=gray))
        story.append(Spacer(1, 10))
        story.append(Paragraph(
            "Generated by MasterSpeak-AI | Confidential Analysis Report", 
            self.styles['Normal']
        ))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        logger.info(f"PDF generated successfully for analysis {analysis['analysis_id']} ({len(pdf_bytes)} bytes)")
        return pdf_bytes
    
    def get_safe_filename(self, title: str, analysis_id: str, extension: str) -> str:
        """
        Generate a safe filename for exports.
        
        Args:
            title: Base title for the file
            analysis_id: Analysis ID for uniqueness
            extension: File extension (e.g., 'pdf', 'json')
            
        Returns:
            str: Safe filename
        """
        # Sanitize title
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')
        
        # Truncate if too long
        if len(safe_title) > 50:
            safe_title = safe_title[:47] + "..."
        
        # Add timestamp and ID for uniqueness
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        short_id = str(analysis_id)[:8]
        
        return f"{safe_title}_{timestamp}_{short_id}.{extension}"


# Global service instance
export_service = ExportService()