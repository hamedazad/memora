import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Dimensions,
  RefreshControl,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { aiAPI, analyticsAPI, memoryAPI } from '../../services/api';

interface DashboardStats {
  total_memories: number;
  memories_this_week: number;
  memories_this_month: number;
  average_importance: number;
  most_used_type: string;
  productivity_score: number;
}

interface MemoryInsight {
  title: string;
  description: string;
  icon: string;
  value: string;
  trend?: 'up' | 'down' | 'stable';
}

interface AIRecommendation {
  type: 'memory_prompt' | 'productivity_tip' | 'organization_tip';
  title: string;
  description: string;
  icon: string;
}

const DashboardScreen = () => {
  const navigation = useNavigation();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [insights, setInsights] = useState<MemoryInsight[]>([]);
  const [recommendations, setRecommendations] = useState<AIRecommendation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedPeriod, setSelectedPeriod] = useState<'week' | 'month' | 'year'>('month');

  useEffect(() => {
    loadDashboardData();
  }, [selectedPeriod]);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      
      // Load dashboard stats
      const [statsResponse, insightsResponse, recommendationsResponse] = await Promise.all([
        analyticsAPI.getDashboardData(),
        aiAPI.getMemoryInsights(),
        aiAPI.getPersonalizedRecommendations(),
      ]);

      setStats(statsResponse.data);
      setInsights(insightsResponse.data.insights || []);
      setRecommendations(recommendationsResponse.data.recommendations || []);
    } catch (error) {
      console.log('Error loading dashboard data:', error);
      // Set mock data for demo
      setStats({
        total_memories: 42,
        memories_this_week: 7,
        memories_this_month: 28,
        average_importance: 6.5,
        most_used_type: 'work',
        productivity_score: 78,
      });
      
      setInsights([
        {
          title: 'Memory Frequency',
          description: 'You\'ve been consistent this week',
          icon: '📊',
          value: '7 memories',
          trend: 'up',
        },
        {
          title: 'Focus Areas',
          description: 'Work memories are trending',
          icon: '💼',
          value: '60%',
          trend: 'up',
        },
        {
          title: 'Importance Level',
          description: 'Average importance score',
          icon: '⭐',
          value: '6.5/10',
          trend: 'stable',
        },
        {
          title: 'Learning Progress',
          description: 'Educational content growth',
          icon: '📚',
          value: '+25%',
          trend: 'up',
        },
      ]);
      
      setRecommendations([
        {
          type: 'memory_prompt',
          title: 'Reflect on Today',
          description: 'What was the most valuable thing you learned today?',
          icon: '💭',
        },
        {
          type: 'productivity_tip',
          title: 'Weekly Review',
          description: 'Consider reviewing your work memories from this week',
          icon: '🔍',
        },
        {
          type: 'organization_tip',
          title: 'Tag Organization',
          description: 'Try adding more specific tags to improve searchability',
          icon: '🏷️',
        },
      ]);
    } finally {
      setIsLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadDashboardData();
  };

  const getTypeIcon = (type: string) => {
    const icons: { [key: string]: string } = {
      work: '💼',
      personal: '👨‍👩‍👧‍👦',
      learning: '📚',
      idea: '💡',
      reminder: '⏰',
      general: '📝',
    };
    return icons[type] || '📝';
  };

  const getTrendIcon = (trend?: string) => {
    switch (trend) {
      case 'up': return '📈';
      case 'down': return '📉';
      case 'stable': return '➡️';
      default: return '';
    }
  };

  const getProductivityColor = (score: number) => {
    if (score >= 80) return '#34C759';
    if (score >= 60) return '#FF9500';
    return '#FF3B30';
  };

  const renderStatCard = (title: string, value: string | number, icon: string, color: string = '#007AFF') => (
    <View style={[styles.statCard, { borderLeftColor: color }]}>
      <View style={styles.statHeader}>
        <Text style={styles.statIcon}>{icon}</Text>
        <Text style={styles.statTitle}>{title}</Text>
      </View>
      <Text style={[styles.statValue, { color }]}>{value}</Text>
    </View>
  );

  const renderInsightCard = (insight: MemoryInsight) => (
    <View key={insight.title} style={styles.insightCard}>
      <View style={styles.insightHeader}>
        <Text style={styles.insightIcon}>{insight.icon}</Text>
        <View style={styles.insightInfo}>
          <Text style={styles.insightTitle}>{insight.title}</Text>
          <Text style={styles.insightDescription}>{insight.description}</Text>
        </View>
        <View style={styles.insightMeta}>
          <Text style={styles.insightValue}>{insight.value}</Text>
          {insight.trend && (
            <Text style={styles.trendIcon}>{getTrendIcon(insight.trend)}</Text>
          )}
        </View>
      </View>
    </View>
  );

  const renderRecommendation = (recommendation: AIRecommendation) => (
    <TouchableOpacity
      key={recommendation.title}
      style={styles.recommendationCard}
      onPress={() => {
        if (recommendation.type === 'memory_prompt') {
          navigation.navigate('CreateMemory' as any);
        }
      }}
    >
      <Text style={styles.recommendationIcon}>{recommendation.icon}</Text>
      <View style={styles.recommendationInfo}>
        <Text style={styles.recommendationTitle}>{recommendation.title}</Text>
        <Text style={styles.recommendationDescription}>{recommendation.description}</Text>
      </View>
      <Text style={styles.chevron}>›</Text>
    </TouchableOpacity>
  );

  if (isLoading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>Loading your insights...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>AI Dashboard</Text>
          <Text style={styles.headerSubtitle}>Your memory insights and recommendations</Text>
        </View>

        {/* Period Selector */}
        <View style={styles.periodSelector}>
          {['week', 'month', 'year'].map((period) => (
            <TouchableOpacity
              key={period}
              style={[
                styles.periodButton,
                selectedPeriod === period && styles.periodButtonActive,
              ]}
              onPress={() => setSelectedPeriod(period as any)}
            >
              <Text
                style={[
                  styles.periodText,
                  selectedPeriod === period && styles.periodTextActive,
                ]}
              >
                {period.charAt(0).toUpperCase() + period.slice(1)}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Quick Stats */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Overview</Text>
          <View style={styles.statsGrid}>
            {renderStatCard('Total Memories', stats?.total_memories || 0, '📝', '#007AFF')}
            {renderStatCard('This Month', stats?.memories_this_month || 0, '📅', '#34C759')}
            {renderStatCard('Avg. Importance', stats?.average_importance?.toFixed(1) || '0', '⭐', '#FF9500')}
            {renderStatCard('Productivity', `${stats?.productivity_score || 0}%`, '🎯', getProductivityColor(stats?.productivity_score || 0))}
          </View>
        </View>

        {/* Most Used Type */}
        {stats?.most_used_type && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Focus Area</Text>
            <View style={styles.focusCard}>
              <Text style={styles.focusIcon}>{getTypeIcon(stats.most_used_type)}</Text>
              <View style={styles.focusInfo}>
                <Text style={styles.focusTitle}>
                  {stats.most_used_type.charAt(0).toUpperCase() + stats.most_used_type.slice(1)}
                </Text>
                <Text style={styles.focusDescription}>
                  Your most active memory category this {selectedPeriod}
                </Text>
              </View>
            </View>
          </View>
        )}

        {/* Insights */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Insights</Text>
          {insights.map(renderInsightCard)}
        </View>

        {/* AI Recommendations */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>AI Recommendations</Text>
          {recommendations.map(renderRecommendation)}
        </View>

        {/* Quick Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.quickActions}>
            <TouchableOpacity
              style={styles.actionButton}
              onPress={() => navigation.navigate('CreateMemory' as any)}
            >
              <Text style={styles.actionIcon}>✨</Text>
              <Text style={styles.actionText}>Create Memory</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.actionButton}
              onPress={() => navigation.navigate('Search' as any)}
            >
              <Text style={styles.actionIcon}>🔍</Text>
              <Text style={styles.actionText}>Smart Search</Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
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
  periodSelector: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    margin: 16,
    borderRadius: 12,
    padding: 4,
  },
  periodButton: {
    flex: 1,
    paddingVertical: 8,
    borderRadius: 8,
    alignItems: 'center',
  },
  periodButtonActive: {
    backgroundColor: '#007AFF',
  },
  periodText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6C757D',
  },
  periodTextActive: {
    color: '#FFFFFF',
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1A1A1A',
    marginBottom: 12,
    paddingHorizontal: 16,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 16,
    gap: 12,
  },
  statCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    flex: 1,
    minWidth: '45%',
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  statHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  statIcon: {
    fontSize: 16,
    marginRight: 6,
  },
  statTitle: {
    fontSize: 14,
    color: '#6C757D',
    fontWeight: '500',
  },
  statValue: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  focusCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 16,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  focusIcon: {
    fontSize: 32,
    marginRight: 16,
  },
  focusInfo: {
    flex: 1,
  },
  focusTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1A1A1A',
    marginBottom: 4,
  },
  focusDescription: {
    fontSize: 14,
    color: '#6C757D',
  },
  insightCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 16,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  insightHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  insightIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  insightInfo: {
    flex: 1,
  },
  insightTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1A1A1A',
    marginBottom: 2,
  },
  insightDescription: {
    fontSize: 14,
    color: '#6C757D',
  },
  insightMeta: {
    alignItems: 'flex-end',
  },
  insightValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#007AFF',
    marginBottom: 2,
  },
  trendIcon: {
    fontSize: 16,
  },
  recommendationCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 16,
    marginBottom: 8,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  recommendationIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  recommendationInfo: {
    flex: 1,
  },
  recommendationTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1A1A1A',
    marginBottom: 2,
  },
  recommendationDescription: {
    fontSize: 14,
    color: '#6C757D',
  },
  chevron: {
    fontSize: 20,
    color: '#C7C7CC',
  },
  quickActions: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    gap: 12,
  },
  actionButton: {
    flex: 1,
    backgroundColor: '#007AFF',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  actionIcon: {
    fontSize: 24,
    marginBottom: 8,
  },
  actionText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default DashboardScreen;
