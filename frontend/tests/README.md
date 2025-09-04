# Frontend Tests

This directory contains all frontend tests for the Ainflue platform, following the project consolidation guidelines.

## Test Structure

### Test Files
- `integration.test.tsx` - Integration tests for frontend components
- `gamification.test.tsx` - Gamification system tests
- `redux-store.test.ts` - Redux store state management tests
- `remix-studio.test.tsx` - Remix studio functionality tests
- `test_gamification_frontend.ts` - Additional gamification tests

## Running Tests

```bash
# Run all frontend tests
npm test

# Run specific test file
npm test -- integration.test.tsx

# Run tests in watch mode
npm test -- --watch
```

## Test Configuration

Frontend tests use Jest and React Testing Library for comprehensive component and integration testing.

## Standards

- All frontend tests are consolidated in this directory
- Tests follow React Testing Library best practices
- Integration tests cover complete user workflows
- Component tests verify UI behavior and state management