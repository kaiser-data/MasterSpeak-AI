import { Page, expect } from '@playwright/test';
import { testAudioData, selectors } from '../fixtures/test-data';
import * as fs from 'fs';
import * as path from 'path';

export class SpeechHelper {
  constructor(private page: Page) {}

  async navigateToSpeechAnalysis() {
    await this.page.goto('/dashboard');
    
    // Click on speech analysis card or button
    await this.page.click(selectors.dashboard.textAnalysisButton);
    
    // Wait for speech analysis page to load
    await expect(this.page.locator(selectors.speechAnalysis.textInput)).toBeVisible();
  }

  async analyzeText(text: string = testAudioData.speechTexts.basic) {
    await this.navigateToSpeechAnalysis();
    
    // Fill text input
    await this.page.fill(selectors.speechAnalysis.textInput, text);
    
    // Click analyze button
    await this.page.click(selectors.speechAnalysis.analyzeButton);
    
    // Wait for loading spinner to appear and disappear
    await expect(this.page.locator(selectors.speechAnalysis.loadingSpinner)).toBeVisible();
    await expect(this.page.locator(selectors.speechAnalysis.loadingSpinner)).toBeHidden({ timeout: 30000 });
    
    // Wait for results to appear
    await expect(this.page.locator(selectors.speechAnalysis.results)).toBeVisible();
    
    return await this.extractAnalysisResults();
  }

  async uploadAndAnalyzeAudio(audioFilePath?: string) {
    await this.navigateToSpeechAnalysis();
    
    // Create a test audio file if none provided
    if (!audioFilePath) {
      audioFilePath = await this.createTestAudioFile();
    }
    
    // Upload file
    await this.page.setInputFiles(selectors.speechAnalysis.fileUpload, audioFilePath);
    
    // Wait for file to be processed
    await this.page.waitForTimeout(1000);
    
    // Click analyze button
    await this.page.click(selectors.speechAnalysis.analyzeButton);
    
    // Wait for analysis to complete
    await expect(this.page.locator(selectors.speechAnalysis.loadingSpinner)).toBeVisible();
    await expect(this.page.locator(selectors.speechAnalysis.loadingSpinner)).toBeHidden({ timeout: 45000 });
    
    // Wait for results
    await expect(this.page.locator(selectors.speechAnalysis.results)).toBeVisible();
    
    return await this.extractAnalysisResults();
  }

  async recordAndAnalyzeSpeech(durationMs: number = 3000) {
    await this.navigateToSpeechAnalysis();
    
    // Grant microphone permissions (in headless mode this is auto-granted)
    await this.page.context().grantPermissions(['microphone']);
    
    // Start recording
    await this.page.click(selectors.speechAnalysis.recordButton);
    
    // Wait for recording duration
    await this.page.waitForTimeout(durationMs);
    
    // Stop recording
    await this.page.click(selectors.speechAnalysis.stopButton);
    
    // Wait for processing
    await this.page.waitForTimeout(1000);
    
    // Analyze recorded speech
    await this.page.click(selectors.speechAnalysis.analyzeButton);
    
    // Wait for analysis
    await expect(this.page.locator(selectors.speechAnalysis.loadingSpinner)).toBeVisible();
    await expect(this.page.locator(selectors.speechAnalysis.loadingSpinner)).toBeHidden({ timeout: 45000 });
    
    await expect(this.page.locator(selectors.speechAnalysis.results)).toBeVisible();
    
    return await this.extractAnalysisResults();
  }

  async extractAnalysisResults() {
    const results: any = {};
    
    try {
      // Extract scores
      const clarityScore = await this.page.locator(selectors.speechAnalysis.clarityScore).textContent();
      const confidenceScore = await this.page.locator(selectors.speechAnalysis.confidenceScore).textContent();
      
      results.clarityScore = clarityScore;
      results.confidenceScore = confidenceScore;
      
      // Extract suggestions
      const suggestions = await this.page.locator(selectors.speechAnalysis.suggestions).allTextContents();
      results.suggestions = suggestions;
      
      // Get overall results container text for validation
      const resultsContainer = await this.page.locator(selectors.speechAnalysis.results).textContent();
      results.fullResults = resultsContainer;
      
    } catch (error) {
      console.warn('Could not extract all analysis results:', error);
    }
    
    return results;
  }

  async createTestAudioFile(): Promise<string> {
    const audioDir = path.join(process.cwd(), 'tests', 'fixtures', 'audio');
    await fs.promises.mkdir(audioDir, { recursive: true });
    
    const audioFilePath = path.join(audioDir, 'test-audio.wav');
    
    // Create a minimal WAV file (just header + minimal data)
    const wavHeader = Buffer.from([
      // RIFF header
      0x52, 0x49, 0x46, 0x46, // "RIFF"
      0x24, 0x08, 0x00, 0x00, // File size - 8
      0x57, 0x41, 0x56, 0x45, // "WAVE"
      
      // fmt sub-chunk
      0x66, 0x6d, 0x74, 0x20, // "fmt "
      0x10, 0x00, 0x00, 0x00, // Sub-chunk size (16)
      0x01, 0x00,             // Audio format (PCM)
      0x01, 0x00,             // Number of channels (1)
      0x40, 0x1f, 0x00, 0x00, // Sample rate (8000)
      0x80, 0x3e, 0x00, 0x00, // Byte rate
      0x02, 0x00,             // Block align
      0x10, 0x00,             // Bits per sample (16)
      
      // data sub-chunk
      0x64, 0x61, 0x74, 0x61, // "data"
      0x00, 0x08, 0x00, 0x00  // Sub-chunk size
    ]);
    
    // Add some silence data (1 second at 8kHz, 16-bit)
    const silenceData = Buffer.alloc(16000); // 8000 samples * 2 bytes
    
    const wavFile = Buffer.concat([wavHeader, silenceData]);
    await fs.promises.writeFile(audioFilePath, wavFile);
    
    return audioFilePath;
  }

  async validateAnalysisResults(results: any) {
    // Verify results contain expected fields
    expect(results).toBeDefined();
    expect(results.fullResults).toBeDefined();
    expect(results.fullResults.length).toBeGreaterThan(0);
    
    // Check for key analysis components in the results text
    const resultsText = results.fullResults.toLowerCase();
    const expectedTerms = ['score', 'analysis', 'clarity', 'confidence'];
    
    for (const term of expectedTerms) {
      expect(resultsText).toContain(term);
    }
  }
}