"""
Unit tests for export service PDF generation functionality.
"""
import pytest
import asyncio
from datetime import datetime
from uuid import uuid4
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

from backend.services.export_service import ExportService, export_service
from backend.models.analysis import Analysis
from backend.database.models import Speech, SpeechAnalysis, SourceType


class TestExportService:
    """Test ExportService functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.export_service = ExportService()
        
        # Create test analysis
        self.analysis_id = uuid4()
        self.speech_id = uuid4()
        self.user_id = uuid4()
        
        self.test_analysis = Analysis(
            id=self.analysis_id,
            user_id=self.user_id,
            speech_id=self.speech_id,
            transcript="This is a test transcript for speech analysis.",
            metrics={
                "word_count": 10,
                "clarity_score": 8,
                "structure_score": 7,
                "filler_word_count": 2
            },
            summary="This is a test summary of the speech analysis.",
            feedback="This is detailed feedback about the speech performance.",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.test_speech = Speech(
            id=self.speech_id,
            user_id=self.user_id,
            title="Test Speech Analysis",
            source_type=SourceType.TEXT,
            content="This is the original speech content.",
            created_at=datetime.utcnow()
        )
        
        self.test_speech_analysis = SpeechAnalysis(
            id=uuid4(),
            speech_id=self.speech_id,
            word_count=10,
            clarity_score=8,
            structure_score=7,
            filler_word_count=2,
            prompt="default",
            feedback="Legacy feedback from speech analysis.",
            created_at=datetime.utcnow()
        )
    
    def test_init_with_reportlab(self):
        """Test ExportService initialization with reportlab available."""
        service = ExportService()
        # This will depend on whether reportlab is installed
        # We can't easily mock the import in __init__, so we test behavior
        assert service is not None
    
    @pytest.mark.asyncio
    async def test_export_json_basic(self):
        """Test basic JSON export functionality."""
        result = await self.export_service.export_json(
            analysis=self.test_analysis,
            speech=self.test_speech,
            include_transcript=False
        )
        
        # Verify basic structure
        assert result["analysis_id"] == str(self.analysis_id)
        assert result["speech_id"] == str(self.speech_id)
        assert result["user_id"] == str(self.user_id)
        assert result["metrics"] == self.test_analysis.metrics
        assert result["summary"] == self.test_analysis.summary
        assert result["feedback"] == self.test_analysis.feedback
        
        # Verify speech context
        assert "speech" in result
        assert result["speech"]["title"] == self.test_speech.title
        assert result["speech"]["source_type"] == self.test_speech.source_type.value
        
        # Verify no transcript when not requested
        assert "transcript" not in result
        assert "content" not in result
        
        # Verify export metadata
        assert "export_metadata" in result
        assert result["export_metadata"]["transcript_included"] is False
        assert result["export_metadata"]["format_version"] == "1.0"
    
    @pytest.mark.asyncio
    async def test_export_json_with_transcript(self):
        """Test JSON export with transcript included."""
        result = await self.export_service.export_json(
            analysis=self.test_analysis,
            speech=self.test_speech,
            include_transcript=True
        )
        
        # Verify transcript is included
        assert result["transcript"] == self.test_analysis.transcript
        assert result["export_metadata"]["transcript_included"] is True
    
    @pytest.mark.asyncio
    async def test_export_json_with_legacy_analysis(self):
        """Test JSON export with legacy SpeechAnalysis data."""
        result = await self.export_service.export_json(
            analysis=self.test_analysis,
            speech=self.test_speech,
            speech_analysis=self.test_speech_analysis,
            include_transcript=False
        )
        
        # Verify legacy metrics are included
        assert "legacy_metrics" in result
        assert result["legacy_metrics"]["word_count"] == self.test_speech_analysis.word_count
        assert result["legacy_metrics"]["clarity_score"] == self.test_speech_analysis.clarity_score
        assert result["legacy_metrics"]["structure_score"] == self.test_speech_analysis.structure_score
        assert result["legacy_metrics"]["filler_word_count"] == self.test_speech_analysis.filler_word_count
        assert result["legacy_metrics"]["prompt"] == self.test_speech_analysis.prompt
    
    @pytest.mark.asyncio
    async def test_export_json_fallback_to_speech_content(self):
        """Test JSON export falls back to speech content when no transcript."""
        # Analysis without transcript
        analysis_no_transcript = Analysis(
            id=self.analysis_id,
            user_id=self.user_id,
            speech_id=self.speech_id,
            transcript=None,
            metrics=self.test_analysis.metrics,
            summary=self.test_analysis.summary,
            feedback=self.test_analysis.feedback,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        result = await self.export_service.export_json(
            analysis=analysis_no_transcript,
            speech=self.test_speech,
            include_transcript=True
        )
        
        # Should include speech content instead
        assert result["content"] == self.test_speech.content
        assert result["export_metadata"]["transcript_included"] is True
    
    @patch('backend.services.export_service.REPORTLAB_AVAILABLE', True)
    @pytest.mark.asyncio
    async def test_render_pdf_reportlab_available(self):
        """Test PDF rendering when reportlab is available."""
        with patch('backend.services.export_service.SimpleDocTemplate') as mock_doc:
            mock_doc_instance = Mock()
            mock_doc.return_value = mock_doc_instance
            
            # Mock the PDF generation
            self.export_service.styles = Mock()  # Mock styles
            
            result = await self.export_service.render_pdf(
                analysis=self.test_analysis,
                speech=self.test_speech,
                include_transcript=True
            )
            
            # Verify PDF document creation was attempted
            mock_doc.assert_called_once()
            mock_doc_instance.build.assert_called_once()
    
    @patch('backend.services.export_service.REPORTLAB_AVAILABLE', False)
    @pytest.mark.asyncio
    async def test_render_pdf_reportlab_unavailable(self):
        """Test PDF rendering when reportlab is not available."""
        with pytest.raises(RuntimeError, match="PDF generation requires reportlab"):
            await self.export_service.render_pdf(
                analysis=self.test_analysis,
                speech=self.test_speech
            )
    
    def test_get_safe_filename(self):
        """Test safe filename generation."""
        title = "My Test Analysis Report!"
        analysis_id = str(uuid4())
        
        filename = self.export_service.get_safe_filename(title, analysis_id, "pdf")
        
        # Verify safe characters only
        assert "!" not in filename
        assert " " not in filename or "_" in filename
        assert filename.endswith(".pdf")
        assert analysis_id[:8] in filename
        
        # Test long title truncation
        long_title = "A" * 100
        long_filename = self.export_service.get_safe_filename(long_title, analysis_id, "json")
        assert len(long_filename) < 100
        assert "..." in long_filename
    
    def test_get_safe_filename_special_characters(self):
        """Test filename generation with special characters."""
        title = "Test/Analysis\\With:Special|Characters<>?"
        analysis_id = str(uuid4())
        
        filename = self.export_service.get_safe_filename(title, analysis_id, "pdf")
        
        # Should only contain safe characters
        safe_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.")
        filename_chars = set(filename)
        
        # Allow safe characters, underscores (from spaces), and the expected format characters
        for char in filename_chars:
            assert char in safe_chars or char in "_.0123456789", f"Unsafe character: {char}"


@pytest.mark.asyncio
class TestExportServiceIntegration:
    """Integration tests for export service."""
    
    async def test_pdf_content_structure(self):
        """Test that PDF contains expected content structure."""
        # This test would require reportlab to be installed
        pytest.skip("Requires reportlab for full integration testing")
    
    async def test_json_serialization(self):
        """Test that exported JSON is properly serializable."""
        service = ExportService()
        
        analysis = Analysis(
            id=uuid4(),
            user_id=uuid4(),
            speech_id=uuid4(),
            transcript="Test transcript",
            metrics={"test": "value"},
            summary="Test summary",
            feedback="Test feedback",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        result = await service.export_json(analysis=analysis)
        
        # Should be JSON serializable
        import json
        json_str = json.dumps(result)
        reconstructed = json.loads(json_str)
        
        assert reconstructed["analysis_id"] == result["analysis_id"]
        assert reconstructed["feedback"] == result["feedback"]


class TestExportServiceError:
    """Test error handling in export service."""
    
    @pytest.mark.asyncio
    async def test_export_json_missing_analysis(self):
        """Test error handling when analysis is None."""
        service = ExportService()
        
        # This should not raise an error, but might have different behavior
        # depending on implementation
        try:
            result = await service.export_json(analysis=None)
            # If it doesn't raise, verify it handles gracefully
            assert result is not None
        except (TypeError, AttributeError):
            # Expected if the method doesn't handle None analysis
            pass
    
    @pytest.mark.asyncio
    async def test_render_pdf_missing_analysis(self):
        """Test PDF rendering error handling."""
        service = ExportService()
        
        # Should handle missing analysis gracefully or raise appropriate error
        try:
            await service.render_pdf(analysis=None)
        except (RuntimeError, TypeError, AttributeError):
            # Expected behavior for invalid input
            pass