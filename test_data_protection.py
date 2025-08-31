"""
Data Protection Test Suite
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Test suite to validate AES-256 encryption, TLS 1.3, E2E encryption, and HSM integration.
"""

import asyncio
import json
import base64
import tempfile
import os
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from security.encryption import get_aes256_encryption, get_content_encryption, get_database_encryption
    from security.e2e_encryption import get_e2e_manager
    from security.hsm_integration import get_hsm_manager, HSMBackend
    from security.tls_config import get_tls13_config
    SECURITY_MODULES_AVAILABLE = True
    print("✓ All security modules imported successfully")
except ImportError as e:
    print(f"❌ Security modules not available: {e}")
    SECURITY_MODULES_AVAILABLE = False
    sys.exit(1)


class DataProtectionTests:
    """Comprehensive test suite for data protection features."""
    
    def __init__(self):
        self.test_results = []
        self.aes_encryption = get_aes256_encryption()
        self.content_encryption = get_content_encryption()
        self.db_encryption = get_database_encryption()
        self.e2e_manager = get_e2e_manager()
        self.hsm_manager = None
        self.tls_config = get_tls13_config()
    
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result."""
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   {details}")
        
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'details': details
        })
    
    def test_aes256_encryption(self):
        """Test AES-256 encryption functionality."""
        print("\n=== Testing AES-256 Encryption ===")
        
        try:
            # Test basic encryption/decryption
            test_data = b"This is sensitive data that needs AES-256 protection!"
            
            # Test with master key
            encrypted_data = self.aes_encryption.encrypt(test_data)
            decrypted_data = self.aes_encryption.decrypt(encrypted_data)
            
            self.log_test(
                "AES-256 Basic Encryption/Decryption",
                test_data == decrypted_data,
                f"Original: {len(test_data)} bytes, Encrypted: {len(encrypted_data['ciphertext'])} bytes"
            )
            
            # Test key derivation
            context = "test_content"
            derived_key = self.aes_encryption.derive_key(context)
            self.log_test(
                "AES-256 Key Derivation",
                len(derived_key) == 32,
                f"Derived key length: {len(derived_key)} bytes"
            )
            
            # Test password-based encryption
            password = "strong_password_123"
            key, salt = self.aes_encryption.generate_key(password)
            encrypted_with_password = self.aes_encryption.encrypt(test_data, key)
            decrypted_with_password = self.aes_encryption.decrypt(encrypted_with_password, key)
            
            self.log_test(
                "AES-256 Password-Based Encryption",
                test_data == decrypted_with_password,
                f"Salt length: {len(salt)} bytes"
            )
            
        except Exception as e:
            self.log_test("AES-256 Encryption", False, f"Error: {str(e)}")
    
    def test_file_encryption(self):
        """Test file encryption capabilities."""
        print("\n=== Testing File Encryption ===")
        
        try:
            # Create test file
            test_content = "This is a test file with sensitive content.\n" * 100
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
                temp_file.write(test_content)
                temp_file_path = temp_file.name
            
            encrypted_file_path = temp_file_path + '.enc'
            decrypted_file_path = temp_file_path + '.dec'
            
            try:
                # Encrypt file
                encrypt_result = self.aes_encryption.encrypt_file(temp_file_path, encrypted_file_path)
                
                self.log_test(
                    "File Encryption",
                    encrypt_result.get('success', False),
                    f"Original: {encrypt_result.get('original_size', 0)} bytes, "
                    f"Encrypted: {encrypt_result.get('encrypted_size', 0)} bytes"
                )
                
                # Decrypt file
                decrypt_result = self.aes_encryption.decrypt_file(encrypted_file_path, decrypted_file_path)
                
                # Verify content
                with open(decrypted_file_path, 'r') as f:
                    decrypted_content = f.read()
                
                self.log_test(
                    "File Decryption",
                    decrypt_result.get('success', False) and decrypted_content == test_content,
                    f"Content integrity: {'preserved' if decrypted_content == test_content else 'corrupted'}"
                )
                
            finally:
                # Cleanup
                for file_path in [temp_file_path, encrypted_file_path, decrypted_file_path]:
                    if os.path.exists(file_path):
                        os.unlink(file_path)
                        
        except Exception as e:
            self.log_test("File Encryption", False, f"Error: {str(e)}")
    
    def test_content_encryption(self):
        """Test content encryption for different content types."""
        print("\n=== Testing Content Encryption ===")
        
        test_cases = [
            ("text", "This is a text document with sensitive information."),
            ("audio", b"Binary audio data would go here..."),
            ("video", b"Binary video data would go here..."),
            ("image", b"Binary image data would go here...")
        ]
        
        for content_type, content_data in test_cases:
            try:
                # Convert to bytes if needed
                if isinstance(content_data, str):
                    content_bytes = content_data.encode('utf-8')
                else:
                    content_bytes = content_data
                
                # Encrypt content
                encrypted_content = self.content_encryption.encrypt_content(
                    content_bytes, 
                    content_type=content_type
                )
                
                # Decrypt content
                decrypted_content = self.content_encryption.decrypt_content(encrypted_content)
                
                self.log_test(
                    f"Content Encryption ({content_type})",
                    content_bytes == decrypted_content,
                    f"Algorithm: {encrypted_content.get('algorithm')}"
                )
                
            except Exception as e:
                self.log_test(f"Content Encryption ({content_type})", False, f"Error: {str(e)}")
    
    def test_database_encryption(self):
        """Test database field encryption."""
        print("\n=== Testing Database Encryption ===")
        
        test_fields = [
            ("users", "email", "user@example.com"),
            ("creators", "real_name", "John Doe"),
            ("content_files", "file_path", "/secure/path/to/file.mp4"),
            ("revenue_data", "amount", "1250.75")
        ]
        
        for table_name, field_name, field_value in test_fields:
            try:
                # Encrypt field
                encrypted_value = self.db_encryption.encrypt_field(field_value, field_name, table_name)
                
                # Decrypt field
                decrypted_value = self.db_encryption.decrypt_field(encrypted_value, field_name, table_name)
                
                self.log_test(
                    f"Database Field Encryption ({table_name}.{field_name})",
                    field_value == decrypted_value,
                    f"Encrypted length: {len(encrypted_value)} chars"
                )
                
            except Exception as e:
                self.log_test(f"Database Field Encryption ({table_name}.{field_name})", False, f"Error: {str(e)}")
    
    async def test_e2e_encryption(self):
        """Test end-to-end encryption."""
        print("\n=== Testing End-to-End Encryption ===")
        
        try:
            # Create E2E session
            session_info = self.e2e_manager.create_session()
            session_id = session_info['session_id']
            server_public_key = session_info['public_key']
            
            self.log_test(
                "E2E Session Creation",
                'session_id' in session_info and 'public_key' in session_info,
                f"Session ID: {session_id[:8]}..."
            )
            
            # Simulate client-side key exchange (normally done by client)
            from security.e2e_encryption import KeyExchange
            client_key_exchange = KeyExchange()
            client_public_key = client_key_exchange.get_public_key_b64()
            
            # Complete handshake
            handshake_result = self.e2e_manager.establish_session(session_id, client_public_key)
            
            self.log_test(
                "E2E Handshake",
                handshake_result.get('established', False),
                f"Algorithm: {handshake_result.get('algorithm')}"
            )
            
            # Test message encryption/decryption
            test_message = "This is a confidential message that requires end-to-end encryption!"
            
            encrypted_message = self.e2e_manager.encrypt_message(session_id, test_message)
            decrypted_message = self.e2e_manager.decrypt_message(session_id, encrypted_message)
            
            self.log_test(
                "E2E Message Encryption",
                test_message == decrypted_message,
                f"Message counter: {encrypted_message.get('counter')}"
            )
            
        except Exception as e:
            self.log_test("E2E Encryption", False, f"Error: {str(e)}")
    
    async def test_hsm_integration(self):
        """Test HSM key management."""
        print("\n=== Testing HSM Integration ===")
        
        try:
            # Initialize local HSM for testing
            hsm_config = {'storage_path': './test_keys'}
            self.hsm_manager = get_hsm_manager(HSMBackend.LOCAL_HSM, hsm_config)
            
            # Connect to HSM
            connected = await self.hsm_manager.connect()
            
            self.log_test(
                "HSM Connection",
                connected,
                f"Backend: {self.hsm_manager.backend.value}"
            )
            
            if connected:
                # Generate master key
                master_key_id = await self.hsm_manager.create_master_key()
                
                self.log_test(
                    "HSM Master Key Generation",
                    master_key_id is not None,
                    f"Key ID: {master_key_id}"
                )
                
                # Generate data encryption key
                dek_id = await self.hsm_manager.create_data_encryption_key("test_content")
                
                self.log_test(
                    "HSM Data Encryption Key Generation",
                    dek_id is not None,
                    f"DEK ID: {dek_id}"
                )
                
                # Test encryption/decryption with HSM
                test_data = b"Test data for HSM encryption"
                encrypted_data = await self.hsm_manager.encrypt_data(dek_id, test_data)
                decrypted_data = await self.hsm_manager.decrypt_data(dek_id, encrypted_data)
                
                self.log_test(
                    "HSM Data Encryption/Decryption",
                    test_data == decrypted_data,
                    f"Data length: {len(test_data)} bytes"
                )
                
                # Test key rotation
                new_key_id = await self.hsm_manager.rotate_key(dek_id)
                
                self.log_test(
                    "HSM Key Rotation",
                    new_key_id != dek_id,
                    f"Old: {dek_id}, New: {new_key_id}"
                )
            
        except Exception as e:
            self.log_test("HSM Integration", False, f"Error: {str(e)}")
        finally:
            # Cleanup test keys
            import shutil
            test_keys_dir = './test_keys'
            if os.path.exists(test_keys_dir):
                shutil.rmtree(test_keys_dir)
    
    def test_tls13_config(self):
        """Test TLS 1.3 configuration."""
        print("\n=== Testing TLS 1.3 Configuration ===")
        
        try:
            # Test SSL context creation
            ssl_context = self.tls_config.get_ssl_context()
            
            self.log_test(
                "TLS 1.3 SSL Context Creation",
                ssl_context is not None,
                f"Min version: TLS 1.3, Protocol: {ssl_context.protocol}"
            )
            
            # Test uvicorn configuration
            uvicorn_config = self.tls_config.get_uvicorn_ssl_config()
            
            required_keys = ['ssl_certfile', 'ssl_keyfile', 'ssl_version']
            config_valid = all(key in uvicorn_config for key in required_keys)
            
            self.log_test(
                "TLS 1.3 Uvicorn Configuration",
                config_valid,
                f"Cert file: {uvicorn_config.get('ssl_certfile', 'N/A')}"
            )
            
        except Exception as e:
            self.log_test("TLS 1.3 Configuration", False, f"Error: {str(e)}")
    
    async def run_all_tests(self):
        """Run all data protection tests."""
        print("🔐 Starting Ainflue Data Protection Test Suite")
        print("=" * 60)
        
        # Run synchronous tests
        self.test_aes256_encryption()
        self.test_file_encryption()
        self.test_content_encryption()
        self.test_database_encryption()
        self.test_tls13_config()
        
        # Run asynchronous tests
        await self.test_e2e_encryption()
        await self.test_hsm_integration()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🔐 Data Protection Test Summary")
        print("=" * 60)
        
        passed_tests = sum(1 for result in self.test_results if result['passed'])
        total_tests = len(self.test_results)
        
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success rate: {(passed_tests / total_tests * 100):.1f}%")
        
        if passed_tests == total_tests:
            print("\n✅ All data protection requirements implemented successfully!")
            print("   - ✓ AES-256 encryption for repositories (data at rest)")
            print("   - ✓ TLS 1.3 encryption for data in transit")
            print("   - ✓ End-to-end encryption for communications")
            print("   - ✓ HSM-based key management system")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Review implementation.")
            
            # Print failed tests
            for result in self.test_results:
                if not result['passed']:
                    print(f"   ❌ {result['test']}: {result['details']}")
        
        return passed_tests == total_tests


async def main():
    """Main test execution function."""
    try:
        test_suite = DataProtectionTests()
        success = await test_suite.run_all_tests()
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"❌ Test suite execution failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())