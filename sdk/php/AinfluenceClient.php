<?php

declare(strict_types=1);

namespace IA Chérie\SDK;

use GuzzleHttp\Client as HttpClient;
use GuzzleHttp\Exception\GuzzleException;
use GuzzleHttp\Psr7\MultipartStream;
use Psr\Http\Message\ResponseInterface;
use React\Socket\Connector;
use React\Socket\ConnectorInterface;
use React\Stream\WritableResourceStream;
use Ratchet\Client\WebSocket;
use Ratchet\Client\Connector as WsConnector;
use Monolog\Logger;
use Monolog\Handler\StreamHandler;
use Firebase\JWT\JWT;
use Firebase\JWT\Key;

/**
 * IA Chérie PHP SDK - Enterprise Server-Side Client
 * 
 * Provides secure, high-performance access to IA Chérie Platform APIs for PHP applications.
 * 
 * Features:
 * - JWT Authentication with automatic refresh
 * - Async WebSocket communication (ReactPHP)
 * - Multi-format content processing
 * - Advanced security with encrypted storage
 * - Performance monitoring and analytics
 * - PSR-7/PSR-18 compatible HTTP client
 * - Enterprise logging and error handling
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @version 4.0.0
 * @since 2025-01-01
 * 
 * @copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 */
class AinfluenceClient
{
    private const VERSION = '4.0.0';
    private const TOKEN_EXPIRY_BUFFER = 300; // 5 minutes

    private AinfluenceConfiguration $config;
    private HttpClient $httpClient;
    private Logger $logger;
    private ?string $accessToken = null;
    private ?string $refreshToken = null;
    private ?int $tokenExpiry = null;
    private array $metrics = [];
    
    // WebSocket connection (ReactPHP)
    private $webSocketConnection = null;
    private array $eventListeners = [];
    
    // Analytics and monitoring
    private AnalyticsManager $analyticsManager;
    private SecurityManager $securityManager;
    private CacheManager $cacheManager;

    public function __construct(AinfluenceConfiguration $config)
    {
        $this->config = $config;
        $this->initializeComponents();
    }

    /**
     * Initialize SDK components
     */
    private function initializeComponents(): void
    {
        // Initialize HTTP client with security headers
        $this->httpClient = new HttpClient([
            'base_uri' => $this->config->getBaseUrl(),
            'timeout' => $this->config->getTimeout(),
            'connect_timeout' => 10.0,
            'headers' => [
                'User-Agent' => "IA Chérie-PHP-SDK/" . self::VERSION,
                'X-Client-Version' => self::VERSION,
                'X-Platform' => 'PHP',
                'Content-Type' => 'application/json',
                'Accept' => 'application/json',
            ],
            'verify' => $this->config->isVerifySsl(),
            'http_errors' => false,
        ]);

        // Initialize logger
        $this->logger = new Logger('iacherie-sdk');
        $this->logger->pushHandler(new StreamHandler($this->config->getLogPath(), Logger::INFO));

        // Initialize managers
        $this->analyticsManager = new AnalyticsManager($this->config, $this->logger);
        $this->securityManager = new SecurityManager($this->config);
        $this->cacheManager = new CacheManager($this->config);

        $this->logger->info('IA Chérie SDK initialized', [
            'version' => self::VERSION,
            'base_url' => $this->config->getBaseUrl(),
        ]);
    }

    /**
     * Authenticate with the IA Chérie platform
     */
    public function authenticate(string $email, string $password): AuthResult
    {
        try {
            $credentials = [
                'email' => $email,
                'password' => $password,
                'client_version' => self::VERSION,
            ];

            $response = $this->httpClient->post('/auth/login', [
                'json' => $credentials,
                'headers' => [
                    'X-Security-Hash' => $this->securityManager->generateSecurityHash(),
                ],
            ]);

            if ($response->getStatusCode() === 200) {
                $data = json_decode($response->getBody()->getContents(), true);
                
                $this->accessToken = $data['access_token'];
                $this->refreshToken = $data['refresh_token'];
                $this->tokenExpiry = time() + $data['expires_in'];

                // Initialize WebSocket connection
                $this->initializeWebSocket();

                $this->analyticsManager->trackEvent('authentication_success', [
                    'user_id' => $data['user']['id'],
                    'timestamp' => time(),
                ]);

                $this->logger->info('Authentication successful', ['user_id' => $data['user']['id']]);

                return new AuthResult(true, $data, null);
            } else {
                $error = "Authentication failed: " . $response->getStatusCode();
                $this->logger->error($error);
                return new AuthResult(false, null, $error);
            }
        } catch (GuzzleException $e) {
            $error = "Authentication error: " . $e->getMessage();
            $this->analyticsManager->trackError('authentication_error', $e);
            $this->logger->error($error);
            return new AuthResult(false, null, $error);
        }
    }

    /**
     * Upload content with AI processing
     */
    public function uploadContent(ContentUpload $content): ContentUploadResult
    {
        try {
            $this->ensureAuthenticated();

            $multipart = [
                [
                    'name' => 'file',
                    'contents' => $content->getData(),
                    'filename' => $content->getFilename(),
                    'headers' => [
                        'Content-Type' => $content->getMimeType(),
                    ],
                ],
                [
                    'name' => 'metadata',
                    'contents' => json_encode($content->getMetadata()),
                ],
            ];

            $response = $this->httpClient->post('/content/upload', [
                'multipart' => $multipart,
                'headers' => [
                    'Authorization' => 'Bearer ' . $this->accessToken,
                    'X-Processing-Options' => 'ai_enhance=true,protection=enabled',
                    'X-Security-Hash' => $this->securityManager->generateSecurityHash(),
                ],
            ]);

            if ($response->getStatusCode() === 200) {
                $data = json_decode($response->getBody()->getContents(), true);

                $this->analyticsManager->trackEvent('content_upload_success', [
                    'content_id' => $data['id'],
                    'content_type' => $content->getType(),
                    'file_size' => strlen($content->getData()),
                ]);

                $this->logger->info('Content upload successful', ['content_id' => $data['id']]);

                return new ContentUploadResult(true, $data, null);
            } else {
                $error = "Upload failed: " . $response->getStatusCode();
                $this->logger->error($error);
                return new ContentUploadResult(false, null, $error);
            }
        } catch (GuzzleException $e) {
            $error = "Upload error: " . $e->getMessage();
            $this->analyticsManager->trackError('content_upload_error', $e);
            $this->logger->error($error);
            return new ContentUploadResult(false, null, $error);
        }
    }

    /**
     * Get analytics data
     */
    public function getAnalytics(array $filters = []): AnalyticsResult
    {
        try {
            $this->ensureAuthenticated();

            $response = $this->httpClient->get('/analytics', [
                'query' => $filters,
                'headers' => [
                    'Authorization' => 'Bearer ' . $this->accessToken,
                ],
            ]);

            if ($response->getStatusCode() === 200) {
                $data = json_decode($response->getBody()->getContents(), true);
                
                $this->logger->info('Analytics data retrieved', ['filters' => $filters]);
                
                return new AnalyticsResult(true, $data, null);
            } else {
                $error = "Analytics request failed: " . $response->getStatusCode();
                $this->logger->error($error);
                return new AnalyticsResult(false, null, $error);
            }
        } catch (GuzzleException $e) {
            $error = "Analytics error: " . $e->getMessage();
            $this->logger->error($error);
            return new AnalyticsResult(false, null, $error);
        }
    }

    /**
     * Initialize WebSocket connection for real-time features
     */
    private function initializeWebSocket(): void
    {
        if (!$this->config->isWebSocketEnabled()) {
            return;
        }

        try {
            $connector = new WsConnector();
            $wsUrl = $this->config->getWebSocketUrl() . '?token=' . $this->accessToken;

            $connector($wsUrl)
                ->then(function (WebSocket $conn) {
                    $this->webSocketConnection = $conn;
                    
                    $conn->on('message', function ($msg) {
                        $this->handleWebSocketMessage($msg->getPayload());
                    });

                    $conn->on('close', function ($code = null, $reason = null) {
                        $this->logger->info('WebSocket connection closed', ['code' => $code, 'reason' => $reason]);
                        $this->webSocketConnection = null;
                    });

                    $this->logger->info('WebSocket connection established');
                    $this->analyticsManager->trackEvent('websocket_connected');
                }, function (\Exception $e) {
                    $this->logger->error('WebSocket connection failed: ' . $e->getMessage());
                    $this->analyticsManager->trackError('websocket_connection_error', $e);
                });
        } catch (\Exception $e) {
            $this->logger->error('WebSocket initialization error: ' . $e->getMessage());
        }
    }

    /**
     * Handle incoming WebSocket messages
     */
    private function handleWebSocketMessage(string $message): void
    {
        try {
            $data = json_decode($message, true);
            
            if (!$data || !isset($data['type'])) {
                return;
            }

            $type = $data['type'];
            
            // Trigger event listeners
            if (isset($this->eventListeners[$type])) {
                foreach ($this->eventListeners[$type] as $callback) {
                    call_user_func($callback, $data);
                }
            }

            $this->analyticsManager->trackEvent('websocket_message_received', [
                'message_type' => $type,
                'message_id' => $data['id'] ?? null,
            ]);

            $this->logger->debug('WebSocket message handled', ['type' => $type]);
        } catch (\Exception $e) {
            $this->logger->error('WebSocket message handling error: ' . $e->getMessage());
        }
    }

    /**
     * Add event listener for WebSocket messages
     */
    public function addEventListener(string $eventType, callable $callback): void
    {
        if (!isset($this->eventListeners[$eventType])) {
            $this->eventListeners[$eventType] = [];
        }
        $this->eventListeners[$eventType][] = $callback;
    }

    /**
     * Send message via WebSocket
     */
    public function sendWebSocketMessage(array $message): bool
    {
        if (!$this->webSocketConnection) {
            $this->logger->warning('WebSocket not connected, cannot send message');
            return false;
        }

        try {
            $this->webSocketConnection->send(json_encode($message));
            return true;
        } catch (\Exception $e) {
            $this->logger->error('WebSocket send error: ' . $e->getMessage());
            return false;
        }
    }

    /**
     * Ensure valid authentication token
     */
    private function ensureAuthenticated(): void
    {
        if (!$this->accessToken) {
            throw new \RuntimeException('Not authenticated. Call authenticate() first.');
        }

        // Check if token needs refresh
        if ($this->tokenExpiry && $this->tokenExpiry - time() < self::TOKEN_EXPIRY_BUFFER) {
            $this->refreshAccessToken();
        }
    }

    /**
     * Refresh access token
     */
    private function refreshAccessToken(): void
    {
        if (!$this->refreshToken) {
            throw new \RuntimeException('No refresh token available');
        }

        try {
            $response = $this->httpClient->post('/auth/refresh', [
                'json' => ['refresh_token' => $this->refreshToken],
            ]);

            if ($response->getStatusCode() === 200) {
                $data = json_decode($response->getBody()->getContents(), true);
                $this->accessToken = $data['access_token'];
                $this->tokenExpiry = time() + $data['expires_in'];
                
                $this->logger->info('Access token refreshed');
            } else {
                throw new \RuntimeException('Token refresh failed: ' . $response->getStatusCode());
            }
        } catch (GuzzleException $e) {
            throw new \RuntimeException('Token refresh error: ' . $e->getMessage());
        }
    }

    /**
     * Get performance metrics
     */
    public function getMetrics(): array
    {
        return $this->metrics;
    }

    /**
     * Logout and cleanup
     */
    public function logout(): void
    {
        try {
            if ($this->accessToken) {
                $this->httpClient->post('/auth/logout', [
                    'headers' => [
                        'Authorization' => 'Bearer ' . $this->accessToken,
                    ],
                ]);
            }
        } catch (GuzzleException $e) {
            $this->logger->warning('Logout request failed: ' . $e->getMessage());
        }

        // Clear tokens
        $this->accessToken = null;
        $this->refreshToken = null;
        $this->tokenExpiry = null;

        // Close WebSocket
        if ($this->webSocketConnection) {
            $this->webSocketConnection->close();
            $this->webSocketConnection = null;
        }

        $this->analyticsManager->trackEvent('logout_success');
        $this->logger->info('Logout completed');
    }

    /**
     * Cleanup resources
     */
    public function __destruct()
    {
        $this->analyticsManager->flush();
    }
}

/**
 * Configuration class for AinfluenceClient
 */
class AinfluenceConfiguration
{
    private string $baseUrl;
    private string $webSocketUrl;
    private string $apiKey;
    private string $secretKey;
    private int $timeout;
    private bool $verifySsl;
    private bool $webSocketEnabled;
    private string $logPath;
    private bool $enableAnalytics;

    public function __construct(
        string $baseUrl,
        string $webSocketUrl,
        string $apiKey,
        string $secretKey,
        int $timeout = 30,
        bool $verifySsl = true,
        bool $webSocketEnabled = true,
        string $logPath = 'php://stderr',
        bool $enableAnalytics = true
    ) {
        $this->baseUrl = rtrim($baseUrl, '/');
        $this->webSocketUrl = $webSocketUrl;
        $this->apiKey = $apiKey;
        $this->secretKey = $secretKey;
        $this->timeout = $timeout;
        $this->verifySsl = $verifySsl;
        $this->webSocketEnabled = $webSocketEnabled;
        $this->logPath = $logPath;
        $this->enableAnalytics = $enableAnalytics;
    }

    // Getters
    public function getBaseUrl(): string { return $this->baseUrl; }
    public function getWebSocketUrl(): string { return $this->webSocketUrl; }
    public function getApiKey(): string { return $this->apiKey; }
    public function getSecretKey(): string { return $this->secretKey; }
    public function getTimeout(): int { return $this->timeout; }
    public function isVerifySsl(): bool { return $this->verifySsl; }
    public function isWebSocketEnabled(): bool { return $this->webSocketEnabled; }
    public function getLogPath(): string { return $this->logPath; }
    public function isEnableAnalytics(): bool { return $this->enableAnalytics; }
}

/**
 * Content upload class
 */
class ContentUpload
{
    private string $filename;
    private string $data;
    private string $type;
    private string $mimeType;
    private array $metadata;

    public function __construct(string $filename, string $data, string $type, string $mimeType, array $metadata = [])
    {
        $this->filename = $filename;
        $this->data = $data;
        $this->type = $type;
        $this->mimeType = $mimeType;
        $this->metadata = $metadata;
    }

    // Getters
    public function getFilename(): string { return $this->filename; }
    public function getData(): string { return $this->data; }
    public function getType(): string { return $this->type; }
    public function getMimeType(): string { return $this->mimeType; }
    public function getMetadata(): array { return $this->metadata; }
}

/**
 * Result classes
 */
class AuthResult
{
    public function __construct(
        public readonly bool $success,
        public readonly ?array $data,
        public readonly ?string $error
    ) {}
}

class ContentUploadResult
{
    public function __construct(
        public readonly bool $success,
        public readonly ?array $data,
        public readonly ?string $error
    ) {}
}

class AnalyticsResult
{
    public function __construct(
        public readonly bool $success,
        public readonly ?array $data,
        public readonly ?string $error
    ) {}
}

/**
 * Analytics Manager
 */
class AnalyticsManager
{
    private AinfluenceConfiguration $config;
    private Logger $logger;
    private array $events = [];

    public function __construct(AinfluenceConfiguration $config, Logger $logger)
    {
        $this->config = $config;
        $this->logger = $logger;
    }

    public function trackEvent(string $name, array $properties = []): void
    {
        if (!$this->config->isEnableAnalytics()) {
            return;
        }

        $event = [
            'name' => $name,
            'properties' => $properties,
            'timestamp' => time(),
        ];

        $this->events[] = $event;
        $this->logger->debug('Event tracked', $event);
    }

    public function trackError(string $name, \Throwable $exception): void
    {
        $this->trackEvent($name, [
            'error_message' => $exception->getMessage(),
            'error_code' => $exception->getCode(),
            'error_file' => $exception->getFile(),
            'error_line' => $exception->getLine(),
        ]);
    }

    public function flush(): void
    {
        // In a real implementation, this would send events to analytics service
        $this->events = [];
    }
}

/**
 * Security Manager
 */
class SecurityManager
{
    private AinfluenceConfiguration $config;

    public function __construct(AinfluenceConfiguration $config)
    {
        $this->config = $config;
    }

    public function generateSecurityHash(): string
    {
        $message = time() . '_' . $this->config->getApiKey();
        return hash_hmac('sha256', $message, $this->config->getSecretKey());
    }
}

/**
 * Cache Manager
 */
class CacheManager
{
    private AinfluenceConfiguration $config;
    private array $cache = [];

    public function __construct(AinfluenceConfiguration $config)
    {
        $this->config = $config;
    }

    public function get(string $key): mixed
    {
        return $this->cache[$key] ?? null;
    }

    public function set(string $key, mixed $value, int $ttl = 3600): void
    {
        $this->cache[$key] = [
            'value' => $value,
            'expires' => time() + $ttl,
        ];
    }

    public function has(string $key): bool
    {
        if (!isset($this->cache[$key])) {
            return false;
        }

        if ($this->cache[$key]['expires'] < time()) {
            unset($this->cache[$key]);
            return false;
        }

        return true;
    }
}