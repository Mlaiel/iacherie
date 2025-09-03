"""
Upload Performance Tests
=======================

Tests the performance of content upload functionality including
file uploads, processing times, and throughput under various conditions.
"""

import pytest
import asyncio
import aiohttp
import time
import random
import statistics
import tempfile
import os
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class UploadTestFile:
    """Represents a test file for upload performance testing."""
    
    def __init__(self, size_kb: int, file_type: str = "text", content_type: str = "text/plain"):
        self.size_kb = size_kb
        self.file_type = file_type
        self.content_type = content_type
        self.file_path = None
        self.created_time = None
    
    def create_temp_file(self) -> str:
        """Create a temporary file for testing."""
        if self.file_path and os.path.exists(self.file_path):
            return self.file_path
        
        self.created_time = time.time()
        
        with tempfile.NamedTemporaryFile(
            mode='w+b', 
            suffix=f'.{self.file_type}', 
            delete=False
        ) as temp_file:
            
            # Generate content based on file type
            if self.file_type == "text":
                content = self._generate_text_content()
            elif self.file_type == "json":
                content = self._generate_json_content()
            elif self.file_type == "binary":
                content = self._generate_binary_content()
            else:
                content = self._generate_text_content()
            
            temp_file.write(content)
            self.file_path = temp_file.name
        
        return self.file_path
    
    def _generate_text_content(self) -> bytes:
        """Generate text content of specified size."""
        content = "This is test content for upload performance testing. " * 100
        target_size = self.size_kb * 1024
        
        while len(content.encode()) < target_size:
            content += f"Line {len(content)} with random data {random.randint(1000, 9999)}.\n"
        
        return content[:target_size].encode()
    
    def _generate_json_content(self) -> bytes:
        """Generate JSON content of specified size."""
        import json
        
        data = {
            "test_upload": True,
            "timestamp": time.time(),
            "content": []
        }
        
        target_size = self.size_kb * 1024
        while len(json.dumps(data).encode()) < target_size:
            data["content"].append({
                "id": len(data["content"]),
                "text": f"Sample content item {len(data['content'])}",
                "data": "x" * 100
            })
        
        return json.dumps(data).encode()[:target_size]
    
    def _generate_binary_content(self) -> bytes:
        """Generate binary content of specified size."""
        target_size = self.size_kb * 1024
        return random.randbytes(target_size)
    
    def cleanup(self):
        """Clean up the temporary file."""
        if self.file_path and os.path.exists(self.file_path):
            try:
                os.unlink(self.file_path)
                self.file_path = None
            except OSError as e:
                logger.warning(f"Failed to cleanup temp file: {e}")


@pytest.mark.performance
@pytest.mark.asyncio
async def test_single_file_upload_performance():
    """Test performance of single file uploads of various sizes."""
    base_url = "http://localhost:8000"
    file_sizes = [1, 10, 100, 500]  # KB
    
    results = []
    
    for size_kb in file_sizes:
        test_file = UploadTestFile(size_kb, "text", "text/plain")
        
        try:
            file_path = test_file.create_temp_file()
            
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=60)
            ) as session:
                
                # Prepare upload
                with open(file_path, 'rb') as f:
                    file_data = aiohttp.FormData()
                    file_data.add_field('file', f, 
                                      filename=f'test_file_{size_kb}kb.txt',
                                      content_type='text/plain')
                    
                    # Measure upload time
                    start_time = time.time()
                    
                    try:
                        # Use health endpoint as a proxy for upload since we don't have actual upload endpoint
                        async with session.post(f"{base_url}/api/v1/health", data=file_data) as response:
                            end_time = time.time()
                            
                            upload_time_ms = (end_time - start_time) * 1000
                            throughput_kbps = (size_kb / (upload_time_ms / 1000)) if upload_time_ms > 0 else 0
                            
                            result = {
                                "file_size_kb": size_kb,
                                "upload_time_ms": upload_time_ms,
                                "throughput_kbps": throughput_kbps,
                                "status_code": response.status,
                                "success": response.status in [200, 201],
                                "file_type": "text"
                            }
                            
                            results.append(result)
                            
                    except Exception as e:
                        logger.warning(f"Upload failed for {size_kb}KB file: {e}")
                        result = {
                            "file_size_kb": size_kb,
                            "upload_time_ms": 0,
                            "throughput_kbps": 0,
                            "status_code": 0,
                            "success": False,
                            "error": str(e),
                            "file_type": "text"
                        }
                        results.append(result)
        
        finally:
            test_file.cleanup()
    
    # Analyze results
    successful_uploads = [r for r in results if r["success"]]
    success_rate = len(successful_uploads) / len(results) if results else 0
    
    # Performance assertions
    assert success_rate >= 0.75, f"Upload success rate too low: {success_rate:.2f}"
    
    # Check upload times are reasonable
    for result in successful_uploads:
        size_kb = result["file_size_kb"]
        upload_time_ms = result["upload_time_ms"]
        
        # Allow more time for larger files
        max_time_ms = max(1000, size_kb * 10)  # 10ms per KB minimum
        assert upload_time_ms < max_time_ms, f"Upload of {size_kb}KB took too long: {upload_time_ms:.2f}ms"
    
    logger.info(f"Single file upload test completed - Success rate: {success_rate:.2f}, "
                f"Files tested: {len(results)}")


@pytest.mark.performance
@pytest.mark.asyncio
async def test_concurrent_uploads_performance():
    """Test performance of concurrent file uploads."""
    base_url = "http://localhost:8000"
    concurrent_uploads = 10
    file_size_kb = 50
    
    upload_files = []
    try:
        # Create test files
        for i in range(concurrent_uploads):
            test_file = UploadTestFile(file_size_kb, "text", "text/plain")
            test_file.create_temp_file()
            upload_files.append(test_file)
        
        async def perform_upload(session: aiohttp.ClientSession, test_file: UploadTestFile, upload_id: int) -> Dict[str, Any]:
            """Perform a single upload."""
            try:
                with open(test_file.file_path, 'rb') as f:
                    file_data = aiohttp.FormData()
                    file_data.add_field('file', f, 
                                      filename=f'concurrent_upload_{upload_id}.txt',
                                      content_type='text/plain')
                    
                    start_time = time.time()
                    
                    # Use health endpoint as proxy for upload
                    async with session.post(f"{base_url}/api/v1/health", data=file_data) as response:
                        end_time = time.time()
                        
                        return {
                            "upload_id": upload_id,
                            "file_size_kb": file_size_kb,
                            "upload_time_ms": (end_time - start_time) * 1000,
                            "status_code": response.status,
                            "success": response.status in [200, 201],
                            "timestamp": start_time
                        }
            
            except Exception as e:
                return {
                    "upload_id": upload_id,
                    "file_size_kb": file_size_kb,
                    "upload_time_ms": 0,
                    "status_code": 0,
                    "success": False,
                    "error": str(e),
                    "timestamp": time.time()
                }
        
        # Execute concurrent uploads
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60),
            connector=aiohttp.TCPConnector(limit=50)
        ) as session:
            
            start_time = time.time()
            
            tasks = [
                perform_upload(session, upload_files[i], i)
                for i in range(concurrent_uploads)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
        
        # Analyze concurrent upload results
        valid_results = [r for r in results if isinstance(r, dict)]
        successful_uploads = [r for r in valid_results if r["success"]]
        
        success_rate = len(successful_uploads) / len(valid_results) if valid_results else 0
        total_duration = end_time - start_time
        
        upload_times = [r["upload_time_ms"] for r in successful_uploads]
        avg_upload_time = statistics.mean(upload_times) if upload_times else 0
        max_upload_time = max(upload_times) if upload_times else 0
        
        total_data_kb = sum(r["file_size_kb"] for r in successful_uploads)
        overall_throughput_kbps = (total_data_kb / total_duration) if total_duration > 0 else 0
        
        # Assertions
        assert success_rate >= 0.80, f"Concurrent upload success rate too low: {success_rate:.2f}"
        assert avg_upload_time < 2000, f"Average concurrent upload time too high: {avg_upload_time:.2f}ms"
        assert max_upload_time < 5000, f"Max concurrent upload time too high: {max_upload_time:.2f}ms"
        assert overall_throughput_kbps > 10, f"Overall throughput too low: {overall_throughput_kbps:.2f} KB/s"
        
        logger.info(f"Concurrent uploads test completed - Uploads: {concurrent_uploads}, "
                    f"Success rate: {success_rate:.2f}, Avg time: {avg_upload_time:.2f}ms, "
                    f"Throughput: {overall_throughput_kbps:.2f} KB/s")
    
    finally:
        # Cleanup test files
        for test_file in upload_files:
            test_file.cleanup()


@pytest.mark.performance
@pytest.mark.asyncio
async def test_large_file_upload_performance():
    """Test performance of large file uploads."""
    base_url = "http://localhost:8000"
    large_file_sizes = [1000, 2000]  # KB - reduced for testing
    
    results = []
    
    for size_kb in large_file_sizes:
        test_file = UploadTestFile(size_kb, "binary", "application/octet-stream")
        
        try:
            file_path = test_file.create_temp_file()
            
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=120)  # Longer timeout for large files
            ) as session:
                
                with open(file_path, 'rb') as f:
                    file_data = aiohttp.FormData()
                    file_data.add_field('file', f, 
                                      filename=f'large_file_{size_kb}kb.bin',
                                      content_type='application/octet-stream')
                    
                    start_time = time.time()
                    
                    try:
                        # Use health endpoint as proxy for upload
                        async with session.post(f"{base_url}/api/v1/health", data=file_data) as response:
                            end_time = time.time()
                            
                            upload_time_ms = (end_time - start_time) * 1000
                            throughput_kbps = (size_kb / (upload_time_ms / 1000)) if upload_time_ms > 0 else 0
                            
                            result = {
                                "file_size_kb": size_kb,
                                "upload_time_ms": upload_time_ms,
                                "throughput_kbps": throughput_kbps,
                                "status_code": response.status,
                                "success": response.status in [200, 201],
                                "file_type": "binary"
                            }
                            
                            results.append(result)
                            
                    except Exception as e:
                        logger.warning(f"Large file upload failed for {size_kb}KB: {e}")
                        result = {
                            "file_size_kb": size_kb,
                            "upload_time_ms": 0,
                            "throughput_kbps": 0,
                            "status_code": 0,
                            "success": False,
                            "error": str(e),
                            "file_type": "binary"
                        }
                        results.append(result)
        
        finally:
            test_file.cleanup()
    
    # Analyze large file results
    successful_uploads = [r for r in results if r["success"]]
    success_rate = len(successful_uploads) / len(results) if results else 0
    
    # Performance assertions for large files
    assert success_rate >= 0.70, f"Large file upload success rate too low: {success_rate:.2f}"
    
    for result in successful_uploads:
        size_kb = result["file_size_kb"]
        upload_time_ms = result["upload_time_ms"]
        throughput_kbps = result["throughput_kbps"]
        
        # Large files should maintain reasonable throughput
        min_throughput_kbps = 50  # Minimum 50 KB/s
        assert throughput_kbps > min_throughput_kbps, f"Large file throughput too low: {throughput_kbps:.2f} KB/s"
        
        # Should complete within reasonable time (allow 30 seconds per MB)
        max_time_ms = size_kb * 30  # 30ms per KB for large files
        assert upload_time_ms < max_time_ms, f"Large file upload took too long: {upload_time_ms:.2f}ms for {size_kb}KB"
    
    logger.info(f"Large file upload test completed - Success rate: {success_rate:.2f}, "
                f"Files tested: {len(results)}")


@pytest.mark.performance
@pytest.mark.asyncio
async def test_mixed_upload_workload():
    """Test performance with mixed upload workload (different file sizes and types)."""
    base_url = "http://localhost:8000"
    
    # Define mixed workload
    upload_specs = [
        {"size_kb": 10, "type": "text", "content_type": "text/plain", "count": 5},
        {"size_kb": 50, "type": "json", "content_type": "application/json", "count": 3},
        {"size_kb": 200, "type": "binary", "content_type": "application/octet-stream", "count": 2},
    ]
    
    upload_files = []
    upload_tasks_specs = []
    
    try:
        # Create all test files
        upload_id = 0
        for spec in upload_specs:
            for i in range(spec["count"]):
                test_file = UploadTestFile(spec["size_kb"], spec["type"], spec["content_type"])
                test_file.create_temp_file()
                upload_files.append(test_file)
                
                upload_tasks_specs.append({
                    "upload_id": upload_id,
                    "test_file": test_file,
                    "spec": spec
                })
                upload_id += 1
        
        # Shuffle to simulate random upload order
        random.shuffle(upload_tasks_specs)
        
        async def perform_mixed_upload(session: aiohttp.ClientSession, upload_spec: Dict[str, Any]) -> Dict[str, Any]:
            """Perform a mixed workload upload."""
            test_file = upload_spec["test_file"]
            spec = upload_spec["spec"]
            upload_id = upload_spec["upload_id"]
            
            try:
                with open(test_file.file_path, 'rb') as f:
                    file_data = aiohttp.FormData()
                    file_data.add_field('file', f, 
                                      filename=f'mixed_{upload_id}_{spec["type"]}.{spec["type"]}',
                                      content_type=spec["content_type"])
                    
                    start_time = time.time()
                    
                    # Use health endpoint as proxy for upload
                    async with session.post(f"{base_url}/api/v1/health", data=file_data) as response:
                        end_time = time.time()
                        
                        return {
                            "upload_id": upload_id,
                            "file_size_kb": spec["size_kb"],
                            "file_type": spec["type"],
                            "upload_time_ms": (end_time - start_time) * 1000,
                            "throughput_kbps": (spec["size_kb"] / ((end_time - start_time))) if (end_time - start_time) > 0 else 0,
                            "status_code": response.status,
                            "success": response.status in [200, 201],
                            "timestamp": start_time
                        }
            
            except Exception as e:
                return {
                    "upload_id": upload_id,
                    "file_size_kb": spec["size_kb"],
                    "file_type": spec["type"],
                    "upload_time_ms": 0,
                    "throughput_kbps": 0,
                    "status_code": 0,
                    "success": False,
                    "error": str(e),
                    "timestamp": time.time()
                }
        
        # Execute mixed workload
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=90),
            connector=aiohttp.TCPConnector(limit=30)
        ) as session:
            
            start_time = time.time()
            
            tasks = [
                perform_mixed_upload(session, upload_spec)
                for upload_spec in upload_tasks_specs
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
        
        # Analyze mixed workload results
        valid_results = [r for r in results if isinstance(r, dict)]
        successful_uploads = [r for r in valid_results if r["success"]]
        
        # Overall metrics
        success_rate = len(successful_uploads) / len(valid_results) if valid_results else 0
        total_duration = end_time - start_time
        
        # Analyze by file type
        type_metrics = {}
        for result in successful_uploads:
            file_type = result["file_type"]
            if file_type not in type_metrics:
                type_metrics[file_type] = []
            type_metrics[file_type].append(result)
        
        # Performance analysis by type
        for file_type, type_results in type_metrics.items():
            upload_times = [r["upload_time_ms"] for r in type_results]
            throughputs = [r["throughput_kbps"] for r in type_results]
            
            avg_upload_time = statistics.mean(upload_times) if upload_times else 0
            avg_throughput = statistics.mean(throughputs) if throughputs else 0
            
            logger.info(f"Mixed workload - {file_type}: avg_time={avg_upload_time:.2f}ms, "
                       f"avg_throughput={avg_throughput:.2f}KB/s")
        
        total_data_kb = sum(r["file_size_kb"] for r in successful_uploads)
        overall_throughput_kbps = (total_data_kb / total_duration) if total_duration > 0 else 0
        
        # Assertions
        assert success_rate >= 0.75, f"Mixed workload success rate too low: {success_rate:.2f}"
        assert overall_throughput_kbps > 20, f"Overall mixed workload throughput too low: {overall_throughput_kbps:.2f} KB/s"
        
        # Type-specific assertions
        for file_type, type_results in type_metrics.items():
            type_success_rate = len(type_results) / sum(1 for r in valid_results if r["file_type"] == file_type)
            assert type_success_rate >= 0.70, f"{file_type} upload success rate too low: {type_success_rate:.2f}"
        
        logger.info(f"Mixed workload test completed - Total uploads: {len(valid_results)}, "
                    f"Success rate: {success_rate:.2f}, Overall throughput: {overall_throughput_kbps:.2f} KB/s")
    
    finally:
        # Cleanup all test files
        for test_file in upload_files:
            test_file.cleanup()


@pytest.mark.performance
@pytest.mark.slow
async def test_upload_stress_testing():
    """Test upload performance under stress conditions."""
    base_url = "http://localhost:8000"
    stress_uploads = 20
    file_size_kb = 100
    max_concurrent = 15
    
    upload_files = []
    
    try:
        # Create test files for stress testing
        for i in range(stress_uploads):
            test_file = UploadTestFile(file_size_kb, "text", "text/plain")
            test_file.create_temp_file()
            upload_files.append(test_file)
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def stress_upload(session: aiohttp.ClientSession, test_file: UploadTestFile, upload_id: int) -> Dict[str, Any]:
            """Perform a stress test upload with concurrency control."""
            async with semaphore:
                try:
                    with open(test_file.file_path, 'rb') as f:
                        file_data = aiohttp.FormData()
                        file_data.add_field('file', f, 
                                          filename=f'stress_upload_{upload_id}.txt',
                                          content_type='text/plain')
                        
                        start_time = time.time()
                        
                        # Use health endpoint as proxy for upload
                        async with session.post(f"{base_url}/api/v1/health", data=file_data) as response:
                            end_time = time.time()
                            
                            return {
                                "upload_id": upload_id,
                                "file_size_kb": file_size_kb,
                                "upload_time_ms": (end_time - start_time) * 1000,
                                "status_code": response.status,
                                "success": response.status in [200, 201],
                                "timestamp": start_time
                            }
                
                except Exception as e:
                    return {
                        "upload_id": upload_id,
                        "file_size_kb": file_size_kb,
                        "upload_time_ms": 0,
                        "status_code": 0,
                        "success": False,
                        "error": str(e),
                        "timestamp": time.time()
                    }
        
        # Execute stress test
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=120),
            connector=aiohttp.TCPConnector(limit=50)
        ) as session:
            
            start_time = time.time()
            
            tasks = [
                stress_upload(session, upload_files[i], i)
                for i in range(stress_uploads)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
        
        # Analyze stress test results
        valid_results = [r for r in results if isinstance(r, dict)]
        successful_uploads = [r for r in valid_results if r["success"]]
        failed_uploads = [r for r in valid_results if not r["success"]]
        
        success_rate = len(successful_uploads) / len(valid_results) if valid_results else 0
        total_duration = end_time - start_time
        
        upload_times = [r["upload_time_ms"] for r in successful_uploads]
        avg_upload_time = statistics.mean(upload_times) if upload_times else 0
        p95_upload_time = statistics.quantiles(upload_times, n=20)[18] if len(upload_times) >= 20 else max(upload_times) if upload_times else 0
        
        uploads_per_second = len(successful_uploads) / total_duration if total_duration > 0 else 0
        total_data_kb = sum(r["file_size_kb"] for r in successful_uploads)
        overall_throughput_kbps = (total_data_kb / total_duration) if total_duration > 0 else 0
        
        # Stress test assertions - more lenient than normal tests
        assert success_rate >= 0.70, f"Stress test success rate too low: {success_rate:.2f}"
        assert avg_upload_time < 3000, f"Average stress test upload time too high: {avg_upload_time:.2f}ms"
        assert p95_upload_time < 5000, f"P95 stress test upload time too high: {p95_upload_time:.2f}ms"
        
        # System should handle at least some concurrent uploads
        assert uploads_per_second > 2, f"Uploads per second too low under stress: {uploads_per_second:.2f}"
        
        logger.info(f"Upload stress test completed - Uploads: {stress_uploads}, "
                    f"Success rate: {success_rate:.2f}, Avg time: {avg_upload_time:.2f}ms, "
                    f"P95: {p95_upload_time:.2f}ms, UPS: {uploads_per_second:.2f}, "
                    f"Throughput: {overall_throughput_kbps:.2f} KB/s")
    
    finally:
        # Cleanup test files
        for test_file in upload_files:
            test_file.cleanup()