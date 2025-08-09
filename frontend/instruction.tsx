import { AntDesign } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { BlurView } from 'expo-blur';
import { useLocalSearchParams, useRouter } from 'expo-router';
import React, { useEffect, useState } from 'react';
import { Image, ScrollView, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

interface ComponentEntry {
  name: string;
  image: string;
  parts: string[];
}

export default function InstructionScreen() {
  const { component, module } = useLocalSearchParams();
  const router = useRouter();
  const insets = useSafeAreaInsets();


  const [requiredImages, setRequiredImages] = useState<number | null>(null);
  const [displayName, setDisplayName] = useState<string>('');
  const [modelName, setModelName] = useState<string>('');
  const [variantName, setVariantName] = useState<string>('');
  const [mainImage, setMainImage] = useState<string>('');

  useEffect(() => {
    const loadComponentDetails = async () => {
      try {
        if (!component || typeof component !== 'string' || !module) return;

        // ✅ Load car overall (for model & variant)
        const carDataRaw = await AsyncStorage.getItem("car_overall");
        if (carDataRaw) {
          const carData = JSON.parse(carDataRaw);
          setModelName(carData.model_name || '');
          setVariantName(carData.variant_name || '');
        }

        // ✅ Load the specific module components
        const compKey = `${module}_components`;
        const cached = await AsyncStorage.getItem(compKey);
        const parsed: Record<string, ComponentEntry> = cached ? JSON.parse(cached) : {};

        const selected = parsed[component];
        if (selected) {
          setDisplayName(selected.name);
          setMainImage(selected.image);
          setRequiredImages(selected.parts?.length || 1);
        } else {
          console.warn(`⚠️ No component found for ${component} in ${module}`);
          setRequiredImages(1);
        }

        await AsyncStorage.setItem('retries', '0');
      } catch (err) {
        console.error("❌ Failed to load component details:", err);
        setRequiredImages(1);
      }
    };

    loadComponentDetails();
  }, []);

  if (!component || typeof component !== 'string') {
    return (
      <View style={styles.container}>
        <Text style={styles.header}>Invalid Component</Text>
      </View>
    );
  }

  const handleGoBack = () => {
    switch (module) {
      case 'interior':
        router.push('/interior-hub');
        break;
      case 'exterior':
        router.push('/exterior-hub');
        break;
      case 'loose':
        router.push('/loose-hub');
        break;
      default:
        router.push('/mainhub');
    }
  };

  const handleProceed = async () => {
    const sysname = component;
    const statusKey = `status_${sysname}`;
    const resultKey = `${sysname}_result_count`;

    const rawStatus = await AsyncStorage.getItem(statusKey);
    const parsedStatus = rawStatus ? JSON.parse(rawStatus) : {};

    const pendingKey = `${module}_pending_count`;
    const notokKey = `${module}_notok_count`;

    if (parsedStatus.overall !== 'pending') {
      parsedStatus.overall = 'pending';
      await AsyncStorage.setItem(statusKey, JSON.stringify(parsedStatus));

      const p = parseInt((await AsyncStorage.getItem(pendingKey)) || '0');
      const n = parseInt((await AsyncStorage.getItem(notokKey)) || '0');
      await AsyncStorage.setItem(pendingKey, (p + 1).toString());
      await AsyncStorage.setItem(notokKey, Math.max(n - 1, 0).toString());

      await AsyncStorage.setItem(resultKey, JSON.stringify({ ok: 0, notok: 0 }));
    }

    await AsyncStorage.setItem('ok_count', '0');
    await AsyncStorage.setItem('notok_count', '0');

    router.push({
      pathname: '/reference',
      params: { component, module, index: '0' },
    });
  };

  return (
    <View style={styles.containerWrapper}>
      <BlurView intensity={80} style={styles.blurContainer}>
        <ScrollView contentContainerStyle={[styles.container, { paddingBottom: insets.bottom + 120 }]}>

          {/* ✅ Main Image */}
          {mainImage ? (
            <Image source={{ uri: mainImage }} style={styles.mainImage} />
          ) : null}

          <Text style={styles.header}>{displayName || component} Inspection</Text>

          <View style={styles.card}>
            <View style={styles.infoRow}>
              <Text style={styles.label}>Model:</Text>
              <Text style={styles.value}>{modelName || "N/A"}</Text>
            </View>

            <View style={styles.infoRow}>
              <Text style={styles.label}>Variant:</Text>
              <Text style={styles.value}>{variantName || "N/A"}</Text>
            </View>

            <View style={styles.requirementSection}>
              <Text style={styles.label}>Requirement:</Text>
              <Text style={styles.requirementText}>
                {requiredImages !== null
                  ? `You will be required to take ${requiredImages} picture${requiredImages > 1 ? 's' : ''} of this part.`
                  : 'Loading requirement...'}
              </Text>
            </View>
          </View>

          <TouchableOpacity style={styles.proceedButton} onPress={handleProceed}>
            <View style={styles.buttonContent}>
              <Text style={styles.proceedButtonText}>Proceed to Continue</Text>
              <AntDesign name="arrowright" size={20} color="#fff" />
            </View>
          </TouchableOpacity>

          <TouchableOpacity style={[styles.backButton,{marginBottom: insets.bottom + 12}]} onPress={handleGoBack}>
            <View style={styles.buttonContent}>
              <AntDesign name="arrowleft" size={20} color="#fff" />
              <Text style={styles.backButtonText}>Go Back</Text>
            </View>
          </TouchableOpacity>
        </ScrollView>
      </BlurView>
    </View>
  );
}

const styles = StyleSheet.create({
  containerWrapper: {
    flex: 1,
    backgroundColor: '#f2f2f2',  // or '#fff' or any flat color
  },
  blurContainer: { flex: 1 },
  container: {
    padding: 20,
    backgroundColor: 'transparent',
    paddingTop: 50,
    alignItems: 'center',
  },
  header: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
    color: '#2c3e50',
  },
  mainImage: {
    width: '90%',
    height: 150,
    borderRadius: 10,
    marginBottom: 15,
    alignSelf: 'center',
  },
  card: {
    marginBottom: 40,
    backgroundColor: '#ffffff',
    padding: 25,
    borderRadius: 20,
    elevation: 8,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(0,0,0,0.08)',
  },
  requirementSection: {
    marginTop: 15,
    padding: 15,
    backgroundColor: '#e8f4fd',
    borderRadius: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#007AFF',
  },
  label: { fontSize: 16, fontWeight: 'bold', color: '#34495e' },
  value: { fontSize: 16, color: '#2c3e50', fontWeight: '500' },
  requirementText: { fontSize: 16, color: '#2c3e50', marginTop: 5 },
  buttonContent: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  backButton: {
    backgroundColor: '#28a745',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 12,
    marginTop: 12,
    alignSelf: 'center',
  },
  backButtonText: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
  proceedButton: {
    backgroundColor: '#007AFF',
    paddingVertical: 15,
    paddingHorizontal: 30,
    borderRadius: 12,
    alignSelf: 'center',
    marginTop: 20,
  },
  proceedButtonText: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
});
