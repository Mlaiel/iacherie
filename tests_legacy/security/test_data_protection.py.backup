"""Test Data Protection Implementation
Comprehensive tests for the four data protection requirements:
1. AES-256 encryption repos
2. TLS 1.3 encryption transit  
3. End-to-end encryption communications
4. Key management HSM

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use strictly prohibited.
"""

import pytest
import asyncio
import json
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.security.data_protection import (
    DataProtectionManager,
    RepositoryDataProtection,
    TransitEncryption,
    EndToEndEncryption,
    HSMKeyManagement,
    DataProtectionLevel,
    EncryptionStandard,
    TransportSecurity
)


@pytest.mark.asyncio
async def test_aes_256_repository_encryption():
    """Test AES-256 encryption for repository data protection"""
    print("\n=== Testing AES-256 Repository Encryption ===")
    
    repo_protection = RepositoryDataProtection()
    
    # Test data encryption
    test_data = "Sensitive repository data that needs AES-256 protection"
    encrypt_result = await repo_protection.encrypt_repository_data(
        test_data,
        data_type="source_code",
        protection_level=DataProtectionLevel.MAXIMUM
    )
    
    assert encrypt_result.success, f"Encryption failed: {encrypt_result.error}"
    assert encrypt_result.algorithm == "AES-256-GCM", "Should use AES-256-GCM"
    assert encrypt_result.key_id is not None, "Should generate key ID"
    assert encrypt_result.iv is not None, "Should generate IV"
    assert encrypt_result.encrypted_data is not None, "Should have encrypted data"
    
    print(f"✓ Repository data encrypted with {encrypt_result.algorithm}")
    print(f"✓ Key ID: {encrypt_result.key_id}")
    print(f"✓ Protection level: {encrypt_result.metadata['protection_level']}")
    
    # Test data decryption
    decrypted_data = await repo_protection.decrypt_repository_data(
        encrypt_result.encrypted_data,
        encrypt_result.key_id,
        encrypt_result.iv,
        encrypt_result.metadata
    )
    
    assert decrypted_data is not None, "Decryption should succeed"
    assert decrypted_data.decode('utf-8') == test_data, "Decrypted data should match original"
    
    print("✓ Repository data decrypted successfully")
    print("✓ AES-256 repository encryption: PASS")


@pytest.mark.asyncio
async def test_tls_1_3_transit_encryption():
    """Test TLS 1.3 encryption for data in transit"""
    print("\n=== Testing TLS 1.3 Transit Encryption ===")
    
    transit_encryption = TransitEncryption()
    
    # Validate TLS 1.3 configuration
    config = transit_encryption.validate_tls_configuration()
    
    assert config["minimum_version"] == "TLS 1.3", "Should enforce TLS 1.3 minimum"
    assert config["maximum_version"] == "TLS 1.3", "Should enforce TLS 1.3 maximum"
    assert config["perfect_forward_secrecy"] is True, "Should enable PFS"
    assert config["certificate_verification"] is True, "Should verify certificates"
    assert config["hostname_verification"] is True, "Should verify hostnames"
    assert config["security_level"] == "MAXIMUM", "Should have maximum security"
    
    # Check cipher suites
    expected_ciphers = [
        "TLS_AES_256_GCM_SHA384",
        "TLS_CHACHA20_POLY1305_SHA256", 
        "TLS_AES_128_GCM_SHA256"
    ]
    assert all(cipher in config["cipher_suites"] for cipher in expected_ciphers), \
        "Should have secure TLS 1.3 cipher suites"
    
    print("✓ TLS 1.3 minimum/maximum version enforced")
    print("✓ Secure cipher suites configured")
    print("✓ Perfect Forward Secrecy enabled")
    print("✓ Certificate and hostname verification enabled")
    print("✓ TLS 1.3 transit encryption: PASS")


@pytest.mark.asyncio
async def test_end_to_end_encryption():
    """Test end-to-end encryption for communications"""
    print("\n=== Testing End-to-End Encryption Communications ===")
    
    e2e_encryption = EndToEndEncryption()
    
    # Generate key pairs for two participants
    alice_keys = await e2e_encryption.generate_key_pair("alice")
    bob_keys = await e2e_encryption.generate_key_pair("bob")
    
    assert "error" not in alice_keys, f"Alice key generation failed: {alice_keys.get('error')}"
    assert "error" not in bob_keys, f"Bob key generation failed: {bob_keys.get('error')}"
    assert alice_keys["algorithm"] == "RSA-4096", "Should use RSA-4096"
    assert bob_keys["algorithm"] == "RSA-4096", "Should use RSA-4096"
    assert alice_keys["key_size"] == 4096, "Should have 4096-bit keys"
    assert bob_keys["key_size"] == 4096, "Should have 4096-bit keys"
    
    print("✓ RSA-4096 key pairs generated for Alice and Bob")
    
    # Test message encryption from Alice to Bob
    test_message = "This is a confidential end-to-end encrypted message from Alice to Bob"
    encrypted_msg = await e2e_encryption.encrypt_message(
        test_message, "alice", "bob"
    )
    
    assert encrypted_msg is not None, "Message encryption should succeed"
    assert encrypted_msg["sender_id"] == "alice", "Should record sender"
    assert encrypted_msg["recipient_id"] == "bob", "Should record recipient"
    assert encrypted_msg["algorithm"] == "RSA-4096/AES-256-GCM", "Should use hybrid encryption"
    assert "encrypted_message" in encrypted_msg, "Should have encrypted message"
    assert "encrypted_key" in encrypted_msg, "Should have encrypted key"
    assert "iv" in encrypted_msg, "Should have IV"
    
    print("✓ Message encrypted with RSA-4096/AES-256-GCM hybrid encryption")
    
    # Test message decryption by Bob
    decrypted_msg = await e2e_encryption.decrypt_message(encrypted_msg, "bob")
    
    assert decrypted_msg is not None, "Message decryption should succeed"
    assert decrypted_msg.decode('utf-8') == test_message, "Decrypted message should match original"
    
    print("✓ Message decrypted successfully by recipient")
    print("✓ End-to-end encryption communications: PASS")


@pytest.mark.asyncio
async def test_hsm_key_management():
    """Test Hardware Security Module integration for key management"""
    print("\n=== Testing HSM Key Management ===")
    
    hsm_management = HSMKeyManagement()
    
    # Test HSM key generation
    hsm_result = await hsm_management.generate_hsm_key(
        key_type="AES",
        key_size=256,
        security_level="FIPS_140_2_LEVEL_4"
    )
    
    assert hsm_result["success"] is True, f"HSM key generation failed: {hsm_result.get('error')}"
    assert hsm_result["key_type"] == "AES", "Should generate AES key"
    assert hsm_result["algorithm"] == "AES-256", "Should be AES-256"
    assert hsm_result["security_level"] == "FIPS_140_2_LEVEL_4", "Should have FIPS 140-2 Level 4"
    assert hsm_result["tamper_resistant"] is True, "Should be tamper resistant"
    assert hsm_result["key_ceremony_required"] is True, "Should require key ceremony"
    
    # Verify compliance certifications
    expected_certifications = [
        "FIPS 140-2 Level 4",
        "Common Criteria EAL7+",
        "ISO 15408"
    ]
    assert all(cert in hsm_result["compliance_certifications"] for cert in expected_certifications), \
        "Should have proper compliance certifications"
    
    print(f"✓ HSM key generated: {hsm_result['key_id']}")
    print(f"✓ Algorithm: {hsm_result['algorithm']}")
    print(f"✓ Security level: {hsm_result['security_level']}")
    print(f"✓ Compliance certifications: {', '.join(hsm_result['compliance_certifications'])}")
    
    # Test key rotation
    key_id = hsm_result["key_id"]
    rotation_result = await hsm_management.rotate_hsm_key(key_id)
    
    assert rotation_result["success"] is True, f"Key rotation failed: {rotation_result.get('error')}"
    assert rotation_result["old_key_id"] == key_id, "Should reference old key"
    assert rotation_result["new_key_id"] != key_id, "Should generate new key ID"
    
    print(f"✓ Key rotation successful: {key_id} -> {rotation_result['new_key_id']}")
    
    # Test HSM status
    hsm_status = hsm_management.get_hsm_status()
    
    assert hsm_status["status"] == "OPERATIONAL", "HSM should be operational"
    assert hsm_status["security_level"] == "FIPS 140-2 Level 4", "Should have proper security level"
    assert hsm_status["tamper_detection"] == "ENABLED", "Should have tamper detection"
    assert hsm_status["total_keys"] >= 2, "Should have at least 2 keys (original + rotated)"
    
    print("✓ HSM status verified as OPERATIONAL")
    print("✓ HSM key management: PASS")


@pytest.mark.asyncio
async def test_comprehensive_data_protection():
    """Test all four data protection requirements together"""
    print("\n=== Testing Comprehensive Data Protection ===")
    
    data_protection = DataProtectionManager()
    
    # Run comprehensive test
    results = await data_protection.comprehensive_data_protection_test()
    
    # Verify all requirements pass
    assert results["aes_256_repos"]["status"] == "PASS", \
        f"AES-256 repository encryption failed: {results['aes_256_repos']}"
    
    assert results["tls_1_3_transit"]["status"] == "PASS", \
        f"TLS 1.3 transit encryption failed: {results['tls_1_3_transit']}"
    
    assert results["e2e_communications"]["status"] == "PASS", \
        f"End-to-end communications failed: {results['e2e_communications']}"
    
    assert results["hsm_key_management"]["status"] == "PASS", \
        f"HSM key management failed: {results['hsm_key_management']}"
    
    assert results["overall_status"] == "PASS", \
        f"Overall data protection test failed: {results}"
    
    print("✓ All four data protection requirements verified:")
    print(f"  - AES-256 encryption repos: {results['aes_256_repos']['status']}")
    print(f"  - TLS 1.3 encryption transit: {results['tls_1_3_transit']['status']}")
    print(f"  - End-to-end encryption communications: {results['e2e_communications']['status']}")
    print(f"  - Key management HSM: {results['hsm_key_management']['status']}")
    print("✓ Comprehensive data protection: PASS")


@pytest.mark.asyncio
async def test_data_protection_edge_cases():
    """Test edge cases and error handling"""
    print("\n=== Testing Data Protection Edge Cases ===")
    
    # Test empty data encryption
    repo_protection = RepositoryDataProtection()
    result = await repo_protection.encrypt_repository_data("")
    assert result.success, "Should handle empty data"
    
    # Test invalid key decryption
    invalid_result = await repo_protection.decrypt_repository_data(
        b"invalid_data", "invalid_key", b"invalid_iv", {}
    )
    assert invalid_result is None, "Should handle invalid decryption gracefully"
    
    # Test E2E with non-existent recipient
    e2e = EndToEndEncryption()
    await e2e.generate_key_pair("alice")
    
    encrypted = await e2e.encrypt_message("test", "alice", "nonexistent")
    assert encrypted is None, "Should handle non-existent recipient"
    
    print("✓ Edge cases handled correctly")


async def run_all_data_protection_tests():
    """Run all data protection tests"""
    print("=" * 80)
    print("DATA PROTECTION IMPLEMENTATION TESTING")
    print("=" * 80)
    
    try:
        await test_aes_256_repository_encryption()
        await test_tls_1_3_transit_encryption()  
        await test_end_to_end_encryption()
        await test_hsm_key_management()
        await test_comprehensive_data_protection()
        await test_data_protection_edge_cases()
        
        print("\n" + "=" * 80)
        print("✅ ALL DATA PROTECTION TESTS PASSED")
        print("=" * 80)
        
        print("\n📋 DATA PROTECTION REQUIREMENTS IMPLEMENTED:")
        print("✓ AES-256 encryption for repository data protection")
        print("✓ TLS 1.3 encryption for data in transit")
        print("✓ End-to-end encryption for communications")
        print("✓ Hardware Security Module (HSM) integration for key management")
        
        print("\n🔐 SECURITY FEATURES:")
        print("✓ AES-256-GCM authenticated encryption")
        print("✓ RSA-4096 asymmetric encryption")
        print("✓ Hybrid encryption for large messages")
        print("✓ Perfect Forward Secrecy with TLS 1.3")
        print("✓ FIPS 140-2 Level 4 HSM simulation")
        print("✓ Automated key rotation")
        print("✓ Tamper-resistant key storage")
        print("✓ Compliance certifications (FIPS, Common Criteria, ISO)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ DATA PROTECTION TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_data_protection_tests())
    exit(0 if success else 1)