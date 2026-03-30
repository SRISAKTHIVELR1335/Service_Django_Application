import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Linking,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

import { useTheme } from '../theme/ThemeContext';
import { versionsApi } from '../api/versions';
import { APP_VERSION } from '../api/config';

const DownloadsScreen = () => {
  const { colors } = useTheme();
  
  const [versions, setVersions] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updateAvailable, setUpdateAvailable] = useState(false);

  useEffect(() => {
    loadVersions();
    checkForUpdates();
  }, []);

  const loadVersions = async () => {
    try {
      const data = await versionsApi.getLatestVersions();
      setVersions(data);
    } catch (error) {
      console.error('Failed to load versions:', error);
    } finally {
      setLoading(false);
    }
  };

  const checkForUpdates = async () => {
    try {
      const data = await versionsApi.checkForUpdates('android');
      setUpdateAvailable(data.update_available);
    } catch (error) {
      console.error('Failed to check updates:', error);
    }
  };

  const openLink = (url) => {
    if (url) {
      Linking.openURL(url).catch(() => {
        Alert.alert('Error', 'Cannot open link');
      });
    }
  };

  const styles = createStyles(colors);

  const renderDownloadCard = (title, description, icon, url, version = null) => (
    <TouchableOpacity
      style={styles.downloadCard}
      onPress={() => openLink(url)}
      disabled={!url}
    >
      <View style={styles.iconContainer}>
        <Icon name={icon} size={32} color={colors.primary} />
      </View>
      <View style={styles.cardInfo}>
        <Text style={styles.cardTitle}>{title}</Text>
        <Text style={styles.cardDescription}>{description}</Text>
        {version && (
          <Text style={styles.versionText}>Version: {version}</Text>
        )}
      </View>
      <Icon name="download" size={24} color={colors.primary} />
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container} edges={['left', 'right']}>
      <View style={styles.header}>
        <Text style={styles.title}>Downloads</Text>
        <Text style={styles.subtitle}>Client applications and drivers</Text>
      </View>

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
        </View>
      ) : (
        <View style={styles.content}>
          {updateAvailable && (
            <View style={styles.updateBanner}>
              <Icon name="update" size={24} color="#ffffff" />
              <View style={styles.updateInfo}>
                <Text style={styles.updateTitle}>Update Available</Text>
                <Text style={styles.updateText}>
                  A new version of the app is available
                </Text>
              </View>
            </View>
          )}

          <Text style={styles.sectionTitle}>Applications</Text>

          {renderDownloadCard(
            'Windows Client',
            'CAN-based diagnostic tool for Windows',
            'microsoft-windows',
            versions?.windows?.download_url,
            versions?.windows?.version
          )}

          {renderDownloadCard(
            'Android App',
            'Mobile diagnostic companion app',
            'android',
            versions?.android?.download_url,
            versions?.android?.version
          )}

          <Text style={styles.currentVersion}>
            Current app version: {APP_VERSION}
          </Text>

          <Text style={styles.sectionTitle}>CAN Drivers</Text>

          {renderDownloadCard(
            'PCAN Driver',
            'Peak Systems CAN interface driver',
            'usb',
            'https://www.peak-system.com/Drivers.523.0.html'
          )}

          {renderDownloadCard(
            'Kvaser Driver',
            'Kvaser CAN interface driver',
            'usb',
            'https://www.kvaser.com/downloads/'
          )}

          {renderDownloadCard(
            'Vector Driver',
            'Vector CAN interface driver',
            'usb',
            'https://www.vector.com/int/en/download/'
          )}
        </View>
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
    content: {
      flex: 1,
      paddingHorizontal: 16,
    },
    updateBanner: {
      flexDirection: 'row',
      alignItems: 'center',
      backgroundColor: colors.primary,
      borderRadius: 12,
      padding: 16,
      marginVertical: 12,
    },
    updateInfo: {
      marginLeft: 12,
    },
    updateTitle: {
      color: '#ffffff',
      fontSize: 16,
      fontWeight: '600',
    },
    updateText: {
      color: 'rgba(255, 255, 255, 0.8)',
      fontSize: 13,
      marginTop: 2,
    },
    sectionTitle: {
      fontSize: 18,
      fontWeight: '600',
      color: colors.text,
      marginTop: 20,
      marginBottom: 12,
    },
    downloadCard: {
      flexDirection: 'row',
      alignItems: 'center',
      backgroundColor: colors.card,
      borderRadius: 12,
      padding: 16,
      marginVertical: 6,
      shadowColor: colors.shadow,
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
      elevation: 2,
    },
    iconContainer: {
      width: 48,
      height: 48,
      borderRadius: 24,
      backgroundColor: colors.background,
      justifyContent: 'center',
      alignItems: 'center',
    },
    cardInfo: {
      flex: 1,
      marginLeft: 12,
    },
    cardTitle: {
      fontSize: 16,
      fontWeight: '600',
      color: colors.text,
    },
    cardDescription: {
      fontSize: 13,
      color: colors.textSecondary,
      marginTop: 2,
    },
    versionText: {
      fontSize: 12,
      color: colors.primary,
      marginTop: 4,
    },
    currentVersion: {
      fontSize: 13,
      color: colors.textSecondary,
      textAlign: 'center',
      marginTop: 12,
    },
    loadingContainer: {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
    },
  });

export default DownloadsScreen;
