import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const CreateMemoryScreen: React.FC = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Create Memory</Text>
      <Text style={styles.subtitle}>Coming soon...</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1C1C1E',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#8E8E93',
  },
});

export default CreateMemoryScreen;






