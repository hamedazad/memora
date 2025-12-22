import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  TextInput,
  TouchableOpacity,
  FlatList,
  ActivityIndicator,
  Alert,
  Modal,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { memoryAPI, aiAPI } from '../../services/api';

interface Memory {
  id: number;
  title: string;
  content: string;
  memory_type: string;
  importance: number;
  created_at: string;
  tags: string[];
  summary?: string;
  similarity_score?: number;
}

interface SearchFilter {
  memory_type?: string;
  importance_min?: number;
  date_from?: string;
  date_to?: string;
}

const SearchScreen = () => {
  const navigation = useNavigation();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Memory[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchType, setSearchType] = useState<'hybrid' | 'semantic' | 'keyword'>('hybrid');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<SearchFilter>({});
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);

  const memoryTypes = [
    { value: '', label: 'All Types', icon: '📋' },
    { value: 'work', label: 'Work', icon: '💼' },
    { value: 'personal', label: 'Personal', icon: '👨‍👩‍👧‍👦' },
    { value: 'learning', label: 'Learning', icon: '📚' },
    { value: 'idea', label: 'Idea', icon: '💡' },
    { value: 'reminder', label: 'Reminder', icon: '⏰' },
    { value: 'general', label: 'General', icon: '📝' },
  ];

  useEffect(() => {
    loadSuggestions();
    loadRecentSearches();
  }, []);

  useEffect(() => {
    if (searchQuery.length > 2) {
      const debounceTimer = setTimeout(() => {
        handleSearch();
      }, 500);
      return () => clearTimeout(debounceTimer);
    } else {
      setSearchResults([]);
    }
  }, [searchQuery, searchType, filters]);

  const loadSuggestions = async () => {
    try {
      const response = await aiAPI.getSearchSuggestions('');
      setSuggestions(response.data.suggestions || []);
    } catch (error) {
      console.log('Could not load suggestions:', error);
    }
  };

  const loadRecentSearches = () => {
    // In a real app, this would come from AsyncStorage
    setRecentSearches(['AI technology', 'team meeting', 'personal goals']);
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setIsLoading(true);
    try {
      let response;
      
      if (searchType === 'semantic') {
        response = await aiAPI.semanticSearch(searchQuery, {
          limit: 20,
          min_relevance: 0.5,
          search_type: 'semantic',
        });
      } else if (searchType === 'hybrid') {
        response = await aiAPI.semanticSearch(searchQuery, {
          limit: 20,
          min_relevance: 0.3,
          search_type: 'hybrid',
        });
      } else {
        // Keyword search
        response = await memoryAPI.getMemories({
          search: searchQuery,
          memory_type: filters.memory_type,
        });
      }

      setSearchResults(response.data.results || response.data.memories || []);
      
      // Add to recent searches
      setRecentSearches(prev => {
        const updated = [searchQuery, ...prev.filter(s => s !== searchQuery)];
        return updated.slice(0, 5);
      });
    } catch (error) {
      Alert.alert('Error', 'Search failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVoiceSearch = () => {
    Alert.alert(
      'Voice Search',
      'Voice search feature requires additional setup. Please use text input for now.',
      [{ text: 'OK' }]
    );
  };

  const renderMemoryItem = ({ item }: { item: Memory }) => {
    const typeIcon = memoryTypes.find(t => t.value === item.memory_type)?.icon || '📝';
    const importanceColor = item.importance >= 7 ? '#FF3B30' : item.importance >= 4 ? '#FF9500' : '#34C759';
    
    return (
      <TouchableOpacity
        style={styles.memoryItem}
        onPress={() => navigation.navigate('MemoryDetail' as any, { memoryId: item.id })}
      >
        <View style={styles.memoryHeader}>
          <View style={styles.memoryTypeContainer}>
            <Text style={styles.memoryTypeIcon}>{typeIcon}</Text>
            <Text style={styles.memoryType}>{item.memory_type.toUpperCase()}</Text>
          </View>
          <View style={styles.memoryMeta}>
            {item.similarity_score && (
              <Text style={styles.similarityScore}>
                {Math.round(item.similarity_score * 100)}%
              </Text>
            )}
            <View style={[styles.importanceBadge, { backgroundColor: importanceColor }]}>
              <Text style={styles.importanceText}>{item.importance}</Text>
            </View>
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
  };

  const renderSuggestion = ({ item }: { item: string }) => (
    <TouchableOpacity
      style={styles.suggestionItem}
      onPress={() => setSearchQuery(item)}
    >
      <Text style={styles.suggestionIcon}>💡</Text>
      <Text style={styles.suggestionText}>{item}</Text>
    </TouchableOpacity>
  );

  const renderRecentSearch = ({ item }: { item: string }) => (
    <TouchableOpacity
      style={styles.recentSearchItem}
      onPress={() => setSearchQuery(item)}
    >
      <Text style={styles.recentSearchIcon}>🕒</Text>
      <Text style={styles.recentSearchText}>{item}</Text>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      {/* Search Header */}
      <View style={styles.searchHeader}>
        <View style={styles.searchContainer}>
          <TextInput
            style={styles.searchInput}
            value={searchQuery}
            onChangeText={setSearchQuery}
            placeholder="Search your memories..."
            placeholderTextColor="#8E8E93"
            returnKeyType="search"
            onSubmitEditing={handleSearch}
          />
          <TouchableOpacity
            style={styles.voiceButton}
            onPress={handleVoiceSearch}
          >
            <Text style={styles.voiceButtonText}>🎤</Text>
          </TouchableOpacity>
        </View>
        
        {/* Search Type Selector */}
        <View style={styles.searchTypeContainer}>
          {['hybrid', 'semantic', 'keyword'].map((type) => (
            <TouchableOpacity
              key={type}
              style={[
                styles.searchTypeButton,
                searchType === type && styles.searchTypeButtonActive,
              ]}
              onPress={() => setSearchType(type as any)}
            >
              <Text
                style={[
                  styles.searchTypeText,
                  searchType === type && styles.searchTypeTextActive,
                ]}
              >
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
        
        {/* Filters Button */}
        <TouchableOpacity
          style={styles.filtersButton}
          onPress={() => setShowFilters(true)}
        >
          <Text style={styles.filtersButtonText}>🔍 Filters</Text>
        </TouchableOpacity>
      </View>

      {/* Search Results */}
      {searchQuery.length > 0 ? (
        <View style={styles.resultsContainer}>
          {isLoading ? (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color="#007AFF" />
              <Text style={styles.loadingText}>Searching...</Text>
            </View>
          ) : (
            <>
              <Text style={styles.resultsHeader}>
                {searchResults.length} results for "{searchQuery}"
              </Text>
              <FlatList
                data={searchResults}
                keyExtractor={(item) => item.id.toString()}
                renderItem={renderMemoryItem}
                showsVerticalScrollIndicator={false}
                ListEmptyComponent={
                  <View style={styles.emptyContainer}>
                    <Text style={styles.emptyText}>No memories found</Text>
                    <Text style={styles.emptySubtext}>
                      Try adjusting your search terms or filters
                    </Text>
                  </View>
                }
              />
            </>
          )}
        </View>
      ) : (
        <View style={styles.emptySearchContainer}>
          {/* Recent Searches */}
          {recentSearches.length > 0 && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Recent Searches</Text>
              <FlatList
                data={recentSearches}
                keyExtractor={(item, index) => index.toString()}
                renderItem={renderRecentSearch}
                horizontal
                showsHorizontalScrollIndicator={false}
              />
            </View>
          )}
          
          {/* Suggestions */}
          {suggestions.length > 0 && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Suggestions</Text>
              <FlatList
                data={suggestions.slice(0, 5)}
                keyExtractor={(item, index) => index.toString()}
                renderItem={renderSuggestion}
              />
            </View>
          )}
        </View>
      )}

      {/* Filters Modal */}
      <Modal
        visible={showFilters}
        animationType="slide"
        presentationStyle="pageSheet"
      >
        <SafeAreaView style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Search Filters</Text>
            <TouchableOpacity onPress={() => setShowFilters(false)}>
              <Text style={styles.modalCloseButton}>Done</Text>
            </TouchableOpacity>
          </View>
          
          <View style={styles.filterSection}>
            <Text style={styles.filterTitle}>Memory Type</Text>
            <FlatList
              data={memoryTypes}
              keyExtractor={(item) => item.value}
              renderItem={({ item }) => (
                <TouchableOpacity
                  style={[
                    styles.filterOption,
                    filters.memory_type === item.value && styles.filterOptionSelected,
                  ]}
                  onPress={() => setFilters(prev => ({ ...prev, memory_type: item.value }))}
                >
                  <Text style={styles.filterOptionIcon}>{item.icon}</Text>
                  <Text style={styles.filterOptionText}>{item.label}</Text>
                  {filters.memory_type === item.value && (
                    <Text style={styles.checkmark}>✓</Text>
                  )}
                </TouchableOpacity>
              )}
            />
          </View>
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
  searchHeader: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E5EA',
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  searchInput: {
    flex: 1,
    backgroundColor: '#F0F0F0',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    color: '#1A1A1A',
    marginRight: 8,
  },
  voiceButton: {
    backgroundColor: '#007AFF',
    borderRadius: 20,
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  voiceButtonText: {
    fontSize: 18,
  },
  searchTypeContainer: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  searchTypeButton: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 16,
    backgroundColor: '#F0F0F0',
    marginHorizontal: 2,
    alignItems: 'center',
  },
  searchTypeButtonActive: {
    backgroundColor: '#007AFF',
  },
  searchTypeText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#6C757D',
  },
  searchTypeTextActive: {
    color: '#FFFFFF',
  },
  filtersButton: {
    backgroundColor: '#F0F0F0',
    borderRadius: 8,
    paddingVertical: 8,
    paddingHorizontal: 12,
    alignSelf: 'flex-start',
  },
  filtersButtonText: {
    fontSize: 14,
    color: '#007AFF',
    fontWeight: '600',
  },
  resultsContainer: {
    flex: 1,
  },
  resultsHeader: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1A1A1A',
    padding: 16,
    backgroundColor: '#FFFFFF',
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
  memoryItem: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    marginHorizontal: 16,
    marginVertical: 4,
    borderRadius: 12,
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
  memoryMeta: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  similarityScore: {
    fontSize: 12,
    color: '#34C759',
    fontWeight: '600',
    marginRight: 8,
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
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1A1A1A',
    marginBottom: 4,
  },
  memoryContent: {
    fontSize: 14,
    color: '#6C757D',
    lineHeight: 20,
    marginBottom: 8,
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
    padding: 40,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1A1A1A',
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#6C757D',
    textAlign: 'center',
  },
  emptySearchContainer: {
    flex: 1,
  },
  section: {
    padding: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1A1A1A',
    marginBottom: 12,
  },
  recentSearchItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    paddingHorizontal: 12,
    paddingVertical: 8,
    marginRight: 8,
  },
  recentSearchIcon: {
    fontSize: 14,
    marginRight: 6,
  },
  recentSearchText: {
    fontSize: 14,
    color: '#1A1A1A',
  },
  suggestionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    padding: 12,
    marginVertical: 2,
    borderRadius: 8,
  },
  suggestionIcon: {
    fontSize: 16,
    marginRight: 12,
  },
  suggestionText: {
    fontSize: 16,
    color: '#1A1A1A',
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
  filterSection: {
    padding: 20,
  },
  filterTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1A1A1A',
    marginBottom: 12,
  },
  filterOption: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    padding: 12,
    marginVertical: 2,
    borderRadius: 8,
  },
  filterOptionSelected: {
    backgroundColor: '#E3F2FD',
  },
  filterOptionIcon: {
    fontSize: 18,
    marginRight: 12,
  },
  filterOptionText: {
    flex: 1,
    fontSize: 16,
    color: '#1A1A1A',
  },
  checkmark: {
    fontSize: 16,
    color: '#007AFF',
    fontWeight: 'bold',
  },
});

export default SearchScreen;




