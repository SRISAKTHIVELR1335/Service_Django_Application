import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

import { useTheme } from '../theme/ThemeContext';
import { logsApi } from '../api/logs';

const LogsScreen = () => {
  const { colors } = useTheme();
  
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  useEffect(() => {
    loadLogs();
  }, []);

  const loadLogs = async (pageNum = 1, append = false) => {
    try {
      const data = await logsApi.getLogs(pageNum);
      if (append) {
        setLogs((prev) => [...prev, ...data.logs]);
      } else {
        setLogs(data.logs || []);
      }
      setHasMore(pageNum < data.pages);
      setPage(pageNum);
    } catch (error) {
      console.error('Failed to load logs:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadLogs(1, false);
  };

  const loadMore = () => {
    if (hasMore && !loading) {
      loadLogs(page + 1, true);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const renderLogItem = ({ item }) => (
    <View style={[styles.logCard, { backgroundColor: colors.card }]}>
      <View style={styles.logHeader}>
        <View style={styles.statusContainer}>
          <Icon
            name={item.status === 'PASS' ? 'check-circle' : 'close-circle'}
            size={20}
            color={item.status === 'PASS' ? colors.success : colors.danger}
          />
          <Text
            style={[
              styles.statusText,
              { color: item.status === 'PASS' ? colors.success : colors.danger },
            ]}
          >
            {item.status}
          </Text>
        </View>
        <Text style={[styles.dateText, { color: colors.textSecondary }]}>
          {formatDate(item.executed_at)}
        </Text>
      </View>
      <Text style={[styles.testName, { color: colors.text }]}>
        {item.test?.name || 'Unknown Test'}
      </Text>
      <View style={styles.logDetails}>
        <Text style={[styles.detailText, { color: colors.textSecondary }]}>
          <Icon name="car" size={14} color={colors.textSecondary} />{' '}
          {item.vehicle?.name || 'Unknown Vehicle'}
        </Text>
        {item.vin && (
          <Text style={[styles.detailText, { color: colors.textSecondary }]}>
            VIN: {item.vin}
          </Text>
        )}
      </View>
      {item.log_text && (
        <Text
          style={[styles.logText, { color: colors.textSecondary }]}
          numberOfLines={2}
        >
          {item.log_text}
        </Text>
      )}
    </View>
  );

  const styles = createStyles(colors);

  return (
    <SafeAreaView style={styles.container} edges={['left', 'right']}>
      <View style={styles.header}>
        <Text style={styles.title}>Test Logs</Text>
        <Text style={styles.subtitle}>View diagnostic test history</Text>
      </View>

      {loading && logs.length === 0 ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
        </View>
      ) : (
        <FlatList
          data={logs}
          keyExtractor={(item) => item.id.toString()}
          renderItem={renderLogItem}
          contentContainerStyle={styles.listContent}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={onRefresh}
              tintColor={colors.primary}
            />
          }
          onEndReached={loadMore}
          onEndReachedThreshold={0.5}
          ListFooterComponent={
            hasMore && !refreshing ? (
              <ActivityIndicator
                style={styles.footerLoader}
                color={colors.primary}
              />
            ) : null
          }
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Icon name="clipboard-text-off" size={48} color={colors.textSecondary} />
              <Text style={styles.emptyText}>No logs found</Text>
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
    title: {
      fontSize: 24,
      fontWeight: 'bold',
      color: colors.text,
    },
    subtitle: {
      fontSize: 14,
      color: colors.textSecondary,
      marginTop: 4,
    },
    listContent: {
      paddingHorizontal: 16,
      paddingBottom: 20,
    },
    logCard: {
      padding: 16,
      borderRadius: 12,
      marginVertical: 6,
      shadowColor: colors.shadow,
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
      elevation: 2,
    },
    logHeader: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: 8,
    },
    statusContainer: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: 6,
    },
    statusText: {
      fontSize: 14,
      fontWeight: '600',
    },
    dateText: {
      fontSize: 12,
    },
    testName: {
      fontSize: 16,
      fontWeight: '600',
    },
    logDetails: {
      flexDirection: 'row',
      marginTop: 8,
      gap: 16,
    },
    detailText: {
      fontSize: 13,
    },
    logText: {
      fontSize: 12,
      marginTop: 10,
      fontFamily: 'monospace',
      backgroundColor: colors.background,
      padding: 8,
      borderRadius: 6,
    },
    loadingContainer: {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
    },
    footerLoader: {
      paddingVertical: 20,
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

export default LogsScreen;
