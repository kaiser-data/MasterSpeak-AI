/**
 * Speech Data Factory for E2E Tests
 * Generates realistic speech analysis test data for various testing scenarios
 */

import { faker } from '@faker-js/faker';

export interface TestSpeech {
  title: string;
  content: string;
  type: 'text' | 'audio' | 'recording';
  category: 'basic' | 'complex' | 'professional' | 'casual' | 'technical';
  expectedDuration?: number; // in seconds
  expectedWordCount?: number;
  metadata?: {
    language?: string;
    accent?: string;
    speakingRate?: 'slow' | 'normal' | 'fast';
    volume?: 'quiet' | 'normal' | 'loud';
  };
}

export interface SpeechAnalysisResult {
  clarity_score: number;
  structure_score: number;
  confidence_score: number;
  pace_analysis: string;
  volume_analysis: string;
  filler_word_count: number;
  suggestions: string[];
  overall_score: number;
  word_count: number;
  duration_seconds?: number;
}

export class SpeechFactory {
  
  /**
   * Generate basic speech content for simple testing scenarios
   */
  static createBasic(): TestSpeech {
    return {
      title: 'Basic Test Speech',
      content: 'Hello, this is a test speech for analysis. I am speaking clearly and slowly. This content is designed to be simple and easy to analyze.',
      type: 'text',
      category: 'basic',
      expectedWordCount: 24,
      expectedDuration: 12,
      metadata: {
        language: 'en-US',
        speakingRate: 'normal',
        volume: 'normal'
      }
    };
  }
  
  /**
   * Generate complex speech content with advanced vocabulary and structure
   */
  static createComplex(): TestSpeech {
    return {
      title: 'Complex Analysis Speech',
      content: 'The quick brown fox jumps over the lazy dog. This sentence contains every letter of the alphabet and is commonly used for testing purposes. Furthermore, we can examine the intricate relationships between linguistic patterns, phonetic variations, and semantic comprehension in modern speech analysis systems.',
      type: 'text',
      category: 'complex',
      expectedWordCount: 45,
      expectedDuration: 25,
      metadata: {
        language: 'en-US',
        speakingRate: 'normal',
        volume: 'normal'
      }
    };
  }
  
  /**
   * Generate professional presentation-style speech
   */
  static createProfessional(): TestSpeech {
    return {
      title: 'Professional Presentation',
      content: 'Good morning everyone. Today I would like to present our quarterly results and discuss our strategic initiatives for the upcoming fiscal year. Our analysis shows significant growth in market penetration, with a 15% increase in customer acquisition. Moving forward, we will focus on operational excellence, customer satisfaction, and sustainable growth strategies.',
      type: 'text',
      category: 'professional',
      expectedWordCount: 55,
      expectedDuration: 30,
      metadata: {
        language: 'en-US',
        speakingRate: 'normal',
        volume: 'normal'
      }
    };
  }
  
  /**
   * Generate casual conversation-style speech
   */
  static createCasual(): TestSpeech {
    const casualPhrases = [
      "Hey there, um, so I was thinking about, you know, maybe we could grab coffee sometime?",
      "Like, actually, the weather's been pretty crazy lately, right? I mean, it's been all over the place.",
      "So anyway, I was telling my friend about this thing, and she was like, no way, that's totally awesome!"
    ];
    
    return {
      title: 'Casual Conversation',
      content: faker.helpers.arrayElement(casualPhrases),
      type: 'text',
      category: 'casual',
      expectedWordCount: 18,
      expectedDuration: 10,
      metadata: {
        language: 'en-US',
        speakingRate: 'fast',
        volume: 'normal'
      }
    };
  }
  
  /**
   * Generate technical speech with specialized vocabulary
   */
  static createTechnical(): TestSpeech {
    return {
      title: 'Technical Documentation',
      content: 'The application implements a microservices architecture utilizing containerized deployments with Kubernetes orchestration. Our API endpoints leverage RESTful principles with GraphQL integration for optimized data fetching. The database layer employs PostgreSQL with Redis caching for enhanced performance metrics.',
      type: 'text',
      category: 'technical',
      expectedWordCount: 40,
      expectedDuration: 22,
      metadata: {
        language: 'en-US',
        speakingRate: 'normal',
        volume: 'normal'
      }
    };
  }
  
  /**
   * Generate speech with specific characteristics for testing edge cases
   */
  static createWithCharacteristics(characteristics: {
    length?: 'short' | 'medium' | 'long';
    complexity?: 'simple' | 'moderate' | 'complex';
    fillerWords?: 'none' | 'few' | 'many';
    clarity?: 'high' | 'medium' | 'low';
  }): TestSpeech {
    const { length = 'medium', complexity = 'moderate', fillerWords = 'few', clarity = 'high' } = characteristics;
    
    let content = '';
    let title = `${complexity} ${length} speech`;
    
    // Base content by complexity
    const simpleWords = ['hello', 'test', 'speech', 'analysis', 'good', 'clear', 'simple'];
    const moderateWords = ['presentation', 'examination', 'discussion', 'evaluation', 'consideration'];
    const complexWords = ['sophisticated', 'comprehensive', 'intricate', 'multifaceted', 'paradigmatic'];
    
    let wordPool = simpleWords;
    if (complexity === 'moderate') wordPool = [...simpleWords, ...moderateWords];
    if (complexity === 'complex') wordPool = [...simpleWords, ...moderateWords, ...complexWords];
    
    // Generate content based on length
    let targetWords = 15; // short
    if (length === 'medium') targetWords = 35;
    if (length === 'long') targetWords = 80;
    
    // Build content
    const sentences = [];
    let currentWords = 0;
    
    while (currentWords < targetWords) {
      let sentence = faker.helpers.arrayElements(wordPool, Math.min(8, targetWords - currentWords)).join(' ');
      
      // Add filler words based on setting
      if (fillerWords === 'few') {
        sentence = sentence.replace(/\b(\w+)\b/g, (match, word, index) => {
          return Math.random() < 0.1 ? `um, ${word}` : word;
        });
      } else if (fillerWords === 'many') {
        sentence = sentence.replace(/\b(\w+)\b/g, (match, word, index) => {
          return Math.random() < 0.3 ? `uh, ${word}, you know,` : word;
        });
      }
      
      sentences.push(sentence.charAt(0).toUpperCase() + sentence.slice(1) + '.');
      currentWords += sentence.split(' ').length;
    }
    
    content = sentences.join(' ');
    
    return {
      title,
      content,
      type: 'text',
      category: complexity as any,
      expectedWordCount: content.split(' ').length,
      expectedDuration: Math.ceil(content.split(' ').length * 0.5), // Rough estimate
      metadata: {
        language: 'en-US',
        speakingRate: clarity === 'high' ? 'normal' : clarity === 'medium' ? 'fast' : 'slow',
        volume: 'normal'
      }
    };
  }
  
  /**
   * Generate mock analysis results for testing
   */
  static createMockAnalysis(speech: TestSpeech): SpeechAnalysisResult {
    const wordCount = speech.expectedWordCount || speech.content.split(' ').length;
    const fillerCount = (speech.content.match(/\b(um|uh|like|you know|actually)\b/gi) || []).length;
    
    // Generate realistic scores based on content characteristics
    let clarityScore = faker.number.int({ min: 7, max: 10 });
    let structureScore = faker.number.int({ min: 6, max: 9 });
    let confidenceScore = faker.number.int({ min: 5, max: 9 });
    
    // Adjust scores based on speech category
    if (speech.category === 'professional') {
      clarityScore = Math.max(clarityScore, 8);
      structureScore = Math.max(structureScore, 8);
    } else if (speech.category === 'casual') {
      clarityScore = Math.max(4, clarityScore - 2);
      structureScore = Math.max(4, structureScore - 3);
    }
    
    const overallScore = Math.round((clarityScore + structureScore + confidenceScore) / 3);
    
    const suggestions = [];
    if (clarityScore < 7) suggestions.push('Practice speaking more clearly and at a steady pace');
    if (structureScore < 7) suggestions.push('Organize your thoughts with clear introduction, body, and conclusion');
    if (fillerCount > 3) suggestions.push('Reduce the use of filler words like "um" and "uh"');
    if (wordCount < 20) suggestions.push('Provide more detailed explanations and examples');
    
    return {
      clarity_score: clarityScore,
      structure_score: structureScore,
      confidence_score: confidenceScore,
      pace_analysis: confidenceScore > 7 ? 'Good speaking pace with natural rhythm' : 'Consider slowing down for better clarity',
      volume_analysis: 'Appropriate volume level for the content',
      filler_word_count: fillerCount,
      suggestions,
      overall_score: overallScore,
      word_count: wordCount,
      duration_seconds: speech.expectedDuration
    };
  }
  
  /**
   * Generate audio file metadata for testing file uploads
   */
  static createAudioFileData(type: 'wav' | 'mp3' | 'mp4' = 'wav') {
    return {
      fileName: `test-speech-${Date.now()}.${type}`,
      fileSize: faker.number.int({ min: 1024, max: 10485760 }), // 1KB to 10MB
      duration: faker.number.int({ min: 10, max: 300 }), // 10 seconds to 5 minutes
      sampleRate: type === 'wav' ? 44100 : 22050,
      bitRate: type === 'mp3' ? 128 : null,
      channels: faker.helpers.arrayElement([1, 2]), // Mono or stereo
      mimeType: `audio/${type}`
    };
  }
}

/**
 * Predefined speech samples for consistent testing
 */
export const PredefinedSpeeches = {
  basic: SpeechFactory.createBasic(),
  complex: SpeechFactory.createComplex(),
  professional: SpeechFactory.createProfessional(),
  casual: SpeechFactory.createCasual(),
  technical: SpeechFactory.createTechnical(),
  
  // Edge cases
  shortSimple: SpeechFactory.createWithCharacteristics({ length: 'short', complexity: 'simple' }),
  longComplex: SpeechFactory.createWithCharacteristics({ length: 'long', complexity: 'complex' }),
  fillerHeavy: SpeechFactory.createWithCharacteristics({ fillerWords: 'many', clarity: 'low' })
} as const;

/**
 * Speech data sets for different testing scenarios
 */
export const SpeechDataSets = {
  analysisVariety: [
    PredefinedSpeeches.basic,
    PredefinedSpeeches.complex,
    PredefinedSpeeches.professional,
    PredefinedSpeeches.technical
  ],
  
  edgeCases: [
    PredefinedSpeeches.shortSimple,
    PredefinedSpeeches.longComplex,
    PredefinedSpeeches.fillerHeavy
  ],
  
  performanceTesting: Array.from({ length: 10 }, () => 
    SpeechFactory.createWithCharacteristics({ 
      length: 'long', 
      complexity: 'complex' 
    })
  )
} as const;