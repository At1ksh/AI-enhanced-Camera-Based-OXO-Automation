// app/processing.tsx
import AsyncStorage from '@react-native-async-storage/async-storage';
import type { AxiosResponse } from 'axios';
import axios from 'axios';
import * as FileSystem from 'expo-file-system';
import { useLocalSearchParams, useRouter } from 'expo-router';
import React, { useEffect, useRef, useState } from 'react';
import {
  Animated,
  Image,
  StyleSheet,
  Text,
  View
} from 'react-native';
import MlkitOcr from 'react-native-mlkit-ocr';
import { getBackendBaseURL } from '../utils/api';

export default function ProcessingPage() {
  const router = useRouter();
  const { component, module, partIndex, capturedImage } = useLocalSearchParams();

  const [imageUri, setImageUri] = useState<string | null>(null);
  const rotationAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    // Start rotation animation
    const startRotation = () => {
      Animated.loop(
        Animated.timing(rotationAnim, {
          toValue: 1,
          duration: 2000,
          useNativeDriver: true,
        })
      ).start();
    };

    startRotation();

    if (typeof capturedImage === 'string') {
      setImageUri(capturedImage);
      processComponent(capturedImage);
    }
  }, [capturedImage]);

 const retryPost = async (
  url: string,
  data: any,
  headers = {},
  maxAttempts = 4
): Promise<AxiosResponse> => {
  for (let i = 0; i < maxAttempts; i++) {
    try {
      const response = await axios.post(url, data, {
        headers,
        timeout: 10000,
      });
      return response;
    } catch (err: any) {
      console.warn(`❌ POST retry ${i + 1} failed:`, err.message || err);
      if (i === maxAttempts - 1) throw err;
      await new Promise(res => setTimeout(res, 1000));
    }
  }

  throw new Error("Unreachable"); // to satisfy return type
};


const processComponent = async (uri: string) => {
  try {
    const carOverallRaw = await AsyncStorage.getItem("car_overall");
    if (!carOverallRaw) throw new Error("Car details not found in storage");

    const carOverall = JSON.parse(carOverallRaw);
    const caseSpec = carOverall.case_spec;
    const fullVin = carOverall.full_vin;

    const partsRaw = await AsyncStorage.getItem(`${component}_parts`);
    const parts = partsRaw ? JSON.parse(partsRaw) : [];
    const partName = parts[parseInt(partIndex as string) || 0] || "Unknown_Part";

    const formData = new FormData();
    formData.append("file", {
      uri,
      type: "image/jpeg",
      name: "captured.jpg",
    } as any);
    formData.append("case_spec", caseSpec);
    formData.append("component", component as string);
    formData.append("part_name", partName);
    formData.append("full_vin", fullVin);

    const baseURL = await getBackendBaseURL();

    // ✅ Retry the /process_component call
    const res = await retryPost(`${baseURL}/process_component`, formData, {
      "Content-Type": "multipart/form-data"
    });

    if (res.data.status === "success") {
      if (res.data.verdict.toUpperCase() === "OK") {
        router.replace({ pathname: '/result-ok', params: { component, module, partIndex } });
      } else {
        router.replace({ pathname: '/result-notok', params: { component, module, partIndex } });
      }

    } else if (res.data.status === "ocr_pending") {
      const ocrImageUri = `${FileSystem.cacheDirectory}ocr_input.jpg`;
      const downloadRes = await FileSystem.downloadAsync(res.data.ocr_image, ocrImageUri);
      const localImagePath = downloadRes.uri;

      const blocks = await MlkitOcr.detectFromFile(localImagePath);
      const detectedTexts = blocks.map(b => b.text.trim()).filter(Boolean);

      // ✅ Retry the /finalize_ocr_component_text call
      const ocrRes = await retryPost(`${baseURL}/finalize_ocr_component_text`, {
        texts: detectedTexts,
        component: res.data.component,
        case_spec: res.data.case_spec
      }, {
        "Content-Type": "application/json"
      });

      const finalVerdict = ocrRes.data.verdict;

      if (finalVerdict === "ok") {
        router.replace({ pathname: '/result-ok', params: { component, module, partIndex } });
      } else {
        router.replace({ pathname: '/result-notok', params: { component, module, partIndex } });
      }

    } else {
      router.replace({ pathname: '/result-notok', params: { component, module, partIndex } });
    }
  } catch (err: any) {
    console.error("❌ Final Processing Error:", err.message || err);
    router.replace({ pathname: '/result-notok', params: { component, module, partIndex } });
  }
};

  const spin = rotationAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '360deg'],
  });

  return (
    <View style={styles.container}>
      <Animated.View style={[styles.rotatingContainer, { transform: [{ rotate: spin }] }]}>
        <Image 
          source={require('../assets/rotatingwheel.png')} 
          style={styles.rotatingWheel}
          resizeMode="contain"
        />
      </Animated.View>
      <Text style={styles.processingText}>Processing...</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  rotatingContainer: {
    marginBottom: 30,
  },
  rotatingWheel: {
    width: 100,
    height: 100,
  },
  processingText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2c3e50',
    textAlign: 'center',
  },
});
