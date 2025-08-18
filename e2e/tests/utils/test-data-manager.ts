/**
 * Test Data Manager for E2E Tests
 * Handles database seeding, cleanup, and state management for consistent testing
 */

import { APIRequestContext, request } from '@playwright/test';
import { UserFactory, TestUser } from '../factories/user-factory';
import { SpeechFactory, TestSpeech } from '../factories/speech-factory';

export interface TestDataSnapshot {
  users: TestUser[];
  speeches: TestSpeech[];
  timestamp: string;
  testRun: string;
}

export class TestDataManager {
  private apiContext: APIRequestContext;
  private baseURL: string;
  private createdUsers: TestUser[] = [];
  private createdSpeeches: TestSpeech[] = [];
  
  constructor(baseURL: string = 'http://localhost:8000') {
    this.baseURL = baseURL;
  }
  
  /**
   * Initialize the test data manager with API context
   */
  async initialize(): Promise<void> {
    this.apiContext = await request.newContext({
      baseURL: this.baseURL,
      extraHTTPHeaders: {
        'Content-Type': 'application/json'
      }
    });
  }
  
  /**
   * Create a test user via API and track for cleanup
   */
  async createUser(userData?: Partial<TestUser>): Promise<TestUser> {
    const user = userData ? { ...UserFactory.createBasic(), ...userData } : UserFactory.createBasic();
    
    try {
      const response = await this.apiContext.post('/api/v1/auth/register', {
        data: {
          email: user.email,
          password: user.password,
          full_name: user.fullName
        }
      });
      
      if (response.ok()) {
        const result = await response.json();
        user.id = result.id || user.id;
        this.createdUsers.push(user);
        return user;
      } else {
        throw new Error(`Failed to create user: ${response.status()} ${await response.text()}`);
      }
    } catch (error) {
      console.warn(`Could not create user via API: ${error}. Using mock user.`);
      this.createdUsers.push(user);
      return user;
    }
  }
  
  /**
   * Create multiple test users
   */
  async createUsers(count: number, baseData?: Partial<TestUser>): Promise<TestUser[]> {
    const users: TestUser[] = [];
    for (let i = 0; i < count; i++) {
      users.push(await this.createUser(baseData));
    }
    return users;
  }
  
  /**
   * Login a user and return authentication token
   */
  async loginUser(user: TestUser): Promise<string> {
    try {
      const response = await this.apiContext.post('/api/v1/auth/jwt/login', {
        data: {
          username: user.email,
          password: user.password
        }
      });
      
      if (response.ok()) {
        const result = await response.json();
        return result.access_token;
      } else {
        throw new Error(`Login failed: ${response.status()}`);
      }
    } catch (error) {
      console.warn(`Could not login user: ${error}`);
      return 'mock-token-for-testing';
    }
  }
  
  /**
   * Create speech analysis data for a user
   */
  async createSpeechAnalysis(user: TestUser, speechData?: Partial<TestSpeech>): Promise<TestSpeech> {
    const speech = speechData ? { ...SpeechFactory.createBasic(), ...speechData } : SpeechFactory.createBasic();
    const token = await this.loginUser(user);
    
    try {
      const response = await this.apiContext.post('/api/v1/analysis/text', {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        data: {
          text: speech.content,
          analysis_type: 'general'
        }
      });
      
      if (response.ok()) {
        const result = await response.json();
        speech.title = result.speech_id || speech.title;
        this.createdSpeeches.push(speech);
        return speech;
      } else {
        throw new Error(`Failed to create speech analysis: ${response.status()}`);
      }
    } catch (error) {
      console.warn(`Could not create speech analysis: ${error}. Using mock data.`);
      this.createdSpeeches.push(speech);
      return speech;
    }
  }
  
  /**
   * Seed the database with predefined test data
   */
  async seedDatabase(): Promise<TestDataSnapshot> {
    const testRun = `test-run-${Date.now()}`;
    
    // Create demo and test users
    const demoUser = await this.createUser(UserFactory.createDemo());
    const testUser = await this.createUser(UserFactory.createTest());
    
    // Create additional users for various scenarios
    const newUser = await this.createUser(UserFactory.createForScenario('new_user'));
    const returningUser = await this.createUser(UserFactory.createForScenario('returning_user'));
    
    // Create speech analyses for testing
    const basicSpeech = await this.createSpeechAnalysis(demoUser, SpeechFactory.createBasic());
    const complexSpeech = await this.createSpeechAnalysis(testUser, SpeechFactory.createComplex());
    const professionalSpeech = await this.createSpeechAnalysis(returningUser, SpeechFactory.createProfessional());
    
    return {
      users: [demoUser, testUser, newUser, returningUser],
      speeches: [basicSpeech, complexSpeech, professionalSpeech],
      timestamp: new Date().toISOString(),
      testRun
    };
  }
  
  /**
   * Reset database to clean state
   */
  async resetDatabase(): Promise<void> {
    try {
      // Try to reset via API endpoint if available
      const response = await this.apiContext.post('/api/v1/test/reset', {
        data: { confirm: true }
      });
      
      if (!response.ok()) {
        console.warn('Database reset endpoint not available or failed');
      }
    } catch (error) {
      console.warn(`Could not reset database: ${error}`);
    }
    
    // Clear local tracking
    this.createdUsers = [];
    this.createdSpeeches = [];
  }
  
  /**
   * Clean up created test data
   */
  async cleanup(): Promise<void> {
    // Clean up speeches
    for (const speech of this.createdSpeeches) {
      try {
        await this.apiContext.delete(`/api/v1/analysis/${speech.title}`);
      } catch (error) {
        console.warn(`Could not delete speech ${speech.title}: ${error}`);
      }
    }
    
    // Clean up users
    for (const user of this.createdUsers) {
      try {
        const token = await this.loginUser(user);
        await this.apiContext.delete('/api/v1/users/me', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
      } catch (error) {
        console.warn(`Could not delete user ${user.email}: ${error}`);
      }
    }
    
    // Clear tracking arrays
    this.createdUsers = [];
    this.createdSpeeches = [];
  }
  
  /**
   * Verify database state for testing
   */
  async verifyDatabaseState(): Promise<{
    healthy: boolean;
    userCount: number;
    speechCount: number;
    issues: string[];
  }> {
    const issues: string[] = [];
    let userCount = 0;
    let speechCount = 0;
    
    try {
      // Check database health
      const healthResponse = await this.apiContext.get('/health');
      if (!healthResponse.ok()) {
        issues.push('Database health check failed');
      }
      
      // Try to get user count (if endpoint exists)
      try {
        const usersResponse = await this.apiContext.get('/api/v1/users/count');
        if (usersResponse.ok()) {
          const data = await usersResponse.json();
          userCount = data.count || 0;
        }
      } catch (error) {
        issues.push('Could not retrieve user count');
      }
      
      // Try to get speech count (if endpoint exists)
      try {
        const speechResponse = await this.apiContext.get('/api/v1/analysis/count');
        if (speechResponse.ok()) {
          const data = await speechResponse.json();
          speechCount = data.count || 0;
        }
      } catch (error) {
        issues.push('Could not retrieve speech count');
      }
      
    } catch (error) {
      issues.push(`Database verification failed: ${error}`);
    }
    
    return {
      healthy: issues.length === 0,
      userCount,
      speechCount,
      issues
    };
  }
  
  /**
   * Create test data for specific scenarios
   */
  async createScenarioData(scenario: 'empty' | 'basic' | 'comprehensive' | 'stress'): Promise<TestDataSnapshot> {
    const testRun = `scenario-${scenario}-${Date.now()}`;
    
    switch (scenario) {
      case 'empty':
        await this.resetDatabase();
        return {
          users: [],
          speeches: [],
          timestamp: new Date().toISOString(),
          testRun
        };
        
      case 'basic':
        const basicUser = await this.createUser();
        const basicSpeech = await this.createSpeechAnalysis(basicUser);
        return {
          users: [basicUser],
          speeches: [basicSpeech],
          timestamp: new Date().toISOString(),
          testRun
        };
        
      case 'comprehensive':
        return await this.seedDatabase();
        
      case 'stress':
        const stressUsers = await this.createUsers(10);
        const stressSpeeches: TestSpeech[] = [];
        
        for (const user of stressUsers) {
          for (let i = 0; i < 3; i++) {
            stressSpeeches.push(await this.createSpeechAnalysis(user));
          }
        }
        
        return {
          users: stressUsers,
          speeches: stressSpeeches,
          timestamp: new Date().toISOString(),
          testRun
        };
    }
  }
  
  /**
   * Export current test data state
   */
  exportState(): TestDataSnapshot {
    return {
      users: [...this.createdUsers],
      speeches: [...this.createdSpeeches],
      timestamp: new Date().toISOString(),
      testRun: `export-${Date.now()}`
    };
  }
  
  /**
   * Get created users for test validation
   */
  getCreatedUsers(): TestUser[] {
    return [...this.createdUsers];
  }
  
  /**
   * Get created speeches for test validation
   */
  getCreatedSpeeches(): TestSpeech[] {
    return [...this.createdSpeeches];
  }
  
  /**
   * Dispose of the API context
   */
  async dispose(): Promise<void> {
    if (this.apiContext) {
      await this.apiContext.dispose();
    }
  }
}