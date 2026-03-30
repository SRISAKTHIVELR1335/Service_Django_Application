import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

import { useTheme } from '../theme/ThemeContext';
import { testsApi } from '../api/tests';

const VehicleDetailScreen = ({ route }) => {
  const { vehicle } = route.params;
  const { colors } = useTheme();
  
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTests();
  }, []);

  const loadTests = async () => {
    try {
      const data = await testsApi.getTests(vehicle.id);
      setTests(data);
    } catch (error) {
      console.error('Failed to load tests:', error);
    } finally {
      setLoading(false);
    }
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

  const handleTestPress = (test) => {
    Alert.alert(
      test.name,
      'CAN-based tests require the Windows client. This app displays test information for reference.',
      [{ text: 'OK' }]
    );
  };

  const renderTestItem = ({ item }) => (
    <TouchableOpacity
      style={[styles.testCard, { backgroundColor: colors.card }]}
      onPress={() => handleTestPress(item)}
    >
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
      <Text style={[styles.moduleName, { color: colors.textSecondary }]}>
        Module: {item.module_name || 'N/A'}
      </Text>
      {item.description && (
        <Text
          style={[styles.description, { color: colors.textSecondary }]}
          numberOfLines={2}
        >
          {item.description}
        </Text>
      )}
    </TouchableOpacity>
  );

  const styles = createStyles(colors);

  return (
    <View style={styles.container}>
      <View style={styles.vehicleHeader}>
        <View style={styles.vehicleIconContainer}>
          <Icon
            name={vehicle.category === 'Electric' ? 'lightning-bolt' : 'motorbike'}
            size={40}
            color={colors.primary}
          />
        </View>
        <View style={styles.vehicleInfo}>
          <Text style={styles.vehicleName}>{vehicle.name}</Text>
          <Text style={styles.vehicleCategory}>{vehicle.category}</Text>
        </View>
      </View>

      <Text style={styles.sectionTitle}>Available Tests</Text>

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
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Icon name="clipboard-off" size={48} color={colors.textSecondary} />
              <Text style={styles.emptyText}>No tests available</Text>
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
    vehicleHeader: {
      flexDirection: 'row',
      alignItems: 'center',
      padding: 20,
      backgroundColor: colors.card,
      marginBottom: 16,
    },
    vehicleIconContainer: {
      width: 64,
      height: 64,
      borderRadius: 32,
      backgroundColor: colors.background,
      justifyContent: 'center',
      alignItems: 'center',
    },
    vehicleInfo: {
      marginLeft: 16,
    },
    vehicleName: {
      fontSize: 20,
      fontWeight: 'bold',
      color: colors.text,
    },
    vehicleCategory: {
      fontSize: 14,
      color: colors.textSecondary,
      marginTop: 4,
    },
    sectionTitle: {
      fontSize: 18,
      fontWeight: '600',
      color: colors.text,
      paddingHorizontal: 20,
      marginBottom: 12,
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
    moduleName: {
      fontSize: 13,
      marginTop: 8,
    },
    description: {
      fontSize: 12,
      marginTop: 6,
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

export default VehicleDetailScreen;
