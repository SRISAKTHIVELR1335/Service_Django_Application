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
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

import { useTheme } from '../theme/ThemeContext';
import { useAuth } from '../api/AuthContext';
import { vehiclesApi } from '../api/vehicles';

const DashboardScreen = ({ navigation }) => {
  const { colors } = useTheme();
  const { user } = useAuth();
  
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('All');

  const categories = ['All', 'Electric', 'Motorcycle', 'Scooter', '3-Wheeler'];

  useEffect(() => {
    loadVehicles();
  }, [selectedCategory]);

  const loadVehicles = async () => {
    try {
      const category = selectedCategory === 'All' ? null : selectedCategory;
      const data = await vehiclesApi.getVehicles(category);
      setVehicles(data);
    } catch (error) {
      console.error('Failed to load vehicles:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadVehicles();
  };

  const renderVehicleCard = ({ item }) => (
    <TouchableOpacity
      style={[styles.vehicleCard, { backgroundColor: colors.card }]}
      onPress={() => navigation.navigate('VehicleDetail', { vehicle: item })}
    >
      <View style={styles.vehicleIcon}>
        <Icon
          name={item.category === 'Electric' ? 'lightning-bolt' : 'motorbike'}
          size={32}
          color={colors.primary}
        />
      </View>
      <View style={styles.vehicleInfo}>
        <Text style={[styles.vehicleName, { color: colors.text }]}>
          {item.name}
        </Text>
        <Text style={[styles.vehicleCategory, { color: colors.textSecondary }]}>
          {item.category}
        </Text>
        {item.description && (
          <Text
            style={[styles.vehicleDescription, { color: colors.textSecondary }]}
            numberOfLines={1}
          >
            {item.description}
          </Text>
        )}
      </View>
      <Icon name="chevron-right" size={24} color={colors.textSecondary} />
    </TouchableOpacity>
  );

  const styles = createStyles(colors);

  return (
    <SafeAreaView style={styles.container} edges={['left', 'right']}>
      <View style={styles.header}>
        <Text style={styles.welcome}>
          Welcome, {user?.first_name || 'User'}!
        </Text>
        <Text style={styles.subtitle}>Select a vehicle to run diagnostics</Text>
      </View>

      <View style={styles.categories}>
        <FlatList
          horizontal
          data={categories}
          keyExtractor={(item) => item}
          showsHorizontalScrollIndicator={false}
          renderItem={({ item }) => (
            <TouchableOpacity
              style={[
                styles.categoryButton,
                selectedCategory === item && styles.categoryButtonActive,
              ]}
              onPress={() => setSelectedCategory(item)}
            >
              <Text
                style={[
                  styles.categoryText,
                  selectedCategory === item && styles.categoryTextActive,
                ]}
              >
                {item}
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
          data={vehicles}
          keyExtractor={(item) => item.id.toString()}
          renderItem={renderVehicleCard}
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
              <Icon name="car-off" size={48} color={colors.textSecondary} />
              <Text style={styles.emptyText}>No vehicles found</Text>
            </View>
          }
        />
      )}
    </SafeAreaView>
  );
};

const createStyles = (colors) =>
  StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: colors.background,
    },
    header: {
      paddingHorizontal: 20,
      paddingTop: 16,
      paddingBottom: 8,
    },
    welcome: {
      fontSize: 24,
      fontWeight: 'bold',
      color: colors.text,
    },
    subtitle: {
      fontSize: 14,
      color: colors.textSecondary,
      marginTop: 4,
    },
    categories: {
      paddingVertical: 12,
    },
    categoryButton: {
      paddingHorizontal: 16,
      paddingVertical: 8,
      marginHorizontal: 6,
      borderRadius: 20,
      backgroundColor: colors.card,
      borderWidth: 1,
      borderColor: colors.border,
    },
    categoryButtonActive: {
      backgroundColor: colors.primary,
      borderColor: colors.primary,
    },
    categoryText: {
      fontSize: 14,
      color: colors.text,
    },
    categoryTextActive: {
      color: '#ffffff',
      fontWeight: '600',
    },
    listContent: {
      paddingHorizontal: 16,
      paddingBottom: 20,
    },
    vehicleCard: {
      flexDirection: 'row',
      alignItems: 'center',
      padding: 16,
      borderRadius: 12,
      marginVertical: 6,
      shadowColor: colors.shadow,
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
      elevation: 2,
    },
    vehicleIcon: {
      width: 56,
      height: 56,
      borderRadius: 28,
      backgroundColor: colors.background,
      justifyContent: 'center',
      alignItems: 'center',
    },
    vehicleInfo: {
      flex: 1,
      marginLeft: 12,
    },
    vehicleName: {
      fontSize: 16,
      fontWeight: '600',
    },
    vehicleCategory: {
      fontSize: 13,
      marginTop: 2,
    },
    vehicleDescription: {
      fontSize: 12,
      marginTop: 4,
    },
    loadingContainer: {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
    },
    emptyContainer: {
      flex: 1,
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

export default DashboardScreen;
