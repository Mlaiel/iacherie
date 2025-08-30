/**
 * Mobile AI Assistant - Intelligent Creative Assistant
 * 
 * Advanced AI-powered assistant for content creation, optimization,
 * and creative guidance on mobile devices.
 * 
 * Author: Fahed Mlaiel <mlaiel@live.de>
 * Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️  CRITICAL LEGAL NOTICE:
 * This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
 * Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
 * Contact: mlaiel@live.de for licensing inquiries.
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Dimensions,
  TextInput,
  Image,
  Animated,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import LinearGradient from 'react-native-linear-gradient';

import { AIAssistantProps, AIMessage, AIConversation } from './types';

const { width, height } = Dimensions.get('window');

interface MobileAIAssistantProps extends AIAssistantProps {
  onVoiceInput?: () => void;
  onImageAnalysis?: (imageUri: string) => void;
  onContentGeneration?: (prompt: string, type: string) => void;
  theme?: 'light' | 'dark';
}

const MobileAIAssistant: React.FC<MobileAIAssistantProps> = ({
  conversation,
  onSendMessage,
  onSuggestionSelect,
  isTyping = false,
  capabilities,
  onVoiceInput,
  onImageAnalysis,
  onContentGeneration,
  theme = 'dark',
  style,
  testID,
}) => {
  const [inputText, setInputText] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedContext, setSelectedContext] = useState<'creative' | 'technical' | 'business' | 'general'>('creative');
  const [isRecording, setIsRecording] = useState(false);
  const [typingAnimation] = useState(new Animated.Value(0));
  
  const scrollViewRef = useRef<ScrollView>(null);
  const inputRef = useRef<TextInput>(null);

  useEffect(() => {
    // Scroll to bottom when new messages arrive
    if (conversation.messages.length > 0) {
      setTimeout(() => {
        scrollViewRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  }, [conversation.messages]);

  useEffect(() => {
    // Animate typing indicator
    if (isTyping) {
      Animated.loop(
        Animated.sequence([
          Animated.timing(typingAnimation, {
            toValue: 1,
            duration: 800,
            useNativeDriver: true,
          }),
          Animated.timing(typingAnimation, {
            toValue: 0,
            duration: 800,
            useNativeDriver: true,
          }),
        ])
      ).start();
    } else {
      typingAnimation.stopAnimation();
    }
  }, [isTyping, typingAnimation]);

  const handleSendMessage = useCallback(() => {
    if (inputText.trim()) {
      onSendMessage(inputText.trim());
      setInputText('');
      setShowSuggestions(false);
    }
  }, [inputText, onSendMessage]);

  const handleSuggestionPress = useCallback((suggestion: string) => {
    onSuggestionSelect(suggestion);
    setShowSuggestions(false);
  }, [onSuggestionSelect]);

  const handleVoiceRecord = useCallback(() => {
    if (isRecording) {
      setIsRecording(false);
      onVoiceInput?.();
    } else {
      setIsRecording(true);
      // Simulate recording for 3 seconds
      setTimeout(() => {
        setIsRecording(false);
        onVoiceInput?.();
      }, 3000);
    }
  }, [isRecording, onVoiceInput]);

  const getContextIcon = (context: AIConversation['context']) => {
    switch (context) {
      case 'creative': return 'palette';
      case 'technical': return 'cog';
      case 'business': return 'briefcase';
      case 'general': return 'chat';
      default: return 'chat';
    }
  };

  const getMessageIcon = (role: AIMessage['role']) => {
    return role === 'user' ? 'account' : 'robot';
  };

  const formatTimestamp = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const renderMessage = (message: AIMessage, index: number) => {
    const isUser = message.role === 'user';
    
    return (
      <View
        key={message.id}
        style={[
          styles.messageContainer,
          isUser ? styles.userMessageContainer : styles.assistantMessageContainer,
        ]}
      >
        <View
          style={[
            styles.messageBubble,
            isUser ? styles.userMessageBubble : styles.assistantMessageBubble,
          ]}
        >
          {!isUser && (
            <View style={styles.messageHeader}>
              <Icon name="robot" size={16} color="#3b82f6" />
              <Text style={styles.assistantLabel}>AI Assistant</Text>
            </View>
          )}
          
          <Text
            style={[
              styles.messageText,
              isUser ? styles.userMessageText : styles.assistantMessageText,
            ]}
          >
            {message.content}
          </Text>

          {message.attachments && message.attachments.length > 0 && (
            <View style={styles.attachmentsContainer}>
              {message.attachments.map((attachment, attachIndex) => (
                <TouchableOpacity
                  key={attachIndex}
                  style={styles.attachmentItem}
                  onPress={() => {
                    if (attachment.type === 'image' && onImageAnalysis) {
                      onImageAnalysis(attachment.uri);
                    }
                  }}
                >
                  {attachment.type === 'image' ? (
                    <Image source={{ uri: attachment.uri }} style={styles.attachmentImage} />
                  ) : (
                    <View style={styles.attachmentFile}>
                      <Icon name="file" size={20} color="#94a3b8" />
                      <Text style={styles.attachmentFileName}>{attachment.name}</Text>
                    </View>
                  )}
                </TouchableOpacity>
              ))}
            </View>
          )}

          <Text style={styles.messageTimestamp}>
            {formatTimestamp(message.timestamp)}
          </Text>
        </View>

        {message.suggestions && message.suggestions.length > 0 && (
          <View style={styles.suggestionsContainer}>
            {message.suggestions.map((suggestion, suggestionIndex) => (
              <TouchableOpacity
                key={suggestionIndex}
                style={styles.suggestionChip}
                onPress={() => handleSuggestionPress(suggestion)}
              >
                <Text style={styles.suggestionText}>{suggestion}</Text>
              </TouchableOpacity>
            ))}
          </View>
        )}
      </View>
    );
  };

  const renderTypingIndicator = () => {
    if (!isTyping) return null;

    return (
      <View style={styles.typingContainer}>
        <View style={styles.typingBubble}>
          <View style={styles.typingHeader}>
            <Icon name="robot" size={16} color="#3b82f6" />
            <Text style={styles.assistantLabel}>AI Assistant</Text>
          </View>
          <View style={styles.typingDots}>
            {[0, 1, 2].map((index) => (
              <Animated.View
                key={index}
                style={[
                  styles.typingDot,
                  {
                    opacity: typingAnimation.interpolate({
                      inputRange: [0, 1],
                      outputRange: [0.3, 1],
                    }),
                    transform: [
                      {
                        scale: typingAnimation.interpolate({
                          inputRange: [0, 1],
                          outputRange: [0.8, 1.2],
                        }),
                      },
                    ],
                  },
                ]}
              />
            ))}
          </View>
        </View>
      </View>
    );
  };

  const renderQuickActions = () => (
    <View style={styles.quickActionsContainer}>
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.quickActionsScroll}
      >
        <TouchableOpacity
          style={styles.quickActionButton}
          onPress={() => onContentGeneration?.('Generate a creative social media post', 'text')}
        >
          <Icon name="text" size={20} color="#3b82f6" />
          <Text style={styles.quickActionText}>Generate Text</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.quickActionButton}
          onPress={() => onContentGeneration?.('Create an engaging video concept', 'video')}
        >
          <Icon name="video" size={20} color="#8b5cf6" />
          <Text style={styles.quickActionText}>Video Ideas</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.quickActionButton}
          onPress={() => onContentGeneration?.('Suggest audio enhancements', 'audio')}
        >
          <Icon name="music" size={20} color="#10b981" />
          <Text style={styles.quickActionText}>Audio Tips</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.quickActionButton}
          onPress={() => onContentGeneration?.('Optimize for SEO and engagement', 'seo')}
        >
          <Icon name="trending-up" size={20} color="#f59e0b" />
          <Text style={styles.quickActionText}>SEO Help</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.quickActionButton}
          onPress={() => onContentGeneration?.('Analyze content performance', 'analytics')}
        >
          <Icon name="chart-line" size={20} color="#ef4444" />
          <Text style={styles.quickActionText}>Analytics</Text>
        </TouchableOpacity>
      </ScrollView>
    </View>
  );

  const renderContextSelector = () => (
    <View style={styles.contextContainer}>
      <Text style={styles.contextLabel}>Context:</Text>
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.contextScroll}
      >
        {(['creative', 'technical', 'business', 'general'] as const).map((context) => (
          <TouchableOpacity
            key={context}
            style={[
              styles.contextButton,
              selectedContext === context && styles.activeContextButton,
            ]}
            onPress={() => setSelectedContext(context)}
          >
            <Icon
              name={getContextIcon(context)}
              size={16}
              color={selectedContext === context ? '#ffffff' : '#94a3b8'}
            />
            <Text
              style={[
                styles.contextButtonText,
                selectedContext === context && styles.activeContextButtonText,
              ]}
            >
              {context.charAt(0).toUpperCase() + context.slice(1)}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>
    </View>
  );

  return (
    <SafeAreaView style={[styles.container, style]} testID={testID}>
      <KeyboardAvoidingView
        style={styles.keyboardAvoidingView}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 64 : 0}
      >
        {/* Header */}
        <LinearGradient
          colors={['#1e40af', '#3b82f6']}
          style={styles.header}
        >
          <View style={styles.headerContent}>
            <View style={styles.headerInfo}>
              <Icon name="robot" size={24} color="#ffffff" />
              <Text style={styles.headerTitle}>AI Assistant</Text>
            </View>
            <View style={styles.headerCapabilities}>
              <Text style={styles.capabilitiesText}>
                {capabilities.length} capabilities available
              </Text>
            </View>
          </View>
        </LinearGradient>

        {/* Context Selector */}
        {renderContextSelector()}

        {/* Messages */}
        <ScrollView
          ref={scrollViewRef}
          style={styles.messagesContainer}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          {conversation.messages.length === 0 ? (
            <View style={styles.emptyState}>
              <Icon name="robot-outline" size={64} color="#6b7280" />
              <Text style={styles.emptyStateTitle}>Welcome to AI Assistant</Text>
              <Text style={styles.emptyStateText}>
                I'm here to help you with content creation, optimization, and creative guidance.
                Ask me anything!
              </Text>
            </View>
          ) : (
            <>
              {conversation.messages.map(renderMessage)}
              {renderTypingIndicator()}
            </>
          )}
        </ScrollView>

        {/* Quick Actions */}
        {!showSuggestions && renderQuickActions()}

        {/* Input Area */}
        <View style={styles.inputContainer}>
          <LinearGradient
            colors={['#1e293b', '#334155']}
            style={styles.inputGradient}
          >
            <View style={styles.inputRow}>
              <TouchableOpacity
                style={styles.attachButton}
                onPress={() => Alert.alert('Attachment', 'Feature coming soon!')}
              >
                <Icon name="paperclip" size={20} color="#94a3b8" />
              </TouchableOpacity>

              <TextInput
                ref={inputRef}
                style={styles.textInput}
                placeholder="Ask me anything..."
                placeholderTextColor="#6b7280"
                value={inputText}
                onChangeText={setInputText}
                onFocus={() => setShowSuggestions(true)}
                onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                multiline
                maxLength={1000}
              />

              <TouchableOpacity
                style={[
                  styles.voiceButton,
                  isRecording && styles.recordingButton,
                ]}
                onPress={handleVoiceRecord}
                disabled={!onVoiceInput}
              >
                <Icon
                  name={isRecording ? 'microphone' : 'microphone-outline'}
                  size={20}
                  color={isRecording ? '#ef4444' : '#94a3b8'}
                />
              </TouchableOpacity>

              <TouchableOpacity
                style={[
                  styles.sendButton,
                  inputText.trim() ? styles.activeSendButton : styles.inactiveSendButton,
                ]}
                onPress={handleSendMessage}
                disabled={!inputText.trim()}
              >
                <Icon
                  name="send"
                  size={20}
                  color={inputText.trim() ? '#ffffff' : '#6b7280'}
                />
              </TouchableOpacity>
            </View>

            {inputText.length > 0 && (
              <Text style={styles.characterCount}>
                {inputText.length}/1000
              </Text>
            )}
          </LinearGradient>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a',
  },
  keyboardAvoidingView: {
    flex: 1,
  },
  header: {
    paddingHorizontal: 16,
    paddingVertical: 16,
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  headerInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
    marginLeft: 12,
  },
  headerCapabilities: {
    alignItems: 'flex-end',
  },
  capabilitiesText: {
    fontSize: 12,
    color: '#e2e8f0',
  },
  contextContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: '#1e293b',
  },
  contextLabel: {
    fontSize: 14,
    color: '#94a3b8',
    marginRight: 12,
  },
  contextScroll: {
    flex: 1,
  },
  contextButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: '#334155',
    borderRadius: 16,
    marginRight: 8,
  },
  activeContextButton: {
    backgroundColor: '#3b82f6',
  },
  contextButtonText: {
    fontSize: 12,
    color: '#94a3b8',
    marginLeft: 4,
  },
  activeContextButtonText: {
    color: '#ffffff',
  },
  messagesContainer: {
    flex: 1,
    paddingHorizontal: 16,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 32,
    paddingVertical: 64,
  },
  emptyStateTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
    marginTop: 16,
    textAlign: 'center',
  },
  emptyStateText: {
    fontSize: 16,
    color: '#94a3b8',
    textAlign: 'center',
    lineHeight: 24,
    marginTop: 8,
  },
  messageContainer: {
    marginVertical: 8,
  },
  userMessageContainer: {
    alignItems: 'flex-end',
  },
  assistantMessageContainer: {
    alignItems: 'flex-start',
  },
  messageBubble: {
    maxWidth: '80%',
    borderRadius: 16,
    padding: 12,
  },
  userMessageBubble: {
    backgroundColor: '#3b82f6',
    borderBottomRightRadius: 4,
  },
  assistantMessageBubble: {
    backgroundColor: '#1e293b',
    borderBottomLeftRadius: 4,
    borderWidth: 1,
    borderColor: '#334155',
  },
  messageHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  assistantLabel: {
    fontSize: 12,
    color: '#3b82f6',
    fontWeight: '600',
    marginLeft: 4,
  },
  messageText: {
    fontSize: 16,
    lineHeight: 22,
  },
  userMessageText: {
    color: '#ffffff',
  },
  assistantMessageText: {
    color: '#e2e8f0',
  },
  attachmentsContainer: {
    marginTop: 8,
  },
  attachmentItem: {
    marginBottom: 4,
  },
  attachmentImage: {
    width: 150,
    height: 100,
    borderRadius: 8,
  },
  attachmentFile: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 8,
    backgroundColor: '#334155',
    borderRadius: 8,
  },
  attachmentFileName: {
    fontSize: 12,
    color: '#e2e8f0',
    marginLeft: 8,
  },
  messageTimestamp: {
    fontSize: 10,
    color: '#6b7280',
    marginTop: 4,
    textAlign: 'right',
  },
  suggestionsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 8,
  },
  suggestionChip: {
    backgroundColor: '#334155',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    marginRight: 8,
    marginBottom: 4,
  },
  suggestionText: {
    fontSize: 12,
    color: '#e2e8f0',
  },
  typingContainer: {
    alignItems: 'flex-start',
    marginVertical: 8,
  },
  typingBubble: {
    backgroundColor: '#1e293b',
    borderRadius: 16,
    borderBottomLeftRadius: 4,
    padding: 12,
    borderWidth: 1,
    borderColor: '#334155',
  },
  typingDots: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  typingDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: '#94a3b8',
    marginHorizontal: 2,
  },
  quickActionsContainer: {
    backgroundColor: '#1e293b',
    paddingVertical: 12,
  },
  quickActionsScroll: {
    paddingHorizontal: 16,
  },
  quickActionButton: {
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: '#334155',
    borderRadius: 12,
    marginRight: 12,
    minWidth: 80,
  },
  quickActionText: {
    fontSize: 10,
    color: '#e2e8f0',
    marginTop: 4,
    textAlign: 'center',
  },
  inputContainer: {
    borderTopWidth: 1,
    borderTopColor: '#334155',
  },
  inputGradient: {
    padding: 16,
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
  },
  attachButton: {
    padding: 12,
    marginRight: 8,
  },
  textInput: {
    flex: 1,
    backgroundColor: '#334155',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    color: '#ffffff',
    maxHeight: 100,
    marginRight: 8,
  },
  voiceButton: {
    padding: 12,
    marginRight: 8,
  },
  recordingButton: {
    backgroundColor: 'rgba(239, 68, 68, 0.2)',
    borderRadius: 20,
  },
  sendButton: {
    padding: 12,
    borderRadius: 20,
  },
  activeSendButton: {
    backgroundColor: '#3b82f6',
  },
  inactiveSendButton: {
    backgroundColor: 'transparent',
  },
  characterCount: {
    fontSize: 10,
    color: '#6b7280',
    textAlign: 'right',
    marginTop: 4,
  },
});

export default MobileAIAssistant;