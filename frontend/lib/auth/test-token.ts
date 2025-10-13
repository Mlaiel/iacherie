/**
 * Test Authentication Token Manager
 * TEMPORAIRE: Pour les tests sans authentification
 */

export function getAuthToken(): string {
  // Vérifier si un token existe déjà
  if (typeof window !== 'undefined') {
    const existingToken = localStorage.getItem('token');
    if (existingToken) {
      return existingToken;
    }
    
    // Créer un token de test si aucun n'existe
    const testToken = 'test-token-' + Date.now();
    localStorage.setItem('token', testToken);
    console.log('🔑 Token de test créé:', testToken);
    return testToken;
  }
  
  return 'test-token-default';
}

export function getAuthHeaders(): HeadersInit {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getAuthToken()}`,
  };
}
