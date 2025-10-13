/**
 * Community Forum - Forum d'entraide santé
 */
import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { 
  MessageSquare, 
  Heart, 
  Send,
  Search,
  Plus,
  User,
  Clock,
  TrendingUp,
  Shield,
  AlertCircle
} from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface CommunityForumProps {
  userId: string;
}

export function CommunityForum({ userId }: CommunityForumProps) {
  const [activeTab, setActiveTab] = useState('browse');
  const [posts, setPosts] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [showNewPost, setShowNewPost] = useState(false);

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      const response = await fetch('/api/medcare/community/posts');
      const data = await response.json();
      setPosts(data.posts || mockPosts);
    } catch (error) {
      console.error('Error fetching posts:', error);
      setPosts(mockPosts);
    }
  };

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-6 w-6 text-blue-600" />
                Forum Santé Communautaire
              </CardTitle>
              <CardDescription>
                Partagez votre expérience et soutenez d'autres personnes
              </CardDescription>
            </div>
            <Button onClick={() => setShowNewPost(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Nouveau post
            </Button>
          </div>
        </CardHeader>
      </Card>

      {/* Règles et avertissement */}
      <Alert>
        <Shield className="h-4 w-4" />
        <AlertDescription>
          <strong>Règles de la communauté:</strong> Respectez la vie privée, soyez bienveillant, 
          et rappelez-vous que les conseils ici ne remplacent pas un avis médical professionnel.
        </AlertDescription>
      </Alert>

      {/* Recherche */}
      <div className="relative">
        <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
        <Input
          placeholder="Rechercher un sujet, symptôme, condition..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Navigation */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="browse">
            <TrendingUp className="h-4 w-4 mr-2" />
            Populaire
          </TabsTrigger>
          <TabsTrigger value="recent">
            <Clock className="h-4 w-4 mr-2" />
            Récent
          </TabsTrigger>
          <TabsTrigger value="my-posts">
            <User className="h-4 w-4 mr-2" />
            Mes posts
          </TabsTrigger>
        </TabsList>

        <TabsContent value="browse" className="space-y-4">
          <PostsList posts={posts} userId={userId} />
        </TabsContent>

        <TabsContent value="recent" className="space-y-4">
          <PostsList posts={[...posts].sort((a, b) => 
            new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
          )} userId={userId} />
        </TabsContent>

        <TabsContent value="my-posts" className="space-y-4">
          <PostsList posts={posts.filter(p => p.author_id === userId)} userId={userId} />
        </TabsContent>
      </Tabs>

      {/* Modal nouveau post */}
      {showNewPost && (
        <NewPostModal
          userId={userId}
          onClose={() => setShowNewPost(false)}
          onSubmit={async (post) => {
            // Soumettre le post
            try {
              await fetch('/api/medcare/community/posts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(post)
              });
              fetchPosts();
              setShowNewPost(false);
            } catch (error) {
              console.error('Error creating post:', error);
            }
          }}
        />
      )}
    </div>
  );
}

function PostsList({ posts, userId }: { posts: any[]; userId: string }) {
  const [likedPosts, setLikedPosts] = useState<Set<string>>(new Set());
  const [selectedPost, setSelectedPost] = useState<any>(null);

  const toggleLike = async (postId: string) => {
    const newLiked = new Set(likedPosts);
    if (newLiked.has(postId)) {
      newLiked.delete(postId);
    } else {
      newLiked.add(postId);
    }
    setLikedPosts(newLiked);

    // TODO: Appel API pour like
  };

  if (posts.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <MessageSquare className="h-12 w-12 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Aucun post trouvé
          </h3>
          <p className="text-gray-600">
            Soyez le premier à partager votre expérience
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      {posts.map((post) => (
        <Card key={post.id} className="hover:shadow-lg transition-shadow">
          <CardContent className="pt-6">
            <div className="space-y-4">
              {/* En-tête du post */}
              <div className="flex items-start gap-3">
                <Avatar>
                  <AvatarFallback className="bg-blue-100 text-blue-600">
                    {post.author_name?.[0] || 'A'}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{post.author_name || 'Anonyme'}</span>
                    {post.is_verified && (
                      <Badge variant="secondary" className="text-xs">
                        ✓ Vérifié
                      </Badge>
                    )}
                  </div>
                  <p className="text-xs text-gray-500">
                    Il y a {getTimeAgo(post.created_at)}
                  </p>
                </div>
                {post.tags && post.tags.length > 0 && (
                  <div className="flex gap-1">
                    {post.tags.slice(0, 2).map((tag: string, i: number) => (
                      <Badge key={i} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>

              {/* Titre */}
              <h3 className="font-semibold text-lg cursor-pointer hover:text-blue-600"
                  onClick={() => setSelectedPost(post)}>
                {post.title}
              </h3>

              {/* Contenu (aperçu) */}
              <p className="text-gray-700 line-clamp-3">
                {post.content}
              </p>

              {/* Actions */}
              <div className="flex items-center gap-4 pt-2 border-t">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => toggleLike(post.id)}
                  className={likedPosts.has(post.id) ? 'text-red-500' : ''}
                >
                  <Heart className={`h-4 w-4 mr-1 ${likedPosts.has(post.id) ? 'fill-current' : ''}`} />
                  {post.likes_count || 0}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setSelectedPost(post)}
                >
                  <MessageSquare className="h-4 w-4 mr-1" />
                  {post.replies_count || 0} réponses
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}

      {/* Modal détails post */}
      {selectedPost && (
        <PostDetailModal
          post={selectedPost}
          userId={userId}
          onClose={() => setSelectedPost(null)}
        />
      )}
    </>
  );
}

function NewPostModal({ userId, onClose, onSubmit }: any) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [isAnonymous, setIsAnonymous] = useState(true);

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <Card 
        className="max-w-2xl w-full"
        onClick={(e) => e.stopPropagation()}
      >
        <CardHeader>
          <CardTitle>Créer un nouveau post</CardTitle>
          <CardDescription>
            Partagez votre expérience ou posez une question
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Titre</label>
            <Input
              placeholder="Ex: Comment gérer le stress au quotidien?"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Votre message</label>
            <Textarea
              placeholder="Décrivez votre expérience, posez votre question..."
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows={6}
            />
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="anonymous"
              checked={isAnonymous}
              onChange={(e) => setIsAnonymous(e.target.checked)}
              className="rounded"
            />
            <label htmlFor="anonymous" className="text-sm">
              Publier anonymement
            </label>
          </div>

          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="text-xs">
              Ne partagez pas d'informations personnelles identifiables. 
              Ce forum est modéré mais reste public.
            </AlertDescription>
          </Alert>

          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={onClose}
              className="flex-1"
            >
              Annuler
            </Button>
            <Button
              onClick={() => {
                if (title.trim() && content.trim()) {
                  onSubmit({
                    user_id: userId,
                    title,
                    content,
                    is_anonymous: isAnonymous
                  });
                }
              }}
              disabled={!title.trim() || !content.trim()}
              className="flex-1"
            >
              <Send className="h-4 w-4 mr-2" />
              Publier
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function PostDetailModal({ post, userId, onClose }: any) {
  const [reply, setReply] = useState('');

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <Card 
        className="max-w-3xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <CardTitle>{post.title}</CardTitle>
              <div className="flex items-center gap-2 mt-2">
                <Avatar className="h-6 w-6">
                  <AvatarFallback className="text-xs">
                    {post.author_name?.[0] || 'A'}
                  </AvatarFallback>
                </Avatar>
                <span className="text-sm text-gray-600">
                  {post.author_name || 'Anonyme'} · {getTimeAgo(post.created_at)}
                </span>
              </div>
            </div>
            <Button variant="ghost" size="sm" onClick={onClose}>×</Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Contenu du post */}
          <div className="prose prose-sm max-w-none">
            <p className="text-gray-700 whitespace-pre-wrap">{post.content}</p>
          </div>

          {/* Zone de réponse */}
          <div className="border-t pt-4 space-y-3">
            <h4 className="font-medium">Répondre</h4>
            <Textarea
              placeholder="Partagez votre expérience ou vos conseils..."
              value={reply}
              onChange={(e) => setReply(e.target.value)}
              rows={3}
            />
            <Button size="sm" disabled={!reply.trim()}>
              <Send className="h-4 w-4 mr-2" />
              Envoyer
            </Button>
          </div>

          {/* Réponses */}
          {post.replies && post.replies.length > 0 && (
            <div className="space-y-4">
              <h4 className="font-medium">{post.replies.length} réponse(s)</h4>
              {post.replies.map((reply: any, index: number) => (
                <div key={index} className="bg-gray-50 p-4 rounded-lg">
                  <div className="flex items-start gap-2 mb-2">
                    <Avatar className="h-6 w-6">
                      <AvatarFallback className="text-xs">
                        {reply.author_name?.[0] || 'A'}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <span className="text-sm font-medium">{reply.author_name || 'Anonyme'}</span>
                      <span className="text-xs text-gray-500 ml-2">
                        {getTimeAgo(reply.created_at)}
                      </span>
                    </div>
                  </div>
                  <p className="text-sm text-gray-700">{reply.content}</p>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// Helpers
function getTimeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'quelques secondes';
  if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''}`;
  if (diffHours < 24) return `${diffHours} heure${diffHours > 1 ? 's' : ''}`;
  if (diffDays < 30) return `${diffDays} jour${diffDays > 1 ? 's' : ''}`;
  return `${Math.floor(diffDays / 30)} mois`;
}

// Mock data
const mockPosts = [
  {
    id: '1',
    author_name: 'Marie D.',
    author_id: 'user-1',
    title: 'Comment j\'ai géré mon anxiété sans médicaments',
    content: 'Bonjour à tous, je voulais partager mon expérience avec l\'anxiété. Après des années de lutte, j\'ai trouvé des techniques qui m\'aident vraiment...',
    likes_count: 24,
    replies_count: 8,
    tags: ['anxiété', 'bien-être'],
    created_at: new Date(Date.now() - 2 * 3600000).toISOString(),
    is_verified: true
  },
  {
    id: '2',
    author_name: 'Anonyme',
    author_id: 'user-2',
    title: 'Question sur les maux de tête persistants',
    content: 'Je souffre de maux de tête depuis 3 semaines. J\'ai consulté mais j\'aimerais savoir si d\'autres ont vécu ça...',
    likes_count: 12,
    replies_count: 15,
    tags: ['maux de tête', 'douleur'],
    created_at: new Date(Date.now() - 5 * 3600000).toISOString()
  }
];
