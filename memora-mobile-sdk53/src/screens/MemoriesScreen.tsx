import React from 'react';
import { View, Text, StyleSheet, FlatList } from 'react-native';

const MemoriesScreen: React.FC = () => {
  const memories: any[] = []; // Will be populated with real data

  const renderEmptyState = () => (
    <View style={styles.emptyContainer}>
      <Text style={styles.emptyIcon}>📝</Text>
      <Text style={styles.emptyTitle}>No Memories Yet</Text>
      <Text style={styles.emptyText}>Create your first memory to get started!</Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <FlatList
        data={memories}
        renderItem={() => null}
        ListEmptyComponent={renderEmptyState}
        contentContainerStyle={styles.listContainer}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  listContainer: {
    flex: 1,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyIcon: {
    fontSize: 60,
    marginBottom: 20,
  },
  emptyTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1C1C1E',
    marginBottom: 10,
  },
  emptyText: {
    fontSize: 16,
    color: '#8E8E93',
    textAlign: 'center',
  },
});

export default MemoriesScreen;






