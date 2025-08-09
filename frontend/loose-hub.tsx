import { AntDesign } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { BlurView } from 'expo-blur';
import { useRouter } from 'expo-router';
import React, { useEffect, useState } from 'react';
import {
  Image,
  ImageBackground,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

interface ComponentEntry {
  name: string;
  image: string; // cached as URL
}

export default function LooseHub() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const [components, setComponents] = useState<Record<string, ComponentEntry>>({});
  const [statusMap, setStatusMap] = useState<Record<string, string>>({});
  const [pendingCount, setPendingCount] = useState(0);
  const [okCount, setOkCount] = useState(0);
  const [notOkCount, setNotOkCount] = useState(0);
  const [resultCounts, setResultCounts] = useState<Record<string, [number, number]>>({});

  useEffect(() => {
    const loadComponentsAndStatuses = async () => {
      try {
        // ✅ Load cached dynamic loose components
        const cached = await AsyncStorage.getItem('loose_components');
        console.log("🔍 Loaded loose_components:", cached);
        const parsed: Record<string, ComponentEntry> = cached ? JSON.parse(cached) : {};
        setComponents(parsed);

        // ✅ Load statuses
        const newMap: Record<string, string> = {};
        const resultMap: Record<string, [number, number]> = {};
        for (const sysname of Object.keys(parsed)) {
          const statusRaw = await AsyncStorage.getItem(`status_${sysname}`);
          const statusParsed = statusRaw ? JSON.parse(statusRaw) : {};
          newMap[sysname] = statusParsed.overall || 'pending';

          const resultRaw = await AsyncStorage.getItem(`${sysname}_result_count`);
          const resultParsed = resultRaw ? JSON.parse(resultRaw) : { ok: 0, notok: 0 };
          resultMap[sysname] = [resultParsed.ok || 0, resultParsed.notok || 0];
        }

        setStatusMap(newMap);
        setResultCounts(resultMap);

        // ✅ Load counts
        const p = await AsyncStorage.getItem('loose_pending_count');
        const o = await AsyncStorage.getItem('loose_ok_count');
        const n = await AsyncStorage.getItem('loose_notok_count');
        setPendingCount(parseInt(p || '0'));
        setOkCount(parseInt(o || '0'));
        setNotOkCount(parseInt(n || '0'));
      } catch (e) {
        console.error('❌ Failed to load loose components or statuses:', e);
      }
    };

    loadComponentsAndStatuses();
  }, []);

  const renderStatus = (sysname: string) => {
    const [ok, notok] = resultCounts[sysname] || [0, 0];
    if (ok === 0 && notok === 0) return <Text style={styles.pending}>🟡 Status: Pending</Text>;
    if (ok > 0 && notok === 0) return <Text style={styles.ok}>🟢 OK: {ok}</Text>;
    if (ok === 0 && notok > 0) return <Text style={styles.notok}>🔴 NOT OK: {notok}</Text>;
    return (
      <Text style={styles.statusLine}>
        <Text style={styles.ok}>🟢 OK: {ok}</Text>
        <Text style={{ color: '#000' }}> | </Text>
        <Text style={styles.notok}>🔴 NOT OK: {notok}</Text>
      </Text>
    );
  };

  return (
    <ImageBackground
      source={require('../assets/sexypic.jpg')}
      style={styles.backgroundImage}
      resizeMode="cover"
    >
      <BlurView intensity={80} style={styles.blurContainer}>
        <View style={styles.container}>
          <View style={styles.counterBox}>
            <Text style={styles.counterText}>
              <Text style={styles.pending}>Pending: {pendingCount}</Text> |{' '}
              <Text style={styles.ok}>OK: {okCount}</Text> |{' '}
              <Text style={styles.notok}>NOT OK: {notOkCount}</Text>
            </Text>
          </View>
          <ScrollView contentContainerStyle={[styles.scrollArea,{paddingBottom: insets.bottom + 80}]}>
            {Object.entries(components).map(([sysname, item], index) => {
              const overallStatus = statusMap[sysname] || 'pending';
              const isLocked = overallStatus === 'ok';

              let cardBackgroundColor = '#f2f2f2';
              if (overallStatus === 'pending') cardBackgroundColor = '#fff3cd';
              else if (overallStatus === 'ok') cardBackgroundColor = '#d4edda';
              else if (overallStatus === 'notok') cardBackgroundColor = '#f8d7da';

              return (
                <TouchableOpacity
                  key={index}
                  style={[styles.card, { backgroundColor: cardBackgroundColor }, isLocked && styles.lockedCard]}
                  disabled={isLocked}
                  onPress={() =>
                    !isLocked &&
                    router.push({
                      pathname: '/instruction',
                      params: { component: sysname, module: 'loose' },
                    })
                  }
                >
                  <Image source={{ uri: item.image }} style={styles.image} />
                  <View style={styles.info}>
                    <Text style={styles.name}>{item.name}</Text>
                    <Text style={styles.status}>{renderStatus(sysname)}</Text>
                    {isLocked && <Text style={styles.lockedText}>🔒 All Ok</Text>}
                  </View>
                </TouchableOpacity>
              );
            })}
          </ScrollView>
          <TouchableOpacity style={[styles.backButton,{marginBottom: insets.bottom + 12}]} onPress={() => router.push('/mainhub')}>
            <View style={styles.buttonContent}>
              <AntDesign name="arrowleft" size={20} color="#fff" />
              <Text style={styles.backButtonText}>Back to Main Hub</Text>
            </View>
          </TouchableOpacity>
        </View>
      </BlurView>
    </ImageBackground>
  );
}


const styles = StyleSheet.create({
  backgroundImage: {
    flex: 1,
  },
  blurContainer: {
    flex: 1,
  },
  container: { flex: 1, padding: 10, backgroundColor: 'transparent', paddingTop: 50 },

  counterBox: {
    backgroundColor: '#eeeeee',
    padding: 12,
    borderRadius: 10,
    marginBottom: 15,
    alignItems: 'center',
    elevation: 3,
  },
  statusLine: {
    fontSize: 14,
    fontWeight: '500',
    marginTop: 4,
  },
  counterText: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  pending: {
    color: '#e69500',
    fontWeight: 'bold',
  },
  ok: {
    color: '#2e8b57',
    fontWeight: 'bold',
  },
  notok: {
    color: '#d32f2f',
    fontWeight: 'bold',
  },

  scrollArea: {
    paddingBottom: 20,
  },
  card: {
    flexDirection: 'row',
    backgroundColor: '#f2f2f2',
    marginBottom: 15,
    borderRadius: 12,
    overflow: 'hidden',
    elevation: 2,
    borderWidth: 1,
    borderColor: 'rgba(0, 0, 0, 0.1)',
  },
  image: {
    width: 90,
    height: 90,
  },
  info: {
    flex: 1,
    padding: 12,
    justifyContent: 'center',
  },
  name: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 4,
  },
  status: {
    fontSize: 15,
  },
  lockedCard: {
    opacity: 0.6,
    borderColor: '#28a745',
    borderWidth: 2,
  },
  lockedText: {
    color: '#28a745',
    fontWeight: 'bold',
    marginTop: 6,
    fontSize: 13,
  },
  backButton: {
    backgroundColor: '#28a745',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 15,
    marginBottom: 5,
    elevation: 2,
  },
  buttonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  backButtonText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 16,
  },
});
