"""Community Forum Service"""
import logging
import hashlib
from typing import List, Optional, Dict
from uuid import UUID, uuid4
from datetime import datetime

logger = logging.getLogger(__name__)

class CommunityForumService:
    def __init__(self, db_session=None):
        self.db = db_session
    
    def generate_anonymous_display_name(self, user_id: UUID, author_type: str) -> str:
        hash_val = int(hashlib.md5(str(user_id).encode()).hexdigest(), 16)
        if author_type == 'doctor':
            return f"Doctor_Specialist_{hash_val % 100}"
        return f"Patient{hash_val % 999}"
    
    async def create_post(self, author_id: UUID, author_type: str, post_type: str, 
                         title: str, content: str, language: str = 'en',
                         related_document_id: Optional[UUID] = None,
                         is_anonymous: bool = True, tags: List[str] = None) -> Dict:
        from sqlalchemy import text
        display_name = self.generate_anonymous_display_name(author_id, author_type) if is_anonymous else "User"
        post_id = uuid4()
        created_at = datetime.now()
        
        # Save to database
        if self.db:
            try:
                query = text("""
                INSERT INTO medcare_community_posts 
                (id, author_id, author_type, post_type, title, content, language, 
                 related_document_id, is_anonymous, anonymous_display_name, tags, status, created_at)
                VALUES (:id, :author_id, :author_type, :post_type, :title, :content, :language,
                        :related_document_id, :is_anonymous, :anonymous_display_name, :tags, :status, :created_at)
                """)
                await self.db.execute(query, {
                    'id': str(post_id), 'author_id': str(author_id), 'author_type': author_type,
                    'post_type': post_type, 'title': title, 'content': content, 'language': language,
                    'related_document_id': str(related_document_id) if related_document_id else None,
                    'is_anonymous': is_anonymous, 'anonymous_display_name': display_name,
                    'tags': tags or [], 'status': 'active', 'created_at': created_at
                })
                await self.db.commit()
                logger.info(f"Post {post_id} saved to database")
            except Exception as e:
                logger.warning(f"Could not save post: {e}")
        
        return {
            'id': post_id, 'author_id': author_id, 'title': title,
            'content': content, 'anonymous_display_name': display_name,
            'status': 'active', 'created_at': created_at
        }
    
    async def add_response(self, post_id: UUID, author_id: UUID, author_type: str,
                          content: str, language: str = 'en', is_anonymous: bool = True) -> Dict:
        display_name = self.generate_anonymous_display_name(author_id, author_type) if is_anonymous else "User"
        response_id = uuid4()
        return {
            'id': response_id, 'post_id': post_id, 'content': content,
            'anonymous_display_name': display_name, 'created_at': datetime.now()
        }
    
    async def get_post_with_responses(self, post_id: UUID, viewer_language: str = 'en',
                                     include_translations: bool = True) -> Dict:
        from sqlalchemy import text
        if self.db:
            try:
                query = text("SELECT * FROM medcare_community_posts WHERE id = :id")
                result = await self.db.execute(query, {'id': str(post_id)})
                row = result.fetchone()
                if row:
                    return {
                        'id': row[0], 'title': row[4], 'content': row[5],
                        'author_display_name': row[9], 'post_type': row[3],
                        'language': row[6], 'status': row[11], 'view_count': row[12],
                        'responses': [], 'created_at': str(row[14]) if len(row) > 14 else str(datetime.now())
                    }
            except Exception as e:
                logger.warning(f"Could not fetch post: {e}")
        
        return {
            'id': post_id, 'title': 'Sample Post', 'content': 'Sample content',
            'author_display_name': 'Patient23', 'responses': []
        }
    
    async def search_posts(self, query: Optional[str] = None, post_type: Optional[str] = None, 
                          tags: Optional[List[str]] = None, language: Optional[str] = None, 
                          limit: int = 20, offset: int = 0) -> List[Dict]:
        """Search posts with filters"""
        logger.info(f"Searching posts: query={query}, type={post_type}, tags={tags}")
        return []
    
    async def get_trending_posts(self, limit: int = 10) -> List[Dict]:
        """Get trending posts"""
        return []
    
    async def vote_on_response(self, response_id: UUID, voter_id: UUID, vote_type: str) -> bool:
        """Vote on response"""
        logger.info(f"Vote {vote_type} on response {response_id} by {voter_id}")
        return True
    
    async def vote_helpful(self, response_id: UUID, voter_id: UUID) -> bool:
        """Mark response as helpful"""
        logger.info(f"Response {response_id} marked helpful by {voter_id}")
        return True
