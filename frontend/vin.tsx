import { AntDesign } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { BlurView } from 'expo-blur';
import * as ImagePicker from 'expo-image-picker';
import { useRouter } from 'expo-router';
import React, { useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Animated,
  Easing,
  Image,
  ImageBackground,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';

import type { AxiosResponse } from 'axios';
import axios from 'axios';
import MlkitOcr from 'react-native-mlkit-ocr';
import { ComponentEntry } from '../types/component';
import { getBackendBaseURL } from '../utils/api';

export default function VinScreen() {
  const [image, setImage] = useState<string | null>(null);
  const [vin, setVin] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const fadeAnim = new Animated.Value(0);
  const retryPost = async (
    url: string,
    data: any,
    headers = {},
    maxAttempts = 4
  ): Promise<AxiosResponse> => {
    for (let i = 0; i < maxAttempts; i++) {
      try {
        return await axios.post(url, data, { headers, timeout: 10000 });
      } catch (err: any) {
        console.warn(`❌ Retry ${i + 1} failed:`, err.message || err);
        if (i === maxAttempts - 1) throw err;
        await new Promise(res => setTimeout(res, 1000));
      }
    }
    throw new Error("Unreachable"); // satisfy return type
  };

const retryGet = async (
    url: string,
    maxAttempts = 4
  ): Promise<AxiosResponse> => {
    for (let i = 0; i < maxAttempts; i++) {
      try {
        return await axios.get(url, { timeout: 10000 });
      } catch (err: any) {
        console.warn(`❌ Retry ${i + 1} failed (GET):`, err.message || err);
        if (i === maxAttempts - 1) throw err;
        await new Promise(res => setTimeout(res, 1000));
      }
    }
    throw new Error("Unreachable");
  };

  const animateText = () => {
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 600,
      easing: Easing.out(Easing.ease),
      useNativeDriver: true,
    }).start();
  };



const handleTakePhoto = async () => {
  const permissionResult = await ImagePicker.requestCameraPermissionsAsync();
  if (!permissionResult.granted) {
    Alert.alert('Permission Denied', 'Camera access is needed.');
    return;
  }

  const result = await ImagePicker.launchCameraAsync({
    quality: 1,
    allowsEditing: true,
    aspect: [4, 3],
    mediaTypes: ImagePicker.MediaTypeOptions.Images,
  });

  if (result.canceled) return;

  const uri = result.assets[0].uri;
  setImage(uri);
  setLoading(true);

  try {
    // ✅ Step 1: Extract text using ML Kit
    const blocks = await MlkitOcr.detectFromFile(uri);
    const allTexts = blocks.map(b => b.text.trim()).filter(Boolean);

    if (allTexts.length === 0) throw new Error("No text detected");

    const baseURL = await getBackendBaseURL();

    // ✅ Step 2: Send to backend for VIN verification
    const vinRes = await retryPost(`${baseURL}/verify_vin_text`, {
      texts: allTexts
    }, { "Content-Type": "application/json" });

    if (vinRes.data.status !== "success") {
      Alert.alert("Invalid VIN ❌", "No matching VIN found in system.");
      return;
    }

    const { vin: detectedVin, case_spec: caseSpec, engine_number: engineNumber, full_vin_number: fullVin } = vinRes.data;

    setVin(detectedVin);
    animateText();
    Alert.alert("VIN Verified ✅", `VIN: ${detectedVin}\nCase Spec: ${caseSpec}`);

    // ✅ Step 3: Fetch Case Spec
    const caseRes = await retryGet(`${baseURL}/get_case_spec?case_code=${caseSpec}`);

    if (caseRes.data.status !== "success") {
      Alert.alert("Error", "Could not fetch Case Spec config.");
      return;
    }

    const { frontendConfig, modelName, variantName, mainImagePath } = caseRes.data;

    // ✅ Step 4: Cache
    await AsyncStorage.setItem("car_overall", JSON.stringify({
      main_image: mainImagePath,
      model_name: modelName,
      variant_name: variantName,
      case_spec: caseSpec,
      vin: detectedVin,
      full_vin: fullVin,
      engine_number: engineNumber,
      total_interior: Object.keys(frontendConfig.interior).length,
      total_exterior: Object.keys(frontendConfig.exterior).length,
      total_loose: Object.keys(frontendConfig.loose).length,
    }));

    await AsyncStorage.setItem("interior_components", JSON.stringify(frontendConfig.interior));
    await AsyncStorage.setItem("exterior_components", JSON.stringify(frontendConfig.exterior));
    await AsyncStorage.setItem("loose_components", JSON.stringify(frontendConfig.loose));

    await initializeAuditFlow("interior", frontendConfig.interior);
    await initializeAuditFlow("exterior", frontendConfig.exterior);
    await initializeAuditFlow("loose", frontendConfig.loose);

    router.push("/carsummary");

  } catch (err: any) {
    console.error("❌ VIN Flow Error:", err.message || err);
    Alert.alert("Error", "Failed to verify VIN. Please try again.");
  } finally {
    setLoading(false);
  }
};


  const initializeAuditFlow = async (module: string, config: Record<string, ComponentEntry>) => {
    // ✅ Your existing logic unchanged, just fed with dynamic config
    await AsyncStorage.setItem(`${module}_pending_count`, Object.keys(config).length.toString());
    await AsyncStorage.setItem(`${module}_ok_count`, '0');
    await AsyncStorage.setItem(`${module}_notok_count`, '0');

    for (const [sysname, component] of Object.entries(config)) {
      const parts = component.parts;
      await AsyncStorage.setItem(`${sysname}_parts`, JSON.stringify(parts));
      await AsyncStorage.setItem(`${sysname}_index`, '0');

      const statusObj: Record<string, string> = { overall: 'pending' };
      parts.forEach((_, i) => {
        statusObj[i.toString()] = 'pending';
      });

      await AsyncStorage.setItem(`status_${sysname}`, JSON.stringify(statusObj));
      await AsyncStorage.setItem(`${sysname}_result_count`, JSON.stringify({ ok: 0, notok: 0 }));
    }

    await AsyncStorage.setItem('ok_count', '0');
    await AsyncStorage.setItem('notok_count', '0');
    await AsyncStorage.setItem('retries', '0');
  };

  return (
    <ImageBackground
      source={require('../assets/sexypic.jpg')}
      style={styles.backgroundImage}
      resizeMode="cover"
    >
      <BlurView intensity={80} style={styles.blurContainer}>
        <View style={styles.container}>
          <Text style={styles.header}>🚗 Scan VIN Number</Text>
          <View style={styles.card}>
            {image ? (
              <Image source={{ uri: image }} style={styles.imagePreview} />
            ) : (
              <View style={styles.placeholder}>
                <AntDesign name="camerao" size={48} color="#aaa" />
                <Text style={styles.placeholderText}>VIN image will appear here</Text>
              </View>
            )}
            <TouchableOpacity style={styles.scanButton} onPress={handleTakePhoto}>
              <AntDesign name="camera" size={20} color="#fff" />
              <Text style={styles.scanButtonText}>Take VIN Photo</Text>
            </TouchableOpacity>
            {loading && <ActivityIndicator size="large" color="#007AFF" style={{ marginTop: 10 }} />}
            {vin && !loading && (
              <Animated.View style={{ opacity: fadeAnim, marginTop: 10 }}>
                <Text style={styles.vinText}>
                  🔍 Detected VIN: <Text style={styles.vinValue}>{vin}</Text>
                </Text>
              </Animated.View>
            )}
          </View>
        </View>
      </BlurView>
    </ImageBackground>
  );
}

// ✅ (Your styles remain unchanged)

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
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  header: {
    fontSize: 26,
    fontWeight: '700',
    marginBottom: 20,
    color: '#2a2a2a',
    textShadowColor: 'rgba(255, 255, 255, 0.8)',
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 2,
  },
  card: {
    width: '100%',
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    padding: 20,
    borderRadius: 16,
    alignItems: 'center',
    elevation: 8,
    shadowColor: '#000',
    shadowOpacity: 0.3,
    shadowRadius: 10,
    shadowOffset: { width: 0, height: 4 },
  },
  imagePreview: {
    width: 280,
    height: 180,
    borderRadius: 12,
    marginBottom: 20,
    resizeMode: 'cover',
    borderWidth: 2,
    borderColor: '#fff',
  },
  placeholder: {
    width: 280,
    height: 180,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#ddd',
    backgroundColor: 'rgba(250, 250, 250, 0.9)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  placeholderText: {
    marginTop: 10,
    color: '#666',
    fontWeight: '500',
  },
  scanButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#007AFF',
    paddingVertical: 12,
    paddingHorizontal: 22,
    borderRadius: 8,
    marginBottom: 10,
    elevation: 4,
    shadowColor: '#000',
    shadowOpacity: 0.3,
    shadowRadius: 6,
    shadowOffset: { width: 0, height: 3 },
  },
  scanButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  vinText: {
    fontSize: 16,
    color: '#333',
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    padding: 10,
    borderRadius: 8,
    textAlign: 'center',
  },
  vinValue: {
    fontWeight: 'bold',
    color: '#007AFF',
  },
});
