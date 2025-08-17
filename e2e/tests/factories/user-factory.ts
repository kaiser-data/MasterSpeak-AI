/**
 * User Factory for E2E Tests
 * Generates realistic test user data for various testing scenarios
 */

import { faker } from '@faker-js/faker';

export interface TestUser {
  email: string;
  password: string;
  fullName: string;
  firstName?: string;
  lastName?: string;
  id?: string;
}

export interface UserCreationOptions {
  domain?: string;
  password?: string;
  verified?: boolean;
  active?: boolean;
}

export class UserFactory {
  private static readonly DEFAULT_PASSWORD = 'Test123!';
  private static readonly TEST_DOMAIN = 'playwright-test.com';
  
  /**
   * Create a basic test user with standard credentials
   */
  static createBasic(options: UserCreationOptions = {}): TestUser {
    const firstName = faker.person.firstName();
    const lastName = faker.person.lastName();
    const domain = options.domain || this.TEST_DOMAIN;
    
    return {
      email: `${firstName.toLowerCase()}.${lastName.toLowerCase()}@${domain}`,
      password: options.password || this.DEFAULT_PASSWORD,
      fullName: `${firstName} ${lastName}`,
      firstName,
      lastName,
      id: faker.string.uuid()
    };
  }
  
  /**
   * Create a demo user with predictable credentials for consistent testing
   */
  static createDemo(): TestUser {
    return {
      email: 'demo@masterspeak.ai',
      password: 'Demo123!',
      fullName: 'Demo User',
      firstName: 'Demo',
      lastName: 'User',
      id: 'demo-user-id-12345'
    };
  }
  
  /**
   * Create a test user for automated testing
   */
  static createTest(): TestUser {
    return {
      email: 'test@playwright.com',
      password: 'Test123!',
      fullName: 'Playwright Test User',
      firstName: 'Playwright',
      lastName: 'Test',
      id: 'test-user-id-67890'
    };
  }
  
  /**
   * Create multiple users for batch testing scenarios
   */
  static createBatch(count: number, options: UserCreationOptions = {}): TestUser[] {
    return Array.from({ length: count }, () => this.createBasic(options));
  }
  
  /**
   * Create a user with specific characteristics for edge case testing
   */
  static createWithCharacteristics(characteristics: {
    emailLength?: 'short' | 'medium' | 'long';
    nameComplexity?: 'simple' | 'complex' | 'international';
    passwordStrength?: 'weak' | 'medium' | 'strong';
  }): TestUser {
    const { emailLength = 'medium', nameComplexity = 'simple', passwordStrength = 'strong' } = characteristics;
    
    let firstName = faker.person.firstName();
    let lastName = faker.person.lastName();
    let email = '';
    let password = '';
    
    // Handle name complexity
    switch (nameComplexity) {
      case 'simple':
        firstName = faker.person.firstName();
        lastName = faker.person.lastName();
        break;
      case 'complex':
        firstName = `${faker.person.firstName()}-${faker.person.firstName()}`;
        lastName = `${faker.person.lastName()} ${faker.person.lastName()}`;
        break;
      case 'international':
        firstName = faker.person.firstName();
        lastName = faker.person.lastName();
        break;
    }
    
    // Handle email length
    const baseEmail = `${firstName.toLowerCase()}.${lastName.toLowerCase()}`.replace(/[^a-z.]/g, '');
    switch (emailLength) {
      case 'short':
        email = `${baseEmail.substring(0, 8)}@test.com`;
        break;
      case 'medium':
        email = `${baseEmail}@${this.TEST_DOMAIN}`;
        break;
      case 'long':
        email = `${baseEmail}.extended.testing.account@very-long-domain-name-for-testing.com`;
        break;
    }
    
    // Handle password strength
    switch (passwordStrength) {
      case 'weak':
        password = 'test123';
        break;
      case 'medium':
        password = 'Test123!';
        break;
      case 'strong':
        password = faker.internet.password({ length: 16, memorable: false, pattern: /[A-Za-z0-9!@#$%^&*]/ });
        break;
    }
    
    return {
      email,
      password,
      fullName: `${firstName} ${lastName}`,
      firstName,
      lastName,
      id: faker.string.uuid()
    };
  }
  
  /**
   * Create users for specific roles/scenarios
   */
  static createForScenario(scenario: 'new_user' | 'returning_user' | 'premium_user' | 'admin_user'): TestUser {
    const baseUser = this.createBasic();
    
    switch (scenario) {
      case 'new_user':
        return {
          ...baseUser,
          email: `new.user.${Date.now()}@${this.TEST_DOMAIN}`
        };
      case 'returning_user':
        return {
          ...baseUser,
          email: `returning.user@${this.TEST_DOMAIN}`
        };
      case 'premium_user':
        return {
          ...baseUser,
          email: `premium.user@${this.TEST_DOMAIN}`,
          fullName: 'Premium Test User'
        };
      case 'admin_user':
        return {
          ...baseUser,
          email: `admin@${this.TEST_DOMAIN}`,
          fullName: 'Admin Test User',
          password: 'AdminTest123!'
        };
    }
  }
  
  /**
   * Create a user with invalid data for negative testing
   */
  static createInvalid(invalidField: 'email' | 'password' | 'name'): Partial<TestUser> {
    const baseUser = this.createBasic();
    
    switch (invalidField) {
      case 'email':
        return {
          ...baseUser,
          email: 'invalid-email-format'
        };
      case 'password':
        return {
          ...baseUser,
          password: '123' // Too short
        };
      case 'name':
        return {
          ...baseUser,
          fullName: '' // Empty name
        };
    }
  }
  
  /**
   * Generate a temporary email for testing email verification flows
   */
  static generateTempEmail(): string {
    const timestamp = Date.now();
    return `temp.${timestamp}@${this.TEST_DOMAIN}`;
  }
}

/**
 * Predefined test users for consistent testing across different test files
 */
export const PredefinedUsers = {
  demo: UserFactory.createDemo(),
  test: UserFactory.createTest(),
  newUser: UserFactory.createForScenario('new_user'),
  returningUser: UserFactory.createForScenario('returning_user'),
  premiumUser: UserFactory.createForScenario('premium_user'),
  adminUser: UserFactory.createForScenario('admin_user')
} as const;

/**
 * User data sets for different testing scenarios
 */
export const UserDataSets = {
  validRegistration: [
    UserFactory.createBasic(),
    UserFactory.createWithCharacteristics({ nameComplexity: 'complex' }),
    UserFactory.createWithCharacteristics({ emailLength: 'long' })
  ],
  
  invalidRegistration: [
    UserFactory.createInvalid('email'),
    UserFactory.createInvalid('password'),
    UserFactory.createInvalid('name')
  ],
  
  edgeCases: [
    UserFactory.createWithCharacteristics({ emailLength: 'short', passwordStrength: 'weak' }),
    UserFactory.createWithCharacteristics({ nameComplexity: 'international', passwordStrength: 'strong' }),
    UserFactory.createWithCharacteristics({ emailLength: 'long', nameComplexity: 'complex' })
  ]
} as const;