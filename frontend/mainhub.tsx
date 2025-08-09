import { AntDesign } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useFocusEffect } from '@react-navigation/native';
import { BlurView } from 'expo-blur';
import { useRouter } from 'expo-router';
import React, { useCallback, useState } from 'react';
import { ImageBackground, ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

export default function MainHub() {
  const router = useRouter();
  const insets = useSafeAreaInsets();

  const [counts, setCounts] = useState({
    interior: { pending: 0, ok: 0, notok: 0 },
    exterior: { pending: 0, ok: 0, notok: 0 },
    loose: { pending: 0, ok: 0, notok: 0 },
  });

  const getCardBackgroundColor = (pending: number, notok: number) => {
    if (pending > 0) return '#FFF3CD'; // Yellow for pending items
    if (notok > 0) return '#F8D7DA'; // Red for not ok items
    return '#D4F8D4'; // Green for all ok
  };

  const [carData, setCarData] = useState<any>(null);

  useFocusEffect(
  useCallback(() => {
    const loadCountsAndCar = async () => {
      try {
        // Load counts (existing code remains)
        const get = async (key: string) =>
          parseInt((await AsyncStorage.getItem(key)) ?? '0');

        const interior = {
          pending: await get('interior_pending_count'),
          ok: await get('interior_ok_count'),
          notok: await get('interior_notok_count'),
        };
        const exterior = {
          pending: await get('exterior_pending_count'),
          ok: await get('exterior_ok_count'),
          notok: await get('exterior_notok_count'),
        };
        const loose = {
          pending: await get('loose_pending_count'),
          ok: await get('loose_ok_count'),
          notok: await get('loose_notok_count'),
        };

        setCounts({ interior, exterior, loose });

        // ✅ NEW: Load car_overall for display
        const storedCar = await AsyncStorage.getItem("car_overall");
        if (storedCar) setCarData(JSON.parse(storedCar));
      } catch (error) { 
        console.error('Error loading counts:', error);
      }
    };

    loadCountsAndCar();
  }, [])
);
  return (
    <ImageBackground 
      source={require('../assets/sexypic.jpg')}
      style={styles.backgroundImage}
      resizeMode="cover"
    >
      <BlurView intensity={80} style={styles.blurContainer}>
        <ScrollView contentContainerStyle={styles.container} showsVerticalScrollIndicator={false}>
          <Text style={styles.heading}>Main Hub</Text>
          {carData && (
      <View style={{ marginBottom: 20, alignItems: 'center' }}>
        <Text style={{ fontSize: 16, fontWeight: 'bold', color: '#333' }}>
          {carData.case_spec} • {carData.vin}
        </Text>
        <Text style={{ fontSize: 12, color: '#555' }}>
          {carData.model_name}
        </Text>
      </View>
    )}

      <TouchableOpacity 
        style={[styles.card, { backgroundColor: getCardBackgroundColor(counts.interior.pending, counts.interior.notok) }]} 
        onPress={() => router.push('/interior-hub')}
      >
        <Text style={styles.cardTitle}>Interior Sub Components</Text>
        <View style={styles.statusContainer}>
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>Pending:</Text>
            <Text style={styles.statusValue}>{counts.interior.pending}</Text>
          </View>
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>OK:</Text>
            <Text style={styles.statusValue}>{counts.interior.ok}</Text>
          </View>
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>NOT OK:</Text>
            <Text style={styles.statusValue}>{counts.interior.notok}</Text>
          </View>
        </View>
      </TouchableOpacity>

      <TouchableOpacity 
        style={[styles.card, { backgroundColor: getCardBackgroundColor(counts.exterior.pending, counts.exterior.notok) }]} 
        onPress={() => router.push('/exterior-hub')}
      >
        <Text style={styles.cardTitle}>Exterior Sub Components</Text>
        <View style={styles.statusContainer}>
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>Pending:</Text>
            <Text style={styles.statusValue}>{counts.exterior.pending}</Text>
          </View>
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>OK:</Text>
            <Text style={styles.statusValue}>{counts.exterior.ok}</Text>
          </View>
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>NOT OK:</Text>
            <Text style={styles.statusValue}>{counts.exterior.notok}</Text>
          </View>
        </View>
      </TouchableOpacity>

      <TouchableOpacity 
        style={[styles.card, { backgroundColor: getCardBackgroundColor(counts.loose.pending, counts.loose.notok) }]} 
        onPress={() => router.push('/loose-hub')}
      >
        <Text style={styles.cardTitle}>Loose Car Points</Text>
        <View style={styles.statusContainer}>
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>Pending:</Text>
            <Text style={styles.statusValue}>{counts.loose.pending}</Text>
          </View>
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>OK:</Text>
            <Text style={styles.statusValue}>{counts.loose.ok}</Text>
          </View>
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>NOT OK:</Text>
            <Text style={styles.statusValue}>{counts.loose.notok}</Text>
          </View>
        </View>
      </TouchableOpacity>

      <View style={[styles.bottomRow, {bottom: insets.bottom + 20}]}>
        <TouchableOpacity style={[styles.bottomButton, { backgroundColor: '#28a745' }]} onPress={() => router.replace('/carsummary')}>
          <View style={styles.buttonContent}>
            <AntDesign name="arrowleft" size={20} color="#fff" />
            <Text style={styles.bottomText}>Go Back</Text>
          </View>
        </TouchableOpacity>

        <TouchableOpacity style={[styles.bottomButton, { backgroundColor: '#007AFF' }]} onPress={() => router.push('/summary')}>
          <View style={styles.buttonContent}>
            <Text style={styles.bottomText}>Finish</Text>
            <AntDesign name="arrowright" size={20} color="#fff" />
          </View>
        </TouchableOpacity>
      </View>
        </ScrollView>
      </BlurView>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  backgroundImage: {
    flex: 1,
    width: '100%',
    height: '100%',
  },
  blurContainer: {
    flex: 1,
  },
  container: { 
    padding: 20,
    paddingBottom: 160,  // ⬅️ extra space for bottom buttons
    alignItems: 'center',
  },
  heading: { 
    fontSize: 28, 
    fontWeight: 'bold', 
    marginBottom: 30, 
    color: '#000', 
    textShadowColor: 'rgba(255, 255, 255, 0.8)', 
    textShadowOffset: { width: 1, height: 1 }, 
    textShadowRadius: 2 
  },
  card: {
    width: '90%',
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    padding: 20,
    marginVertical: 12,
    borderRadius: 15,
    shadowColor: '#000',
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
    alignItems: 'center',
  },
  cardTitle: { fontSize: 20, fontWeight: 'bold', marginBottom: 15, color: '#000' },
  statusContainer: { alignItems: 'center', width: '100%' },
  statusRow: { 
    flexDirection: 'row', 
    justifyContent: 'space-between', 
    width: '80%', 
    marginVertical: 3,
    paddingHorizontal: 10,
  },
  statusLabel: { fontSize: 14, color: '#000', fontWeight: 'bold' },
  statusValue: { fontSize: 14, color: '#000', fontWeight: 'bold' },

  bottomRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
    position: 'absolute',
    paddingHorizontal: 20,
  },
  bottomButton: {
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 10,
    elevation: 6,
    shadowColor: '#000',
    shadowOpacity: 0.3,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 4 },
  },
  buttonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  bottomText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
