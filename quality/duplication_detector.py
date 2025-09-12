#!/usr/bin/env python3
"""
Duplication Detector - Ainflue Quality Platform
==============================================

Enterprise-grade code duplication detection and analysis system.
Demonstrates Lead Dev IA + Backend Senior + ML Engineer expertise.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import hashlib
import ast
import difflib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import yaml
import aiofiles
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import seaborn as sns
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
from itertools import combinations
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DuplicationType(Enum):
    """Types of code duplication"""
    EXACT_DUPLICATE = "exact_duplicate"  # Identical code blocks
    SIMILAR_STRUCTURE = "similar_structure"  # Similar AST structure
    COPY_PASTE = "copy_paste"  # Modified copy-paste with minor changes
    DESIGN_PATTERN = "design_pattern"  # Intentional pattern repetition
    BOILERPLATE = "boilerplate"  # Expected boilerplate code
    ALGORITHMIC = "algorithmic"  # Similar algorithms/logic


class DuplicationSeverity(Enum):
    """Severity levels of duplication"""
    CRITICAL = "critical"  # > 50 lines exact duplication
    HIGH = "high"  # > 20 lines or high similarity
    MEDIUM = "medium"  # > 10 lines or moderate similarity
    LOW = "low"  # > 5 lines or low similarity
    INFO = "info"  # Minor duplication or patterns


class AnalysisScope(Enum):
    """Scope of duplication analysis"""
    PROJECT_WIDE = "project_wide"
    MODULE_LEVEL = "module_level"
    PACKAGE_LEVEL = "package_level"
    CLASS_LEVEL = "class_level"
    FUNCTION_LEVEL = "function_level"


@dataclass
class CodeBlock:
    """Represents a block of code for duplication analysis"""
    file_path: str
    start_line: int
    end_line: int
    content: str
    content_hash: str
    normalized_content: str
    ast_structure: str = ""
    tokens: List[str] = field(default_factory=list)
    language: str = "python"
    function_name: str = ""
    class_name: str = ""
    complexity: int = 0


@dataclass
class DuplicationMatch:
    """Represents a duplication match between code blocks"""
    match_id: str
    duplication_type: DuplicationType
    severity: DuplicationSeverity
    similarity_score: float
    block1: CodeBlock
    block2: CodeBlock
    lines_duplicated: int
    exact_match: bool
    context_similarity: float = 0.0
    refactor_potential: bool = True
    estimated_effort_minutes: float = 0.0
    recommendations: List[str] = field(default_factory=list)


@dataclass
class DuplicationCluster:
    """Represents a cluster of related duplications"""
    cluster_id: str
    blocks: List[CodeBlock]
    cluster_type: DuplicationType
    total_lines: int
    files_affected: Set[str]
    refactoring_opportunity: str = ""
    estimated_savings_lines: int = 0
    priority_score: float = 0.0


@dataclass
class DuplicationReport:
    """Comprehensive duplication analysis report"""
    report_id: str
    generated_at: datetime
    project_path: str
    total_files_analyzed: int
    total_lines_analyzed: int
    total_duplications: int
    duplication_percentage: float
    duplicated_lines: int
    potential_savings_lines: int
    estimated_refactoring_hours: float
    matches: List[DuplicationMatch] = field(default_factory=list)
    clusters: List[DuplicationCluster] = field(default_factory=list)
    hotspot_files: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    refactoring_priorities: List[Dict[str, Any]] = field(default_factory=list)


class DuplicationDetector:
    """
    Enterprise code duplication detector
    
    Demonstrates expertise in:
    - Lead Dev IA: Advanced code analysis and refactoring recommendations
    - Backend Senior: Systematic code analysis and pattern recognition
    - ML Engineer: Similarity algorithms and clustering analysis
    """
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.supported_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.cs'}
        self.language_mapping = {
            '.py': 'python',
            '.js': 'javascript', 
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.cs': 'csharp'
        }
        
        # Analysis parameters
        self.min_block_size = 5  # Minimum lines for duplication consideration
        self.similarity_threshold = 0.8  # Minimum similarity for matching
        self.exact_match_threshold = 0.98  # Threshold for exact matches
        
        # Initialize directories
        self.reports_dir = Path("reports/duplication")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Analysis caches
        self.code_blocks_cache = {}
        self.similarity_cache = {}
        
        logger.info(f"DuplicationDetector initialized for {self.project_path}")
    
    async def analyze_duplications(self, 
                                 scope: AnalysisScope = AnalysisScope.PROJECT_WIDE,
                                 min_lines: int = None) -> DuplicationReport:
        """
        Perform comprehensive duplication analysis
        
        Lead Dev IA expertise: Advanced code analysis and architectural insights
        Backend expertise: Systematic file processing and data management
        ML expertise: Similarity analysis and clustering algorithms
        """
        logger.info(f"Starting duplication analysis with scope: {scope.value}")
        
        start_time = datetime.now()
        
        if min_lines:
            self.min_block_size = min_lines
        
        # Discover and analyze code files
        code_files = await self._discover_code_files()
        logger.info(f"Found {len(code_files)} code files to analyze")
        
        # Extract code blocks
        all_blocks = []
        total_lines = 0
        
        for file_path in code_files:
            try:
                blocks = await self._extract_code_blocks(file_path)
                all_blocks.extend(blocks)
                total_lines += len(file_path.read_text().splitlines())
            except Exception as e:
                logger.warning(f"Failed to analyze {file_path}: {e}")
        
        logger.info(f"Extracted {len(all_blocks)} code blocks")
        
        # Find duplication matches
        matches = await self._find_duplication_matches(all_blocks)
        logger.info(f"Found {len(matches)} duplication matches")
        
        # Cluster related duplications
        clusters = await self._cluster_duplications(matches)
        logger.info(f"Identified {len(clusters)} duplication clusters")
        
        # Identify hotspot files
        hotspot_files = await self._identify_hotspot_files(matches)
        
        # Calculate metrics
        duplicated_lines = sum(match.lines_duplicated for match in matches)
        duplication_percentage = (duplicated_lines / max(total_lines, 1)) * 100
        
        # Estimate potential savings
        potential_savings = await self._estimate_potential_savings(clusters)
        refactoring_hours = await self._estimate_refactoring_effort(matches, clusters)
        
        # Generate report
        report = DuplicationReport(
            report_id=f"dup_report_{start_time.strftime('%Y%m%d_%H%M%S')}",
            generated_at=start_time,
            project_path=str(self.project_path),
            total_files_analyzed=len(code_files),
            total_lines_analyzed=total_lines,
            total_duplications=len(matches),
            duplication_percentage=duplication_percentage,
            duplicated_lines=duplicated_lines,
            potential_savings_lines=potential_savings,
            estimated_refactoring_hours=refactoring_hours,
            matches=matches,
            clusters=clusters,
            hotspot_files=hotspot_files
        )
        
        # Generate recommendations
        await self._generate_recommendations(report)
        
        # Create refactoring priorities
        await self._prioritize_refactoring(report)
        
        # Save report
        await self._save_duplication_report(report)
        
        end_time = datetime.now()
        analysis_duration = (end_time - start_time).total_seconds()
        logger.info(f"Duplication analysis completed in {analysis_duration:.2f}s")
        
        return report
    
    async def _discover_code_files(self) -> List[Path]:
        """Discover code files for analysis (Backend expertise)"""
        code_files = []
        
        # Exclusion patterns
        exclude_patterns = [
            '**/node_modules/**',
            '**/venv/**',
            '**/env/**', 
            '**/__pycache__/**',
            '**/build/**',
            '**/dist/**',
            '**/target/**',
            '**/.git/**',
            '**/migrations/**',
            '**/test_*',
            '**/*_test.*',
            '**/tests/**'
        ]
        
        for extension in self.supported_extensions:
            pattern = f"**/*{extension}"
            files = list(self.project_path.rglob(pattern))
            
            # Filter out excluded files
            filtered_files = []
            for file_path in files:
                excluded = False
                for exclude_pattern in exclude_patterns:
                    if file_path.match(exclude_pattern):
                        excluded = True
                        break
                
                if not excluded and file_path.stat().st_size > 0:
                    filtered_files.append(file_path)
            
            code_files.extend(filtered_files)
        
        return sorted(code_files)
    
    async def _extract_code_blocks(self, file_path: Path) -> List[CodeBlock]:
        """
        Extract code blocks from file for analysis
        
        Lead Dev IA expertise: Advanced code parsing and AST analysis
        """
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            language = self.language_mapping.get(file_path.suffix, 'unknown')
            lines = content.splitlines()
            
            if language == 'python':
                return await self._extract_python_blocks(file_path, content, lines)
            else:
                return await self._extract_generic_blocks(file_path, content, lines, language)
                
        except Exception as e:
            logger.error(f"Error extracting blocks from {file_path}: {e}")
            return []
    
    async def _extract_python_blocks(self, file_path: Path, content: str, lines: List[str]) -> List[CodeBlock]:
        """Extract Python code blocks using AST analysis (Lead Dev IA expertise)"""
        blocks = []
        
        try:
            tree = ast.parse(content)
            
            class BlockExtractor(ast.NodeVisitor):
                def __init__(self):
                    self.blocks = []
                    self.current_class = ""
                
                def visit_FunctionDef(self, node):
                    self._extract_function_block(node)
                    self.generic_visit(node)
                
                def visit_ClassDef(self, node):
                    old_class = self.current_class
                    self.current_class = node.name
                    self._extract_class_block(node)
                    self.generic_visit(node)
                    self.current_class = old_class
                
                def _extract_function_block(self, node):
                    start_line = node.lineno - 1
                    end_line = getattr(node, 'end_lineno', start_line + 10) - 1
                    
                    if end_line - start_line >= self.min_block_size:
                        block_content = '\n'.join(lines[start_line:end_line + 1])
                        normalized_content = self._normalize_code(block_content)
                        
                        block = CodeBlock(
                            file_path=str(file_path),
                            start_line=start_line + 1,
                            end_line=end_line + 1,
                            content=block_content,
                            content_hash=hashlib.md5(block_content.encode()).hexdigest(),
                            normalized_content=normalized_content,
                            ast_structure=ast.dump(node, annotate_fields=False),
                            tokens=self._tokenize_code(block_content),
                            language='python',
                            function_name=node.name,
                            class_name=self.current_class,
                            complexity=self._calculate_complexity(node)
                        )
                        self.blocks.append(block)
                
                def _extract_class_block(self, node):
                    start_line = node.lineno - 1
                    end_line = getattr(node, 'end_lineno', start_line + 20) - 1
                    
                    if end_line - start_line >= self.min_block_size:
                        block_content = '\n'.join(lines[start_line:end_line + 1])
                        normalized_content = self._normalize_code(block_content)
                        
                        block = CodeBlock(
                            file_path=str(file_path),
                            start_line=start_line + 1,
                            end_line=end_line + 1,
                            content=block_content,
                            content_hash=hashlib.md5(block_content.encode()).hexdigest(),
                            normalized_content=normalized_content,
                            ast_structure=ast.dump(node, annotate_fields=False),
                            tokens=self._tokenize_code(block_content),
                            language='python',
                            function_name="",
                            class_name=node.name,
                            complexity=len(node.body)
                        )
                        self.blocks.append(block)
            
            extractor = BlockExtractor()
            extractor.visit(tree)
            blocks.extend(extractor.blocks)
            
        except SyntaxError:
            logger.warning(f"Syntax error in {file_path}, using generic extraction")
            blocks.extend(await self._extract_generic_blocks(file_path, content, lines, 'python'))
        
        # Also extract method-level blocks
        blocks.extend(await self._extract_sliding_window_blocks(file_path, lines, 'python'))
        
        return blocks
    
    async def _extract_generic_blocks(self, file_path: Path, content: str, 
                                     lines: List[str], language: str) -> List[CodeBlock]:
        """Extract blocks from non-Python files (Backend expertise)"""
        blocks = []
        
        # Use sliding window approach for generic languages
        blocks.extend(await self._extract_sliding_window_blocks(file_path, lines, language))
        
        # Extract function-like patterns
        blocks.extend(await self._extract_function_patterns(file_path, lines, language))
        
        return blocks
    
    async def _extract_sliding_window_blocks(self, file_path: Path, 
                                           lines: List[str], language: str) -> List[CodeBlock]:
        """Extract blocks using sliding window approach"""
        blocks = []
        window_sizes = [10, 15, 20, 30]  # Different block sizes to check
        
        for window_size in window_sizes:
            if window_size < self.min_block_size:
                continue
                
            for i in range(len(lines) - window_size + 1):
                block_lines = lines[i:i + window_size]
                
                # Skip blocks with too many empty/comment lines
                non_empty_lines = [line for line in block_lines if line.strip() and not line.strip().startswith('#')]
                if len(non_empty_lines) < window_size * 0.6:  # At least 60% non-empty
                    continue
                
                block_content = '\n'.join(block_lines)
                normalized_content = self._normalize_code(block_content)
                
                block = CodeBlock(
                    file_path=str(file_path),
                    start_line=i + 1,
                    end_line=i + window_size,
                    content=block_content,
                    content_hash=hashlib.md5(block_content.encode()).hexdigest(),
                    normalized_content=normalized_content,
                    tokens=self._tokenize_code(block_content),
                    language=language
                )
                blocks.append(block)
        
        return blocks
    
    async def _extract_function_patterns(self, file_path: Path, 
                                       lines: List[str], language: str) -> List[CodeBlock]:
        """Extract function-like patterns for various languages"""
        blocks = []
        
        function_patterns = {
            'javascript': [r'^\s*function\s+\w+', r'^\s*const\s+\w+\s*=\s*\(', r'^\s*\w+\s*:\s*function'],
            'typescript': [r'^\s*function\s+\w+', r'^\s*const\s+\w+\s*=\s*\(', r'^\s*\w+\s*\(.*\)\s*:\s*\w+'],
            'java': [r'^\s*(public|private|protected)?\s*(static\s+)?\w+\s+\w+\s*\('],
            'cpp': [r'^\s*\w+\s+\w+\s*\(', r'^\s*(public|private|protected)\s*:'],
            'csharp': [r'^\s*(public|private|protected)?\s*(static\s+)?\w+\s+\w+\s*\(']
        }
        
        patterns = function_patterns.get(language, [])
        if not patterns:
            return blocks
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check if line matches function pattern
            for pattern in patterns:
                if re.search(pattern, line):
                    # Extract function block
                    start_line = i
                    brace_count = 0
                    in_function = False
                    
                    for j in range(i, min(i + 100, len(lines))):  # Look ahead max 100 lines
                        current_line = lines[j]
                        
                        if '{' in current_line:
                            brace_count += current_line.count('{')
                            in_function = True
                        if '}' in current_line:
                            brace_count -= current_line.count('}')
                        
                        if in_function and brace_count == 0:
                            end_line = j
                            
                            if end_line - start_line >= self.min_block_size:
                                block_lines = lines[start_line:end_line + 1]
                                block_content = '\n'.join(block_lines)
                                normalized_content = self._normalize_code(block_content)
                                
                                # Extract function name
                                func_name = self._extract_function_name(line, language)
                                
                                block = CodeBlock(
                                    file_path=str(file_path),
                                    start_line=start_line + 1,
                                    end_line=end_line + 1,
                                    content=block_content,
                                    content_hash=hashlib.md5(block_content.encode()).hexdigest(),
                                    normalized_content=normalized_content,
                                    tokens=self._tokenize_code(block_content),
                                    language=language,
                                    function_name=func_name
                                )
                                blocks.append(block)
                            
                            i = j  # Move to end of function
                            break
                    break
            i += 1
        
        return blocks
    
    def _normalize_code(self, content: str) -> str:
        """
        Normalize code for better comparison
        
        ML expertise: Text preprocessing and normalization
        """
        # Remove comments
        lines = content.split('\n')
        normalized_lines = []
        
        for line in lines:
            # Remove comments (basic approach)
            if '//' in line:
                line = line[:line.index('//')]
            if '#' in line and not line.strip().startswith('#'):
                line = line[:line.index('#')]
            
            # Normalize whitespace
            line = ' '.join(line.split())
            
            # Remove empty lines
            if line.strip():
                normalized_lines.append(line.lower())
        
        return '\n'.join(normalized_lines)
    
    def _tokenize_code(self, content: str) -> List[str]:
        """Tokenize code for analysis (ML expertise)"""
        # Simple tokenization - split by common delimiters
        tokens = re.findall(r'\w+', content.lower())
        return [token for token in tokens if len(token) > 2]  # Filter short tokens
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of AST node"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.With, ast.Try, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _extract_function_name(self, line: str, language: str) -> str:
        """Extract function name from function declaration line"""
        patterns = {
            'javascript': r'function\s+(\w+)',
            'typescript': r'function\s+(\w+)',
            'java': r'\w+\s+(\w+)\s*\(',
            'cpp': r'\w+\s+(\w+)\s*\(',
            'csharp': r'\w+\s+(\w+)\s*\('
        }
        
        pattern = patterns.get(language, r'(\w+)')
        match = re.search(pattern, line)
        return match.group(1) if match else ""
    
    async def _find_duplication_matches(self, blocks: List[CodeBlock]) -> List[DuplicationMatch]:
        """
        Find duplication matches between code blocks
        
        ML expertise: Similarity analysis and clustering
        Lead Dev IA expertise: Code pattern recognition
        """
        matches = []
        
        # Group blocks by hash for exact matches
        hash_groups = defaultdict(list)
        for block in blocks:
            hash_groups[block.content_hash].append(block)
        
        # Find exact duplications
        for blocks_with_same_hash in hash_groups.values():
            if len(blocks_with_same_hash) > 1:
                # Create matches for all pairs
                for i, block1 in enumerate(blocks_with_same_hash):
                    for block2 in blocks_with_same_hash[i + 1:]:
                        match = DuplicationMatch(
                            match_id=f"exact_{block1.content_hash}_{i}",
                            duplication_type=DuplicationType.EXACT_DUPLICATE,
                            severity=self._calculate_severity(block1, block2, 1.0),
                            similarity_score=1.0,
                            block1=block1,
                            block2=block2,
                            lines_duplicated=block1.end_line - block1.start_line + 1,
                            exact_match=True
                        )
                        matches.append(match)
        
        # Find similar blocks using various similarity measures
        similar_matches = await self._find_similar_blocks(blocks)
        matches.extend(similar_matches)
        
        # Add recommendations to matches
        for match in matches:
            match.recommendations = await self._generate_match_recommendations(match)
            match.estimated_effort_minutes = await self._estimate_refactoring_effort_match(match)
        
        return matches
    
    async def _find_similar_blocks(self, blocks: List[CodeBlock]) -> List[DuplicationMatch]:
        """
        Find similar code blocks using ML similarity analysis
        
        ML expertise: Text similarity and vectorization
        """
        matches = []
        
        if len(blocks) < 2:
            return matches
        
        # Prepare texts for vectorization
        texts = [block.normalized_content for block in blocks]
        
        try:
            # Use TF-IDF vectorization for similarity analysis
            vectorizer = TfidfVectorizer(
                stop_words='english',
                ngram_range=(1, 3),
                max_features=1000,
                min_df=1,
                max_df=0.8
            )
            
            tfidf_matrix = vectorizer.fit_transform(texts)
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # Find similar pairs
            for i in range(len(blocks)):
                for j in range(i + 1, len(blocks)):
                    similarity = similarity_matrix[i][j]
                    
                    if similarity >= self.similarity_threshold:
                        # Calculate additional similarity measures
                        token_similarity = self._calculate_token_similarity(blocks[i], blocks[j])
                        structural_similarity = self._calculate_structural_similarity(blocks[i], blocks[j])
                        
                        # Combined similarity score
                        combined_similarity = (similarity + token_similarity + structural_similarity) / 3
                        
                        if combined_similarity >= self.similarity_threshold:
                            duplication_type = self._classify_duplication_type(blocks[i], blocks[j], combined_similarity)
                            
                            match = DuplicationMatch(
                                match_id=f"similar_{i}_{j}",
                                duplication_type=duplication_type,
                                severity=self._calculate_severity(blocks[i], blocks[j], combined_similarity),
                                similarity_score=combined_similarity,
                                block1=blocks[i],
                                block2=blocks[j],
                                lines_duplicated=min(
                                    blocks[i].end_line - blocks[i].start_line + 1,
                                    blocks[j].end_line - blocks[j].start_line + 1
                                ),
                                exact_match=False,
                                context_similarity=structural_similarity
                            )
                            matches.append(match)
            
        except Exception as e:
            logger.warning(f"TF-IDF similarity analysis failed: {e}")
            # Fallback to simple token-based similarity
            matches.extend(await self._fallback_similarity_analysis(blocks))
        
        return matches
    
    def _calculate_token_similarity(self, block1: CodeBlock, block2: CodeBlock) -> float:
        """Calculate token-based similarity between blocks"""
        tokens1 = set(block1.tokens)
        tokens2 = set(block2.tokens)
        
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_structural_similarity(self, block1: CodeBlock, block2: CodeBlock) -> float:
        """Calculate structural similarity between blocks"""
        if block1.language != 'python' or block2.language != 'python':
            return 0.0
        
        if not block1.ast_structure or not block2.ast_structure:
            return 0.0
        
        # Simple structural similarity based on AST string comparison
        structure1 = re.sub(r'\w+', 'IDENTIFIER', block1.ast_structure)
        structure2 = re.sub(r'\w+', 'IDENTIFIER', block2.ast_structure)
        
        # Calculate sequence similarity
        similarity = difflib.SequenceMatcher(None, structure1, structure2).ratio()
        return similarity
    
    def _classify_duplication_type(self, block1: CodeBlock, block2: CodeBlock, 
                                 similarity: float) -> DuplicationType:
        """Classify the type of duplication based on analysis"""
        if similarity >= self.exact_match_threshold:
            return DuplicationType.EXACT_DUPLICATE
        
        # Check for copy-paste patterns (high token similarity, different context)
        token_sim = self._calculate_token_similarity(block1, block2)
        if token_sim > 0.9 and similarity > 0.85:
            return DuplicationType.COPY_PASTE
        
        # Check for structural similarity
        structural_sim = self._calculate_structural_similarity(block1, block2)
        if structural_sim > 0.8:
            return DuplicationType.SIMILAR_STRUCTURE
        
        # Check for algorithmic similarity
        if (block1.function_name and block2.function_name and 
            'algorithm' in block1.function_name.lower() or 'sort' in block1.function_name.lower()):
            return DuplicationType.ALGORITHMIC
        
        # Check for boilerplate patterns
        if (len(block1.tokens) < 20 and len(block2.tokens) < 20 and
            any(keyword in ' '.join(block1.tokens) for keyword in ['init', 'setup', 'config'])):
            return DuplicationType.BOILERPLATE
        
        return DuplicationType.SIMILAR_STRUCTURE
    
    def _calculate_severity(self, block1: CodeBlock, block2: CodeBlock, similarity: float) -> DuplicationSeverity:
        """Calculate duplication severity"""
        lines_count = max(
            block1.end_line - block1.start_line + 1,
            block2.end_line - block2.start_line + 1
        )
        
        # Severity based on line count and similarity
        if similarity >= 0.95 and lines_count >= 50:
            return DuplicationSeverity.CRITICAL
        elif similarity >= 0.9 and lines_count >= 20:
            return DuplicationSeverity.HIGH
        elif similarity >= 0.85 and lines_count >= 10:
            return DuplicationSeverity.MEDIUM
        elif similarity >= 0.8 and lines_count >= 5:
            return DuplicationSeverity.LOW
        else:
            return DuplicationSeverity.INFO
    
    async def _fallback_similarity_analysis(self, blocks: List[CodeBlock]) -> List[DuplicationMatch]:
        """Fallback similarity analysis using simple methods"""
        matches = []
        
        for i, block1 in enumerate(blocks):
            for j, block2 in enumerate(blocks[i + 1:], i + 1):
                # Simple line-by-line comparison
                lines1 = block1.normalized_content.split('\n')
                lines2 = block2.normalized_content.split('\n')
                
                similarity = difflib.SequenceMatcher(None, lines1, lines2).ratio()
                
                if similarity >= self.similarity_threshold:
                    match = DuplicationMatch(
                        match_id=f"fallback_{i}_{j}",
                        duplication_type=DuplicationType.SIMILAR_STRUCTURE,
                        severity=self._calculate_severity(block1, block2, similarity),
                        similarity_score=similarity,
                        block1=block1,
                        block2=block2,
                        lines_duplicated=min(len(lines1), len(lines2)),
                        exact_match=False
                    )
                    matches.append(match)
        
        return matches
    
    async def _cluster_duplications(self, matches: List[DuplicationMatch]) -> List[DuplicationCluster]:
        """
        Cluster related duplications for better analysis
        
        ML expertise: Clustering and graph analysis
        """
        if not matches:
            return []
        
        # Create graph of duplicate relationships
        G = nx.Graph()
        
        # Add nodes (code blocks)
        block_to_id = {}
        for i, match in enumerate(matches):
            block1_id = f"{match.block1.file_path}:{match.block1.start_line}"
            block2_id = f"{match.block2.file_path}:{match.block2.start_line}"
            
            block_to_id[block1_id] = match.block1
            block_to_id[block2_id] = match.block2
            
            G.add_node(block1_id, block=match.block1)
            G.add_node(block2_id, block=match.block2)
            G.add_edge(block1_id, block2_id, 
                      similarity=match.similarity_score,
                      match=match)
        
        # Find connected components (clusters)
        clusters = []
        for i, component in enumerate(nx.connected_components(G)):
            if len(component) < 2:
                continue
            
            blocks = [block_to_id[node_id] for node_id in component]
            files_affected = set(block.file_path for block in blocks)
            total_lines = sum(block.end_line - block.start_line + 1 for block in blocks)
            
            # Determine cluster type
            cluster_matches = [G[u][v]['match'] for u, v in G.subgraph(component).edges()]
            most_common_type = max(set(match.duplication_type for match in cluster_matches),
                                 key=lambda x: sum(1 for match in cluster_matches if match.duplication_type == x))
            
            # Calculate potential savings
            savings = await self._calculate_cluster_savings(blocks)
            priority_score = self._calculate_cluster_priority(blocks, cluster_matches)
            
            cluster = DuplicationCluster(
                cluster_id=f"cluster_{i}",
                blocks=blocks,
                cluster_type=most_common_type,
                total_lines=total_lines,
                files_affected=files_affected,
                estimated_savings_lines=savings,
                priority_score=priority_score,
                refactoring_opportunity=await self._suggest_refactoring_approach(blocks, most_common_type)
            )
            clusters.append(cluster)
        
        # Sort clusters by priority
        clusters.sort(key=lambda x: x.priority_score, reverse=True)
        
        return clusters
    
    async def _calculate_cluster_savings(self, blocks: List[CodeBlock]) -> int:
        """Calculate potential line savings from refactoring cluster"""
        if len(blocks) < 2:
            return 0
        
        # Estimate savings: keep one instance, remove others
        total_lines = sum(block.end_line - block.start_line + 1 for block in blocks)
        average_lines = total_lines // len(blocks)
        
        # Account for refactoring overhead (function extraction, etc.)
        overhead = 5  # Estimated overhead lines
        savings = total_lines - average_lines - overhead
        
        return max(0, savings)
    
    def _calculate_cluster_priority(self, blocks: List[CodeBlock], matches: List[DuplicationMatch]) -> float:
        """Calculate priority score for cluster refactoring"""
        if not blocks or not matches:
            return 0.0
        
        # Factors for priority calculation
        num_files = len(set(block.file_path for block in blocks))
        total_lines = sum(block.end_line - block.start_line + 1 for block in blocks)
        avg_similarity = sum(match.similarity_score for match in matches) / len(matches)
        severity_score = sum(
            {'critical': 5, 'high': 4, 'medium': 3, 'low': 2, 'info': 1}[match.severity.value] 
            for match in matches
        ) / len(matches)
        
        # Weighted priority score
        priority = (
            num_files * 2.0 +  # More files affected = higher priority
            (total_lines / 50) * 1.5 +  # More lines = higher priority  
            avg_similarity * 2.0 +  # Higher similarity = higher priority
            severity_score * 1.0  # Severity factor
        )
        
        return min(10.0, priority)  # Cap at 10
    
    async def _suggest_refactoring_approach(self, blocks: List[CodeBlock], 
                                          cluster_type: DuplicationType) -> str:
        """Suggest refactoring approach for cluster"""
        approaches = {
            DuplicationType.EXACT_DUPLICATE: "Extract common code into shared function/module",
            DuplicationType.COPY_PASTE: "Refactor into parameterized function with common interface",
            DuplicationType.SIMILAR_STRUCTURE: "Create template method or strategy pattern",
            DuplicationType.ALGORITHMIC: "Extract algorithm into utility class with variants",
            DuplicationType.BOILERPLATE: "Create code generator or template system",
            DuplicationType.DESIGN_PATTERN: "Validate pattern implementation consistency"
        }
        
        base_approach = approaches.get(cluster_type, "Consider refactoring into shared component")
        
        # Add specific suggestions based on context
        function_names = [block.function_name for block in blocks if block.function_name]
        if len(set(function_names)) > 1:
            base_approach += " | Consider creating function family with shared base"
        
        files_count = len(set(block.file_path for block in blocks))
        if files_count > 3:
            base_approach += " | High impact: affects multiple modules"
        
        return base_approach
    
    async def _identify_hotspot_files(self, matches: List[DuplicationMatch]) -> List[Dict[str, Any]]:
        """Identify files with high duplication concentration"""
        file_stats = defaultdict(lambda: {
            'duplications': 0,
            'total_lines_duplicated': 0,
            'severity_scores': [],
            'matches': []
        })
        
        for match in matches:
            for block in [match.block1, match.block2]:
                file_path = block.file_path
                file_stats[file_path]['duplications'] += 1
                file_stats[file_path]['total_lines_duplicated'] += match.lines_duplicated
                file_stats[file_path]['severity_scores'].append(
                    {'critical': 5, 'high': 4, 'medium': 3, 'low': 2, 'info': 1}[match.severity.value]
                )
                file_stats[file_path]['matches'].append(match)
        
        hotspots = []
        for file_path, stats in file_stats.items():
            if stats['duplications'] >= 3:  # Files with 3+ duplications
                avg_severity = sum(stats['severity_scores']) / len(stats['severity_scores'])
                
                hotspot = {
                    'file_path': file_path,
                    'duplications_count': stats['duplications'],
                    'total_lines_duplicated': stats['total_lines_duplicated'],
                    'average_severity': avg_severity,
                    'severity_level': 'high' if avg_severity >= 4 else 'medium' if avg_severity >= 3 else 'low',
                    'refactoring_priority': avg_severity * stats['duplications']
                }
                hotspots.append(hotspot)
        
        # Sort by refactoring priority
        hotspots.sort(key=lambda x: x['refactoring_priority'], reverse=True)
        
        return hotspots[:10]  # Top 10 hotspots
    
    async def _estimate_potential_savings(self, clusters: List[DuplicationCluster]) -> int:
        """Estimate total potential line savings"""
        return sum(cluster.estimated_savings_lines for cluster in clusters)
    
    async def _estimate_refactoring_effort(self, matches: List[DuplicationMatch], 
                                         clusters: List[DuplicationCluster]) -> float:
        """Estimate total refactoring effort in hours"""
        # Base effort for individual matches
        match_effort = sum(match.estimated_effort_minutes for match in matches) / 60
        
        # Additional effort for cluster refactoring
        cluster_effort = 0
        for cluster in clusters:
            complexity_factor = len(cluster.files_affected) * 0.5
            size_factor = cluster.total_lines / 100
            cluster_effort += (complexity_factor + size_factor) * 2  # 2 hours base per cluster
        
        return match_effort + cluster_effort
    
    async def _generate_match_recommendations(self, match: DuplicationMatch) -> List[str]:
        """Generate specific recommendations for duplication match"""
        recommendations = []
        
        if match.duplication_type == DuplicationType.EXACT_DUPLICATE:
            recommendations.append("Extract identical code into shared function")
            recommendations.append("Consider creating utility module for common functionality")
        elif match.duplication_type == DuplicationType.COPY_PASTE:
            recommendations.append("Refactor copy-paste code into parameterized function")
            recommendations.append("Add unit tests to prevent future regressions")
        elif match.duplication_type == DuplicationType.SIMILAR_STRUCTURE:
            recommendations.append("Consider template method or strategy pattern")
            recommendations.append("Analyze for potential interface abstraction")
        
        if match.severity in [DuplicationSeverity.CRITICAL, DuplicationSeverity.HIGH]:
            recommendations.append("HIGH PRIORITY: Address immediately to reduce technical debt")
        
        if match.block1.file_path != match.block2.file_path:
            recommendations.append("Cross-file duplication: consider shared module")
        
        return recommendations
    
    async def _estimate_refactoring_effort_match(self, match: DuplicationMatch) -> float:
        """Estimate refactoring effort for single match in minutes"""
        base_effort = {
            DuplicationSeverity.CRITICAL: 60,
            DuplicationSeverity.HIGH: 30,
            DuplicationSeverity.MEDIUM: 15,
            DuplicationSeverity.LOW: 10,
            DuplicationSeverity.INFO: 5
        }
        
        effort = base_effort.get(match.severity, 15)
        
        # Adjust based on complexity factors
        if match.block1.file_path != match.block2.file_path:
            effort *= 1.5  # Cross-file refactoring is more complex
        
        if match.duplication_type == DuplicationType.SIMILAR_STRUCTURE:
            effort *= 1.3  # Structural refactoring requires more thought
        
        return effort
    
    async def _generate_recommendations(self, report: DuplicationReport):
        """Generate comprehensive recommendations (Lead Dev IA expertise)"""
        recommendations = []
        
        # Overall recommendations
        if report.duplication_percentage > 15:
            recommendations.append("CRITICAL: High duplication rate (>15%) requires immediate attention")
            recommendations.append("Consider architecture review to identify systemic issues")
        elif report.duplication_percentage > 10:
            recommendations.append("WARNING: Elevated duplication rate (>10%) needs improvement")
        
        # Cluster-based recommendations
        if report.clusters:
            high_priority_clusters = [c for c in report.clusters if c.priority_score >= 7]
            if high_priority_clusters:
                recommendations.append(f"Focus on {len(high_priority_clusters)} high-priority duplication clusters")
        
        # File-based recommendations
        if report.hotspot_files:
            high_priority_files = [f for f in report.hotspot_files if f['severity_level'] == 'high']
            if high_priority_files:
                recommendations.append(f"Refactor {len(high_priority_files)} hotspot files with high duplication")
        
        # Effort-based recommendations
        if report.estimated_refactoring_hours > 40:
            recommendations.append("Consider phased refactoring approach due to high effort required")
            recommendations.append("Prioritize refactoring based on business impact and file usage frequency")
        
        # Savings-based recommendations
        if report.potential_savings_lines > 1000:
            recommendations.append(f"Significant savings opportunity: {report.potential_savings_lines} lines could be reduced")
        
        report.recommendations = recommendations
    
    async def _prioritize_refactoring(self, report: DuplicationReport):
        """Create refactoring priority list"""
        priorities = []
        
        # High-priority clusters
        for cluster in report.clusters[:5]:  # Top 5 clusters
            priority = {
                'type': 'cluster',
                'id': cluster.cluster_id,
                'description': f"Refactor {len(cluster.blocks)} duplicate blocks across {len(cluster.files_affected)} files",
                'priority_score': cluster.priority_score,
                'estimated_effort_hours': cluster.total_lines / 50,  # Rough estimate
                'potential_savings': cluster.estimated_savings_lines,
                'approach': cluster.refactoring_opportunity
            }
            priorities.append(priority)
        
        # High-severity individual matches
        high_severity_matches = [m for m in report.matches if m.severity in [DuplicationSeverity.CRITICAL, DuplicationSeverity.HIGH]]
        for match in high_severity_matches[:10]:  # Top 10 matches
            priority = {
                'type': 'match',
                'id': match.match_id,
                'description': f"Refactor {match.duplication_type.value} between {match.block1.file_path} and {match.block2.file_path}",
                'priority_score': 5 if match.severity == DuplicationSeverity.CRITICAL else 4,
                'estimated_effort_hours': match.estimated_effort_minutes / 60,
                'potential_savings': match.lines_duplicated,
                'approach': '; '.join(match.recommendations)
            }
            priorities.append(priority)
        
        # Sort by priority score
        priorities.sort(key=lambda x: x['priority_score'], reverse=True)
        
        report.refactoring_priorities = priorities[:15]  # Top 15 priorities
    
    async def _save_duplication_report(self, report: DuplicationReport):
        """Save duplication report to file (Backend expertise)"""
        timestamp = report.generated_at.strftime("%Y%m%d_%H%M%S")
        filename = f"duplication_report_{timestamp}.json"
        filepath = self.reports_dir / filename
        
        # Convert report to dict for JSON serialization
        report_dict = {
            'report_id': report.report_id,
            'generated_at': report.generated_at.isoformat(),
            'project_path': report.project_path,
            'total_files_analyzed': report.total_files_analyzed,
            'total_lines_analyzed': report.total_lines_analyzed,
            'total_duplications': report.total_duplications,
            'duplication_percentage': report.duplication_percentage,
            'duplicated_lines': report.duplicated_lines,
            'potential_savings_lines': report.potential_savings_lines,
            'estimated_refactoring_hours': report.estimated_refactoring_hours,
            'recommendations': report.recommendations,
            'refactoring_priorities': report.refactoring_priorities,
            'hotspot_files': report.hotspot_files,
            'matches_summary': {
                'total_matches': len(report.matches),
                'exact_duplicates': len([m for m in report.matches if m.duplication_type == DuplicationType.EXACT_DUPLICATE]),
                'similar_blocks': len([m for m in report.matches if m.duplication_type == DuplicationType.SIMILAR_STRUCTURE]),
                'copy_paste': len([m for m in report.matches if m.duplication_type == DuplicationType.COPY_PASTE])
            },
            'clusters_summary': {
                'total_clusters': len(report.clusters),
                'high_priority_clusters': len([c for c in report.clusters if c.priority_score >= 7]),
                'files_in_clusters': len(set().union(*[c.files_affected for c in report.clusters]))
            }
        }
        
        async with aiofiles.open(filepath, 'w') as f:
            await f.write(json.dumps(report_dict, indent=2))
        
        logger.info(f"Duplication report saved to: {filepath}")


# Global instance
duplication_detector = DuplicationDetector()


async def analyze_project_duplications(project_path: str = ".", 
                                     min_lines: int = 5) -> DuplicationReport:
    """Convenience function to analyze duplications"""
    detector = DuplicationDetector(project_path)
    return await detector.analyze_duplications(AnalysisScope.PROJECT_WIDE, min_lines)


async def find_exact_duplicates(project_path: str = ".") -> List[DuplicationMatch]:
    """Quick function to find only exact duplicates"""
    report = await analyze_project_duplications(project_path)
    return [match for match in report.matches if match.exact_match]


if __name__ == "__main__":
    # Example usage
    async def main():
        # Analyze duplications in current project
        report = await analyze_project_duplications(".", min_lines=10)
        
        print(f"Duplication Analysis Report: {report.report_id}")
        print(f"Files Analyzed: {report.total_files_analyzed}")
        print(f"Duplication Percentage: {report.duplication_percentage:.2f}%")
        print(f"Total Duplications: {report.total_duplications}")
        print(f"Potential Savings: {report.potential_savings_lines} lines")
        print(f"Estimated Effort: {report.estimated_refactoring_hours:.1f} hours")
        
        if report.recommendations:
            print("\nRecommendations:")
            for rec in report.recommendations[:5]:
                print(f"  - {rec}")
        
        if report.clusters:
            print(f"\nTop 3 Duplication Clusters:")
            for cluster in report.clusters[:3]:
                print(f"  - {cluster.cluster_id}: {len(cluster.blocks)} blocks, {cluster.total_lines} lines")
    
    asyncio.run(main())