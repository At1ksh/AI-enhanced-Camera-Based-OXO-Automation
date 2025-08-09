import { FontAwesome } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useLocalSearchParams, useRouter } from 'expo-router';
import React, { useEffect, useState } from 'react';
import {
  Image,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

interface ComponentEntry {
  name: string;
  image: string;
  parts: string[];
  referenceImages: string[];
}

export default function ReferencePage() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { component, module, partIndex } = useLocalSearchParams();

  const [currentIndex, setCurrentIndex] = useState(0);
  const [entry, setEntry] = useState<ComponentEntry | null>(null);
  const [partName, setPartName] = useState('');
  const [referenceImage, setReferenceImage] = useState<string | null>(null);

  useEffect(() => {
    if (typeof partIndex === 'string') {
      setCurrentIndex(parseInt(partIndex));
    }
  }, [partIndex]);

  useEffect(() => {
    const loadComponentData = async () => {
      try {
        if (!module || !component || typeof component !== 'string') return;

        const compKey = `${module}_components`;
        const cached = await AsyncStorage.getItem(compKey);
        const parsed: Record<string, ComponentEntry> = cached ? JSON.parse(cached) : {};

        const selected = parsed[component];
        if (selected) {
          setEntry(selected);
          setPartName(selected.parts[currentIndex] || 'Unknown Location');
          setReferenceImage(selected.referenceImages[currentIndex] || null);
        } else {
          console.warn(`⚠️ No data found for component ${component}`);
        }
      } catch (err) {
        console.error('❌ Failed to load reference data:', err);
      }
    };

    loadComponentData();
  }, [currentIndex]);

  if (!component || typeof component !== 'string' || !entry) {
    return (
      <View style={styles.container}>
        <Text>❌ Invalid or missing component data.</Text>
      </View>
    );
  }

  const handleTakePicture = () => {
    router.push({
      pathname: '/rectify',
      params: {
        component,
        module,
        partIndex: currentIndex.toString(),
      },
    });
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.componentTitle}>{entry.name}</Text>
        <Text style={styles.subtitle}>Reference Guide</Text>
      </View>

      <ScrollView 
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
            <View style={styles.contentContainer}>
            <View style={styles.infoCard}>
              <View style={styles.infoRow}>
                <Text style={styles.label}>📍 Location:</Text>
                <Text style={styles.location}>{partName}</Text>
              </View>

              <View style={styles.instructionContainer}>
                <Text style={styles.instructionLabel}>📋 Instructions:</Text>
                <Text style={styles.instruction}>
                  {/* ✅ You can replace with dynamic instructions later */}
                  ALIGN CAMERA PROPERLY AND ENSURE CLARITY
                </Text>
              </View>
            </View>

            {referenceImage && (
              <View style={styles.imageContainer}>
                <Text style={styles.imageLabel}>🖼️ Reference Image</Text>
                <Image
                  source={{ uri: referenceImage }}
                  style={styles.referenceImage}
                  resizeMode="contain"
                />
              </View>
            )}

            <TouchableOpacity style={[styles.captureButton,{marginBottom: insets.bottom + 12}]} onPress={handleTakePicture}>
              <FontAwesome name="camera" size={28} color="#fff" />
              <Text style={styles.captureText}>Take Picture</Text>
            </TouchableOpacity>
            </View>
          </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    paddingTop: 60,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    paddingTop:10,
    paddingHorizontal: 20,
    paddingBottom: 30,
  },
  header: {
    alignItems: 'center',
    marginBottom: 30,
    marginHorizontal: 20,
    paddingVertical: 20,
    backgroundColor: '#ffffff',
    borderRadius: 20,
    elevation: 8,
  },
  componentTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 5,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: '#7f8c8d',
    fontWeight: '500',
    textAlign: 'center',
  },
  contentContainer: { flex: 1, width: '100%' },
  infoCard: {
    backgroundColor: '#ffffff',
    borderRadius: 20,
    padding: 25,
    marginBottom: 20,
    elevation: 6,
  },
  infoRow: { marginBottom: 20 },
  instructionContainer: {
    backgroundColor: '#fff3cd',
    borderRadius: 12,
    padding: 15,
    borderLeftWidth: 4,
    borderLeftColor: '#ffc107',
  },
  label: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#34495e',
    marginBottom: 8,
  },
  instructionLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#856404',
    marginBottom: 8,
  },
  location: {
    fontSize: 18,
    fontWeight: '600',
    color: '#2c3e50',
    backgroundColor: '#e8f4fd',
    padding: 12,
    borderRadius: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#007AFF',
  },
  instruction: { fontSize: 16, color: '#721c24', fontWeight: '600' },
  imageContainer: {
    backgroundColor: '#ffffff',
    borderRadius: 20,
    padding: 20,
    alignItems: 'center',
    elevation: 6,
    marginBottom: 30,
  },
  imageLabel: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 15,
    textAlign: 'center',
  },
  referenceImage: {
    width: '100%',
    height: 250,
    borderRadius: 15,
    backgroundColor: '#f8f9fa',
  },
  captureButton: {
    flexDirection: 'row',
    backgroundColor: '#007AFF',
    paddingVertical: 18,
    paddingHorizontal: 30,
    borderRadius: 25,
    alignItems: 'center',
    justifyContent: 'center',
    alignSelf: 'center',
    elevation: 8,
    minWidth: 200,
    marginTop: 20,
  },
  captureText: {
    color: '#fff',
    fontSize: 18,
    marginLeft: 12,
    fontWeight: 'bold',
  },
});
