import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  Modal,
  FlatList,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { memoryAPI, aiAPI, voiceAPI } from '../../services/api';

interface MemoryType {
  value: string;
  label: string;
  icon: string;
  description: string;
}

interface AIEnhancement {
  summary: string;
  tags: string[];
  memory_type: string;
  importance: number;
  reasoning: string;
}

const CreateMemoryScreen = () => {
  const navigation = useNavigation();
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [selectedType, setSelectedType] = useState<string>('general');
  const [importance, setImportance] = useState(5);
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [showTypeSelector, setShowTypeSelector] = useState(false);
  const [aiEnhancement, setAiEnhancement] = useState<AIEnhancement | null>(null);
  const [showAiSuggestions, setShowAiSuggestions] = useState(false);
  const [aiSuggestions, setAiSuggestions] = useState<string[]>([]);

  const memoryTypes: MemoryType[] = [
    { value: 'work', label: 'Work', icon: '💼', description: 'Professional tasks and meetings' },
    { value: 'personal', label: 'Personal', icon: '👨‍👩‍👧‍👦', description: 'Family, friends, and personal life' },
    { value: 'learning', label: 'Learning', icon: '📚', description: 'Education and skill development' },
    { value: 'idea', label: 'Idea', icon: '💡', description: 'Creative thoughts and innovations' },
    { value: 'reminder', label: 'Reminder', icon: '⏰', description: 'Tasks and appointments' },
    { value: 'general', label: 'General', icon: '📝', description: 'General memories and notes' },
  ];

  useEffect(() => {
    loadAiSuggestions();
  }, []);

  const loadAiSuggestions = async () => {
    try {
      const response = await aiAPI.getSuggestions();
      setAiSuggestions(response.data.suggestions || []);
    } catch (error) {
      console.log('Could not load AI suggestions:', error);
    }
  };

  const handleAiEnhance = async () => {
    if (!content.trim()) {
      Alert.alert('Error', 'Please enter some content first');
      return;
    }

    setIsLoading(true);
    try {
      const response = await aiAPI.autoEnhanceMemory({
        content,
        memory_type: selectedType,
      });
      
      setAiEnhancement(response.data);
      setSelectedType(response.data.memory_type);
      setImportance(response.data.importance);
    } catch (error) {
      Alert.alert('Error', 'Failed to enhance memory with AI');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVoiceRecord = async () => {
    // Note: This would require proper voice recording implementation
    // For now, we'll show a placeholder
    Alert.alert(
      'Voice Recording',
      'Voice recording feature requires additional setup. Please use text input for now.',
      [{ text: 'OK' }]
    );
  };

  const handleCreateMemory = async () => {
    if (!title.trim() || !content.trim()) {
      Alert.alert('Error', 'Please fill in both title and content');
      return;
    }

    setIsLoading(true);
    try {
      const memoryData = {
        title: title.trim(),
        content: content.trim(),
        memory_type: selectedType,
        priority: importance >= 7 ? 'high' : importance >= 4 ? 'medium' : 'low',
      };

      await memoryAPI.createMemory(memoryData);
      
      Alert.alert(
        'Success',
        'Memory created successfully!',
        [
          {
            text: 'OK',
            onPress: () => navigation.goBack(),
          },
        ]
      );
    } catch (error) {
      Alert.alert('Error', 'Failed to create memory');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionSelect = (suggestion: string) => {
    setContent(prev => prev ? `${prev}\n\n${suggestion}` : suggestion);
    setShowAiSuggestions(false);
  };

  const selectedTypeData = memoryTypes.find(type => type.value === selectedType);

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Create Memory</Text>
          <Text style={styles.headerSubtitle}>Capture your thoughts and experiences</Text>
        </View>

        {/* AI Suggestions */}
        {aiSuggestions.length > 0 && (
          <View style={styles.section}>
            <TouchableOpacity
              style={styles.aiSuggestionsButton}
              onPress={() => setShowAiSuggestions(true)}
            >
              <Text style={styles.aiSuggestionsIcon}>🤖</Text>
              <Text style={styles.aiSuggestionsText}>AI Suggestions</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* Title Input */}
        <View style={styles.section}>
          <Text style={styles.label}>Title</Text>
          <TextInput
            style={styles.titleInput}
            value={title}
            onChangeText={setTitle}
            placeholder="Give your memory a title..."
            placeholderTextColor="#8E8E93"
            maxLength={100}
          />
        </View>

        {/* Content Input */}
        <View style={styles.section}>
          <View style={styles.contentHeader}>
            <Text style={styles.label}>Content</Text>
            <View style={styles.contentActions}>
              <TouchableOpacity
                style={styles.actionButton}
                onPress={handleVoiceRecord}
              >
                <Text style={styles.actionButtonText}>🎤</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.actionButton, { marginLeft: 8 }]}
                onPress={handleAiEnhance}
                disabled={isLoading}
              >
                <Text style={styles.actionButtonText}>✨</Text>
              </TouchableOpacity>
            </View>
          </View>
          <TextInput
            style={styles.contentInput}
            value={content}
            onChangeText={setContent}
            placeholder="What would you like to remember?"
            placeholderTextColor="#8E8E93"
            multiline
            textAlignVertical="top"
          />
        </View>

        {/* AI Enhancement Display */}
        {aiEnhancement && (
          <View style={styles.section}>
            <Text style={styles.label}>AI Enhancement</Text>
            <View style={styles.aiEnhancementCard}>
              <Text style={styles.aiEnhancementTitle}>Summary</Text>
              <Text style={styles.aiEnhancementText}>{aiEnhancement.summary}</Text>
              
              <Text style={styles.aiEnhancementTitle}>Tags</Text>
              <View style={styles.tagsContainer}>
                {aiEnhancement.tags.map((tag, index) => (
                  <View key={index} style={styles.tag}>
                    <Text style={styles.tagText}>{tag}</Text>
                  </View>
                ))}
              </View>
              
              <Text style={styles.aiEnhancementTitle}>Reasoning</Text>
              <Text style={styles.aiEnhancementText}>{aiEnhancement.reasoning}</Text>
            </View>
          </View>
        )}

        {/* Memory Type Selector */}
        <View style={styles.section}>
          <Text style={styles.label}>Memory Type</Text>
          <TouchableOpacity
            style={styles.typeSelector}
            onPress={() => setShowTypeSelector(true)}
          >
            <Text style={styles.typeIcon}>{selectedTypeData?.icon}</Text>
            <View style={styles.typeInfo}>
              <Text style={styles.typeName}>{selectedTypeData?.label}</Text>
              <Text style={styles.typeDescription}>{selectedTypeData?.description}</Text>
            </View>
            <Text style={styles.chevron}>›</Text>
          </TouchableOpacity>
        </View>

        {/* Importance Slider */}
        <View style={styles.section}>
          <Text style={styles.label}>Importance Level: {importance}</Text>
          <View style={styles.importanceContainer}>
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((level) => (
              <TouchableOpacity
                key={level}
                style={[
                  styles.importanceButton,
                  importance === level && styles.importanceButtonActive,
                ]}
                onPress={() => setImportance(level)}
              >
                <Text
                  style={[
                    styles.importanceText,
                    importance === level && styles.importanceTextActive,
                  ]}
                >
                  {level}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Create Button */}
        <TouchableOpacity
          style={[styles.createButton, isLoading && styles.createButtonDisabled]}
          onPress={handleCreateMemory}
          disabled={isLoading}
        >
          {isLoading ? (
            <ActivityIndicator color="#FFFFFF" />
          ) : (
            <Text style={styles.createButtonText}>Create Memory</Text>
          )}
        </TouchableOpacity>
      </ScrollView>

      {/* Type Selector Modal */}
      <Modal
        visible={showTypeSelector}
        animationType="slide"
        presentationStyle="pageSheet"
      >
        <SafeAreaView style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Select Memory Type</Text>
            <TouchableOpacity onPress={() => setShowTypeSelector(false)}>
              <Text style={styles.modalCloseButton}>Done</Text>
            </TouchableOpacity>
          </View>
          <FlatList
            data={memoryTypes}
            keyExtractor={(item) => item.value}
            renderItem={({ item }) => (
              <TouchableOpacity
                style={[
                  styles.typeOption,
                  selectedType === item.value && styles.typeOptionSelected,
                ]}
                onPress={() => {
                  setSelectedType(item.value);
                  setShowTypeSelector(false);
                }}
              >
                <Text style={styles.typeOptionIcon}>{item.icon}</Text>
                <View style={styles.typeOptionInfo}>
                  <Text style={styles.typeOptionName}>{item.label}</Text>
                  <Text style={styles.typeOptionDescription}>{item.description}</Text>
                </View>
                {selectedType === item.value && (
                  <Text style={styles.checkmark}>✓</Text>
                )}
              </TouchableOpacity>
            )}
          />
        </SafeAreaView>
      </Modal>

      {/* AI Suggestions Modal */}
      <Modal
        visible={showAiSuggestions}
        animationType="slide"
        presentationStyle="pageSheet"
      >
        <SafeAreaView style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>AI Suggestions</Text>
            <TouchableOpacity onPress={() => setShowAiSuggestions(false)}>
              <Text style={styles.modalCloseButton}>Close</Text>
            </TouchableOpacity>
          </View>
          <FlatList
            data={aiSuggestions}
            keyExtractor={(item, index) => index.toString()}
            renderItem={({ item }) => (
              <TouchableOpacity
                style={styles.suggestionItem}
                onPress={() => handleSuggestionSelect(item)}
              >
                <Text style={styles.suggestionText}>{item}</Text>
              </TouchableOpacity>
            )}
          />
        </SafeAreaView>
      </Modal>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  scrollView: {
    flex: 1,
  },
  header: {
    padding: 20,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E5EA',
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1A1A1A',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#6C757D',
  },
  section: {
    padding: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1A1A1A',
    marginBottom: 8,
  },
  titleInput: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    color: '#1A1A1A',
    borderWidth: 1,
    borderColor: '#E5E5EA',
  },
  contentHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  contentActions: {
    flexDirection: 'row',
  },
  actionButton: {
    backgroundColor: '#007AFF',
    borderRadius: 20,
    width: 32,
    height: 32,
    justifyContent: 'center',
    alignItems: 'center',
  },
  actionButtonText: {
    fontSize: 16,
  },
  contentInput: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    color: '#1A1A1A',
    borderWidth: 1,
    borderColor: '#E5E5EA',
    minHeight: 120,
  },
  aiSuggestionsButton: {
    backgroundColor: '#007AFF',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  aiSuggestionsIcon: {
    fontSize: 20,
    marginRight: 8,
  },
  aiSuggestionsText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  aiEnhancementCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E5E5EA',
  },
  aiEnhancementTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#007AFF',
    marginTop: 12,
    marginBottom: 4,
  },
  aiEnhancementText: {
    fontSize: 14,
    color: '#1A1A1A',
    lineHeight: 20,
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 4,
  },
  tag: {
    backgroundColor: '#F0F0F0',
    borderRadius: 16,
    paddingHorizontal: 12,
    paddingVertical: 6,
    marginRight: 8,
    marginBottom: 8,
  },
  tagText: {
    fontSize: 12,
    color: '#1A1A1A',
  },
  typeSelector: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E5E5EA',
  },
  typeIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  typeInfo: {
    flex: 1,
  },
  typeName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1A1A1A',
  },
  typeDescription: {
    fontSize: 14,
    color: '#6C757D',
    marginTop: 2,
  },
  chevron: {
    fontSize: 20,
    color: '#C7C7CC',
  },
  importanceContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  importanceButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#F0F0F0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  importanceButtonActive: {
    backgroundColor: '#007AFF',
  },
  importanceText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6C757D',
  },
  importanceTextActive: {
    color: '#FFFFFF',
  },
  createButton: {
    backgroundColor: '#007AFF',
    borderRadius: 12,
    padding: 16,
    margin: 20,
    alignItems: 'center',
  },
  createButtonDisabled: {
    backgroundColor: '#C7C7CC',
  },
  createButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
  modalContainer: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E5EA',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1A1A1A',
  },
  modalCloseButton: {
    fontSize: 16,
    color: '#007AFF',
    fontWeight: '600',
  },
  typeOption: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#FFFFFF',
    marginHorizontal: 20,
    marginVertical: 4,
    borderRadius: 12,
  },
  typeOptionSelected: {
    backgroundColor: '#E3F2FD',
  },
  typeOptionIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  typeOptionInfo: {
    flex: 1,
  },
  typeOptionName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1A1A1A',
  },
  typeOptionDescription: {
    fontSize: 14,
    color: '#6C757D',
    marginTop: 2,
  },
  checkmark: {
    fontSize: 18,
    color: '#007AFF',
    fontWeight: 'bold',
  },
  suggestionItem: {
    padding: 16,
    backgroundColor: '#FFFFFF',
    marginHorizontal: 20,
    marginVertical: 4,
    borderRadius: 12,
  },
  suggestionText: {
    fontSize: 16,
    color: '#1A1A1A',
    lineHeight: 22,
  },
});

export default CreateMemoryScreen;




