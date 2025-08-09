import { FontAwesome, MaterialIcons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as ImageManipulator from 'expo-image-manipulator';
import * as ImagePicker from 'expo-image-picker';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { useEffect, useState } from 'react';
import {
  Alert,
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

export default function RectifyPage() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { component, module, partIndex } = useLocalSearchParams();
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [rotation, setRotation] = useState(0);
  const [entry, setEntry] = useState<ComponentEntry | null>(null);
  const [referenceImage, setReferenceImage] = useState<string | null>(null);
  const [partName, setPartName] = useState('');

  const currentIndex = typeof partIndex === 'string' ? parseInt(partIndex) : 0;

  useEffect(() => {
    // ✅ Load component details dynamically
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
        }
      } catch (err) {
        console.error('❌ Failed to load component details:', err);
      }
    };

    loadComponentData();
  }, [currentIndex]);

  useEffect(() => {
    (async () => {
      const { status } = await ImagePicker.requestCameraPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Camera permission is required');
        router.back();
        return;
      }

      const result = await ImagePicker.launchCameraAsync({ 
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 1,
      });
      if (!result.canceled) {
        setImageUri(result.assets[0].uri);
      } else {
        router.back();
      }
    })();
  }, []);

  const handleRotate = () => {
    setRotation((prev) => (prev + 90) % 360);
  };

  const handleRetake = () => {
    router.push({
      pathname: '/reference',
      params: { component, module, partIndex: partIndex?.toString() || '0' },
    });
  };

  const handleProceed = async () => {
    try {
      if (!imageUri) {
        Alert.alert('Error', 'No image to process');
        return;
      }

      let finalUri = imageUri;

      // ✅ Apply rotation physically (only if rotation != 0)
      if (rotation !== 0) {
        const manipulated = await ImageManipulator.manipulateAsync(
          imageUri,
          [{ rotate: rotation }],
          { compress: 1, format: ImageManipulator.SaveFormat.JPEG }
        );
        finalUri = manipulated.uri;
      }

      // ✅ Pass processed image to next screen
      router.push({
        pathname: '/processing',
        params: {
          component,
          module,
          partIndex: partIndex?.toString() || '0',
          capturedImage: finalUri, // ✅ rotated image URI
        },
      });
    } catch (error) {
      console.error('❌ Failed to process rotated image:', error);
      Alert.alert('Error', 'Could not process rotated image.');
    }
  };

  if (!entry) {
    return (
      <View style={styles.container}>
        <Text>❌ Loading component data...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>
      <View style={styles.header}>
        <Text style={styles.title}>Image Comparison</Text>
        <Text style={styles.subtitle}>{partName}</Text>
      </View>

          {imageUri ? (
            <>
              {referenceImage && (
                <View style={styles.imageSection}>
                  <Text style={styles.sectionTitle}>📋 Reference Image</Text>
                  <View style={styles.imageContainer}>
                    <Image
                      source={{ uri: referenceImage }}
                      style={styles.referenceImage}
                      resizeMode="contain"
                    />
                  </View>
                </View>
              )}

              <View style={styles.imageSection}>
                <Text style={styles.sectionTitle}>📸 Your Captured Image</Text>
                <View style={styles.imageContainer}>
                  <Image
                    source={{ uri: imageUri }}
                    style={[
                      styles.capturedImage,
                      { transform: [{ rotate: `${rotation}deg` }] },
                    ]}
                    resizeMode="contain"
                  />
                </View>
              </View>

              <View style={[styles.buttonSection,{marginBottom: insets.bottom + 20}]}>
                <View style={styles.buttonRow}>
                  <TouchableOpacity
                    style={[styles.actionButton, styles.rotateButton]}
                    onPress={handleRotate}
                  >
                    <MaterialIcons name="rotate-right" size={24} color="white" />
                    <Text style={styles.buttonText}>Rotate</Text>
                  </TouchableOpacity>

                  <TouchableOpacity
                    style={[styles.actionButton, styles.retakeButton]}
                    onPress={handleRetake}
                  >
                    <MaterialIcons name="refresh" size={24} color="white" />
                    <Text style={styles.buttonText}>Retake</Text>
                  </TouchableOpacity>
                </View>

                <TouchableOpacity
                  style={[styles.actionButton, styles.proceedButton]}
                  onPress={handleProceed}
                >
                  <FontAwesome name="check" size={24} color="white" />
                  <Text style={styles.buttonText}>Proceed to Analysis</Text>
                </TouchableOpacity>
              </View>
            </>
          ) : (
            <View style={styles.loadingContainer}>
              <Text style={styles.loadingText}>📷 Opening Camera...</Text>
            </View>
          )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { 
    flex: 1, 
    backgroundColor: '#f5f5f5' 
  },
  contentContainer: { padding: 20, paddingTop: 60 },
  header: {
    alignItems: 'center',
    marginBottom: 25,
    backgroundColor: '#ffffff',
    padding: 20,
    borderRadius: 20,
    elevation: 6,
  },
  title: { fontSize: 24, fontWeight: 'bold', color: '#2c3e50', marginBottom: 5 },
  subtitle: { fontSize: 16, color: '#7f8c8d', fontWeight: '500' },
  imageSection: { marginBottom: 25 },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2c3e50',
    marginBottom: 15,
    textAlign: 'center',
  },
  imageContainer: {
    backgroundColor: '#ffffff',
    borderRadius: 20,
    padding: 15,
    elevation: 6,
    alignItems: 'center',
  },
  referenceImage: {
    width: '100%',
    height: 200,
    borderRadius: 12,
    backgroundColor: '#f8f9fa',
  },
  capturedImage: {
    width: '100%',
    height: 250,
    borderRadius: 12,
    backgroundColor: '#f8f9fa',
  },
  buttonSection: { marginTop: 20 },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 15,
    gap: 10,
  },
  actionButton: {
    paddingVertical: 15,
    paddingHorizontal: 20,
    borderRadius: 15,
    alignItems: 'center',
    elevation: 5,
    minHeight: 60,
  },
  rotateButton: { backgroundColor: '#6c757d', flex: 1 },
  retakeButton: { backgroundColor: '#dc3545', flex: 1 },
  proceedButton: { backgroundColor: '#28a745', width: '100%' },
  buttonText: { color: 'white', fontSize: 16, fontWeight: 'bold', marginTop: 5 },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#ffffff',
    borderRadius: 20,
    padding: 40,
    elevation: 6,
  },
  loadingText: {
    fontSize: 18,
    color: '#7f8c8d',
    fontWeight: '500',
    textAlign: 'center',
  },
});
