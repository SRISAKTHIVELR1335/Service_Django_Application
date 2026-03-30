import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

import { useTheme } from '../theme/ThemeContext';
import { testsApi } from '../api/tests';

const TestsScreen = () => {
  const { colors } = useTheme();
  
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedType, setSelectedType] = useState('all');

  const testTypes = ['all', 'check', 'read', 'write'];

  useEffect(() => {
    loadTests();
  }, [selectedType]);

  const loadTests = async () => {
    try {
      const type = selectedType === 'all' ? null : selectedType;
      const data = await testsApi.getTests(null, type);
      setTests(data);
    } catch (error) {
      console.error('Failed to load tests:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadTests();
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'read':
        return colors.success;
      case 'write':
        return colors.warning;
      case 'check':
      default:
        return colors.primary;
    }
  };

  const renderTestItem = ({ item }) => (
    <View style={[styles.testCard, { backgroundColor: colors.card }]}>
      <View style={styles.testHeader}>
        <Text style={[styles.testName, { color: colors.text }]}>
          {item.name}
        </Text>
        <View
          style={[
            styles.typeBadge,
            { backgroundColor: getTypeColor(item.test_type) },
          ]}
        >
          <Text style={styles.typeText}>
            {item.test_type?.toUpperCase() || 'CHECK'}
          </Text>
        </View>
      </View>
      <View style={styles.testDetails}>
        <Text style={[styles.detailText, { color: colors.textSecondary }]}>
          <Icon name="puzzle" size={14} color={colors.textSecondary} /> {item.module_name || 'N/A'}
        </Text>
        <Text style={[styles.detailText, { color: colors.textSecondary }]}>
          <Icon name="function" size={14} color={colors.textSecondary} /> {item.function_name || 'run'}
        </Text>
      </View>
      {item.vehicle && (
        <Text style={[styles.vehicleText, { color: colors.primary }]}>
          <Icon name="car" size={14} color={colors.primary} /> {item.vehicle.name}
        </Text>
      )}
    </View>
  );

  const styles = createStyles(colors);

  return (
    <View style={styles.container}>
      <View style={styles.filters}>
        <FlatList
          horizontal
          data={testTypes}
          keyExtractor={(item) => item}
          showsHorizontalScrollIndicator={false}
          renderItem={({ item }) => (
            <TouchableOpacity
              style={[
                styles.filterButton,
                selectedType === item && styles.filterButtonActive,
              ]}
              onPress={() => setSelectedType(item)}
            >
              <Text
                style={[
                  styles.filterText,
                  selectedType === item && styles.filterTextActive,
                ]}
              >
                {item.charAt(0).toUpperCase() + item.slice(1)}
              </Text>
            </TouchableOpacity>
          )}
        />
      </View>

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
        </View>
      ) : (
        <FlatList
          data={tests}
          keyExtractor={(item) => item.id.toString()}
          renderItem={renderTestItem}
          contentContainerStyle={styles.listContent}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={onRefresh}
              tintColor={colors.primary}
            />
          }
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Icon name="clipboard-off" size={48} color={colors.textSecondary} />
              <Text style={styles.emptyText}>No tests found</Text>
            </View>
          }
        />
      )}
    </View>
  );
};

const createStyles = (colors) =>
  StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: colors.background,
    },
    filters: {
      paddingVertical: 12,
      paddingHorizontal: 8,
    },
    filterButton: {
      paddingHorizontal: 16,
      paddingVertical: 8,
      marginHorizontal: 4,
      borderRadius: 20,
      backgroundColor: colors.card,
      borderWidth: 1,
      borderColor: colors.border,
    },
    filterButtonActive: {
      backgroundColor: colors.primary,
      borderColor: colors.primary,
    },
    filterText: {
      fontSize: 14,
      color: colors.text,
    },
    filterTextActive: {
      color: '#ffffff',
      fontWeight: '600',
    },
    listContent: {
      paddingHorizontal: 16,
      paddingBottom: 20,
    },
    testCard: {
      padding: 16,
      borderRadius: 12,
      marginVertical: 6,
      shadowColor: colors.shadow,
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
      elevation: 2,
    },
    testHeader: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
    },
    testName: {
      fontSize: 16,
      fontWeight: '600',
      flex: 1,
    },
    typeBadge: {
      paddingHorizontal: 10,
      paddingVertical: 4,
      borderRadius: 12,
    },
    typeText: {
      color: '#ffffff',
      fontSize: 11,
      fontWeight: '600',
    },
    testDetails: {
      flexDirection: 'row',
      marginTop: 10,
      gap: 16,
    },
    detailText: {
      fontSize: 13,
    },
    vehicleText: {
      fontSize: 13,
      marginTop: 8,
    },
    loadingContainer: {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
    },
    emptyContainer: {
      justifyContent: 'center',
      alignItems: 'center',
      paddingVertical: 60,
    },
    emptyText: {
      color: colors.textSecondary,
      marginTop: 12,
      fontSize: 16,
    },
  });

export default TestsScreen;
