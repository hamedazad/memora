import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
  Modal,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { memoryAPI } from '../../services/api';

interface Memory {
  id: number;
  title: string;
  content: string;
  memory_type: string;
  importance: number;
  created_at: string;
  tags: string[];
  summary?: string;
}

const MemoriesScreen = () => {
  const navigation = useNavigation();
  const [memories, setMemories] = useState<Memory[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedFilter, setSelectedFilter] = useState<string>('all');
  const [showFilters, setShowFilters] = useState(false);

  const memoryTypes = [
    { value: 'all', label: 'All Memories', icon: '📋' },
    { value: 'work', label: 'Work', icon: '💼' },
    { value: 'personal', label: 'Personal', icon: '👨‍👩‍👧‍👦' },
    { value: 'learning', label: 'Learning', icon: '📚' },
    { value: 'idea', label: 'Idea', icon: '💡' },
    { value: 'reminder', label: 'Reminder', icon: '⏰' },
    { value: 'general', label: 'General', icon: '📝' },
  ];

  useEffect(() => {
    loadMemories();
  }, [selectedFilter]);

  const loadMemories = async () => {
    try {
      setIsLoading(true);
      const params: any = {};
      if (selectedFilter !== 'all') {
        params.memory_type = selectedFilter;
      }
      
      const response = await memoryAPI.getMemories(params);
      setMemories(response.data.results || response.data.memories || []);
    } catch (error) {
      console.log('Error loading memories:', error);
      // Set mock data for demo
      setMemories([
        {
          id: 1,
          title: 'Team Meeting Notes',
          content: 'Discussed the new project roadmap and assigned tasks for next sprint.',
          memory_type: 'work',
          importance: 7,
          created_at: new Date().toISOString(),
          tags: ['meeting', 'project', 'roadmap'],
          summary: 'Project roadmap discussion and task assignments',
        },
        {
          id: 2,
          title: 'Learning React Native',
          content: 'Started learning React Native development. Focused on navigation and state management.',
          memory_type: 'learning',
          importance: 8,
          created_at: new Date(Date.now() - 86400000).toISOString(),
          tags: ['react-native', 'mobile', 'development'],
          summary: 'React Native learning progress',
        },
        {
          id: 3,
          title: 'Weekend Plans',
          content: 'Planning to visit the park with family and have a picnic.',
          memory_type: 'personal',
          importance: 5,
          created_at: new Date(Date.now() - 172800000).toISOString(),
          tags: ['family', 'weekend', 'outdoor'],
          summary: 'Family weekend picnic plans',
        },
      ]);
    } finally {
      setIsLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadMemories();
  };

  const getTypeIcon = (type: string) => {
    const typeData = memoryTypes.find(t => t.value === type);
    return typeData?.icon || '📝';
  };

  const getImportanceColor = (importance: number) => {
    if (importance >= 7) return '#FF3B30';
    if (importance >= 4) return '#FF9500';
    return '#34C759';
  };

  const renderMemoryItem = ({ item }: { item: Memory }) => (
    <TouchableOpacity
      style={styles.memoryCard}
      onPress={() => navigation.navigate('MemoryDetail' as any, { memoryId: item.id })}
    >
      <View style={styles.memoryHeader}>
        <View style={styles.memoryTypeContainer}>
          <Text style={styles.memoryTypeIcon}>{getTypeIcon(item.memory_type)}</Text>
          <Text style={styles.memoryType}>{item.memory_type.toUpperCase()}</Text>
        </View>
        <View style={[styles.importanceBadge, { backgroundColor: getImportanceColor(item.importance) }]}>
          <Text style={styles.importanceText}>{item.importance}</Text>
        </View>
      </View>
      
      <Text style={styles.memoryTitle} numberOfLines={2}>
        {item.title}
      </Text>
      
      <Text style={styles.memoryContent} numberOfLines={3}>
        {item.summary || item.content}
      </Text>
      
      {item.tags && item.tags.length > 0 && (
        <View style={styles.tagsContainer}>
          {item.tags.slice(0, 3).map((tag, index) => (
            <View key={index} style={styles.tag}>
              <Text style={styles.tagText}>{tag}</Text>
            </View>
          ))}
          {item.tags.length > 3 && (
            <Text style={styles.moreTagsText}>+{item.tags.length - 3}</Text>
          )}
        </View>
      )}
      
      <Text style={styles.memoryDate}>
        {new Date(item.created_at).toLocaleDateString()}
      </Text>
    </TouchableOpacity>
  );

  const renderFilterButton = ({ item }: { item: typeof memoryTypes[0] }) => (
    <TouchableOpacity
      style={[
        styles.filterButton,
        selectedFilter === item.value && styles.filterButtonActive,
      ]}
      onPress={() => {
        setSelectedFilter(item.value);
        setShowFilters(false);
      }}
    >
      <Text style={styles.filterIcon}>{item.icon}</Text>
      <Text
        style={[
          styles.filterText,
          selectedFilter === item.value && styles.filterTextActive,
        ]}
      >
        {item.label}
      </Text>
      {selectedFilter === item.value && (
        <Text style={styles.checkmark}>✓</Text>
      )}
    </TouchableOpacity>
  );

  const selectedFilterData = memoryTypes.find(t => t.value === selectedFilter);

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>My Memories</Text>
        <TouchableOpacity
          style={styles.filterSelector}
          onPress={() => setShowFilters(true)}
        >
          <Text style={styles.filterSelectorIcon}>{selectedFilterData?.icon}</Text>
          <Text style={styles.filterSelectorText}>{selectedFilterData?.label}</Text>
          <Text style={styles.chevron}>▼</Text>
        </TouchableOpacity>
      </View>

      {/* Memories List */}
      {isLoading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>Loading your memories...</Text>
        </View>
      ) : (
        <FlatList
          data={memories}
          keyExtractor={(item) => item.id.toString()}
          renderItem={renderMemoryItem}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
          contentContainerStyle={styles.listContainer}
          showsVerticalScrollIndicator={false}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text style={styles.emptyIcon}>📝</Text>
              <Text style={styles.emptyTitle}>No memories yet</Text>
              <Text style={styles.emptySubtitle}>
                Start creating memories to see them here
              </Text>
              <TouchableOpacity
                style={styles.createButton}
                onPress={() => navigation.navigate('CreateMemory' as any)}
              >
                <Text style={styles.createButtonText}>Create First Memory</Text>
              </TouchableOpacity>
            </View>
          }
        />
      )}

      {/* Filter Modal */}
      <Modal
        visible={showFilters}
        animationType="slide"
        presentationStyle="pageSheet"
      >
        <SafeAreaView style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Filter Memories</Text>
            <TouchableOpacity onPress={() => setShowFilters(false)}>
              <Text style={styles.modalCloseButton}>Done</Text>
            </TouchableOpacity>
          </View>
          <FlatList
            data={memoryTypes}
            keyExtractor={(item) => item.value}
            renderItem={renderFilterButton}
            contentContainerStyle={styles.filterList}
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
  header: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E5EA',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1A1A1A',
  },
  filterSelector: {
    backgroundColor: '#F0F0F0',
    borderRadius: 20,
    paddingHorizontal: 12,
    paddingVertical: 8,
    flexDirection: 'row',
    alignItems: 'center',
  },
  filterSelectorIcon: {
    fontSize: 16,
    marginRight: 6,
  },
  filterSelectorText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1A1A1A',
    marginRight: 6,
  },
  chevron: {
    fontSize: 12,
    color: '#6C757D',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: '#6C757D',
  },
  listContainer: {
    padding: 16,
  },
  memoryCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  memoryHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  memoryTypeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  memoryTypeIcon: {
    fontSize: 16,
    marginRight: 6,
  },
  memoryType: {
    fontSize: 12,
    fontWeight: '600',
    color: '#007AFF',
  },
  importanceBadge: {
    borderRadius: 8,
    paddingHorizontal: 6,
    paddingVertical: 2,
  },
  importanceText: {
    fontSize: 12,
    color: '#FFFFFF',
    fontWeight: 'bold',
  },
  memoryTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1A1A1A',
    marginBottom: 8,
  },
  memoryContent: {
    fontSize: 14,
    color: '#6C757D',
    lineHeight: 20,
    marginBottom: 12,
  },
  tagsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  tag: {
    backgroundColor: '#F0F0F0',
    borderRadius: 12,
    paddingHorizontal: 8,
    paddingVertical: 4,
    marginRight: 6,
  },
  tagText: {
    fontSize: 12,
    color: '#1A1A1A',
  },
  moreTagsText: {
    fontSize: 12,
    color: '#6C757D',
    fontStyle: 'italic',
  },
  memoryDate: {
    fontSize: 12,
    color: '#8E8E93',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: 16,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1A1A1A',
    marginBottom: 8,
  },
  emptySubtitle: {
    fontSize: 16,
    color: '#6C757D',
    textAlign: 'center',
    marginBottom: 24,
  },
  createButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    paddingHorizontal: 24,
    paddingVertical: 12,
  },
  createButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
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
  filterList: {
    padding: 16,
  },
  filterButton: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 8,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  filterButtonActive: {
    backgroundColor: '#E3F2FD',
  },
  filterIcon: {
    fontSize: 20,
    marginRight: 12,
  },
  filterText: {
    flex: 1,
    fontSize: 16,
    color: '#1A1A1A',
  },
  filterTextActive: {
    fontWeight: '600',
    color: '#007AFF',
  },
  checkmark: {
    fontSize: 16,
    color: '#007AFF',
    fontWeight: 'bold',
  },
});

export default MemoriesScreen;




