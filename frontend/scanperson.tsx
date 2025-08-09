import { AntDesign } from "@expo/vector-icons";
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from "axios";
import { BlurView } from "expo-blur";
import * as ImagePicker from "expo-image-picker";
import { useRouter } from "expo-router";
import React, { useEffect, useRef, useState } from "react";
import {
  Alert,
  Animated,
  Image,
  ImageBackground,
  KeyboardAvoidingView, Platform,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import MlkitOcr from 'react-native-mlkit-ocr';
import { SafeAreaView } from "react-native-safe-area-context";

export default function ScanPersonScreen() {
  
  const [image, setImage] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const [verified, setVerified] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const router = useRouter();
  
  const spinValue = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (isProcessing) {
      const spinAnimation = Animated.loop(
        Animated.timing(spinValue, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        })
      );
      spinAnimation.start();
      return () => spinAnimation.stop();
    }
  }, [isProcessing, spinValue]);

  const handlePickImage = async () => {
    const permissionResult = await ImagePicker.requestCameraPermissionsAsync();
    if (permissionResult.status !== "granted") {
        Alert.alert("Permission Denied", "Camera access is required.");
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
    setIsProcessing(true);

    try {
        const blocks = await MlkitOcr.detectFromFile(uri);
        const allTexts = blocks.map(b => b.text.trim()).filter(Boolean);
        console.log("🧠 MLKit Detected:", allTexts);

        // Now send this to backend, as we discussed
        const rawIP = await AsyncStorage.getItem("backend_ip");
        const baseURL = `http://${rawIP}`;
        const payload = { texts: allTexts };

        let response;
        for (let i = 0; i < 4; i++) {
        try {
            response = await axios.post(`${baseURL}/verify_person_text`, payload, {
            headers: { "Content-Type": "application/json" },
            timeout: 10000
            });
            break;
        } catch (e) {
            console.warn(`Retry ${i + 1} failed`);
            if (i === 3) throw e;
            await new Promise(res => setTimeout(res, 1000));
        }
        }

        if (!response) {
        throw new Error("Backend not reachable after retries.");
        }

        const res = response.data;
        if (res.status === "verified") {
        setVerified(true);
        setResult(res);
        await AsyncStorage.setItem("person_name", res.name || "");
        await AsyncStorage.setItem("person_pno", res.pno || "");
        await AsyncStorage.setItem("person_department", res.department || "");
        } else {
        setVerified(false);
        setResult({ status: "not_verified", detected: res.detected });
        }
    } catch (err) {
        console.error("🛑 MLKit OCR failed:", err);
        Alert.alert("Error", "MLKit OCR failed or backend unreachable");
    } finally {
        setIsProcessing(false);
    }
    };
  return (
  <SafeAreaView style={{ flex: 1 }}>
    <ImageBackground
      source={require("../assets/sexypic.jpg")}
      style={styles.backgroundImage}
      resizeMode="cover"
    >
      <BlurView intensity={80} style={styles.blurContainer}>
        <KeyboardAvoidingView
          style={{ flex: 1 }}
          behavior={Platform.OS === "ios" ? "padding" : "height"}
        >
          <ScrollView contentContainerStyle={styles.scrollContainer}>
            <View style={styles.container}>
              

              <Text style={styles.title}>Scan Your ID</Text>

              {image ? (
                <Image source={{ uri: image }} style={styles.preview} />
              ) : (
                <View style={styles.placeholder}>
                  <AntDesign name="idcard" size={48} color="#aaa" />
                  <Text style={styles.placeholderText}>
                    Your ID image will appear here
                  </Text>
                </View>
              )}

              <TouchableOpacity style={styles.captureButton} onPress={handlePickImage}>
                <Text style={styles.captureText}>📷 Take Photo</Text>
              </TouchableOpacity>

              {isProcessing && (
                <View style={styles.processingContainer}>
                  <Animated.View
                    style={[
                      styles.processingSpinner,
                      {
                        transform: [
                          {
                            rotate: spinValue.interpolate({
                              inputRange: [0, 1],
                              outputRange: ['0deg', '360deg'],
                            }),
                          },
                        ],
                      },
                    ]}
                  >
                    <AntDesign name="loading1" size={32} color="#007AFF" />
                  </Animated.View>
                  <Text style={styles.processingText}>Processing your ID...</Text>
                  <Text style={styles.processingSubtext}>Please wait while we verify your information</Text>
                </View>
              )}

              {result && !isProcessing && (
                <View style={styles.resultContainer}>
                  {verified ? (
                    <View style={styles.verifiedResult}>
                      <View style={styles.statusHeader}>
                        <AntDesign name="checkcircle" size={24} color="#28a745" />
                        <Text style={styles.statusTitle}>✅ Verified Successfully!</Text>
                      </View>
                      <View style={styles.userInfoCard}>
                        <View style={styles.infoRow}>
                          <Text style={styles.infoLabel}>👤 Name:</Text>
                          <Text style={styles.infoValue}>{result.name}</Text>
                        </View>
                        <View style={styles.infoRow}>
                          <Text style={styles.infoLabel}>🏢 Department:</Text>
                          <Text style={styles.infoValue}>{result.department}</Text>
                        </View>
                        <View style={[styles.infoRow, { borderBottomWidth: 0 }]}>
                          <Text style={styles.infoLabel}>🆔 P.No:</Text>
                          <Text style={styles.infoValue}>{result.pno}</Text>
                        </View>
                      </View>
                    </View>
                  ) : (
                    <View style={styles.notVerifiedResult}>
                      <View style={styles.statusHeader}>
                        <AntDesign name="closecircle" size={24} color="#dc3545" />
                        <Text style={styles.statusTitleError}>❌ Not Verified</Text>
                      </View>
                      <View style={styles.errorInfoCard}>
                        <Text style={styles.errorLabel}>Detected text:</Text>
                        <Text style={styles.errorValue}>
                          {result.detected && result.detected.length > 0
                            ? result.detected.join(", ")
                            : "No text detected"}
                        </Text>
                      </View>
                    </View>
                  )}
                </View>
              )}

              {image && !isProcessing && (
                <View style={styles.bottomButtonContainer}>
                  <TouchableOpacity
                    style={[styles.captureButton, styles.backButton]}
                    onPress={() => router.back()}
                  >
                    <AntDesign name="arrowleft" size={20} color="#fff" />
                    <Text style={styles.captureText}> Go Back</Text>
                  </TouchableOpacity>

                  {verified && (
                    <TouchableOpacity
                      style={[styles.captureButton, styles.proceedBtn]}
                      onPress={() => router.push("/home")}
                    >
                      <Text style={styles.captureText}>Proceed </Text>
                      <AntDesign name="arrowright" size={20} color="#fff" />
                    </TouchableOpacity>
                  )}
                </View>
              )}


            </View>
          </ScrollView>
        </KeyboardAvoidingView>
      </BlurView>
    </ImageBackground>
  </SafeAreaView>
);

}

const styles = StyleSheet.create({
  backgroundImage: {
    flex: 1,
    width: "100%",
    height: "100%",
  },
  bottomButtonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 24,
    paddingBottom: 24,
    width: '100%',
    gap: 10,
  },

  blurContainer: {
    flex: 1,
  },
  container: {
    flex: 1,
    padding: 24,
    justifyContent: "center",
    alignItems: "center",
    position: "relative",
  },
  title: {
    fontSize: 26,
    fontWeight: "700",
    marginBottom: 30,
    color: "#333",
  },
  preview: {
    width: 260,
    height: 180,
    borderRadius: 12,
    marginBottom: 20,
    borderWidth: 2,
    borderColor: "#fff",
  },
  placeholder: {
    width: 260,
    height: 180,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: "#fff",
    backgroundColor: "rgba(240, 240, 240, 0.9)",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 20,
  },
  placeholderText: {
    color: "#666",
    marginTop: 8,
    textAlign: "center",
    fontWeight: "500",
  },
  captureButton: {
    backgroundColor: "#007AFF",
    paddingVertical: 14,
    paddingHorizontal: 32,
    borderRadius: 12,
    marginBottom: 10,
  },
  captureText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
  backButton: {
    backgroundColor: "#28a745",
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    flex: 1,
  },
  backText: {
    color: "#fff",
    fontSize: 18,
    marginLeft: 8,
    fontWeight: "500",
  },
  processingContainer: {
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 30,
    paddingHorizontal: 20,
    backgroundColor: "rgba(255, 255, 255, 0.95)",
    borderRadius: 16,
    marginTop: 20,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  processingSpinner: {
    marginBottom: 15,
  },
  processingText: {
    fontSize: 18,
    fontWeight: "600",
    color: "#333",
    marginBottom: 8,
    textAlign: "center",
  },
  processingSubtext: {
    fontSize: 14,
    color: "#666",
    textAlign: "center",
    lineHeight: 20,
  },
  resultText: {
    marginTop: 15,
    fontSize: 16,
    fontWeight: "600",
    textAlign: "center",
    backgroundColor: "rgba(255,255,255,0.8)",
    padding: 10,
    borderRadius: 8,
  },
  resultContainer: {
    width: "100%",
    marginTop: 20,
    paddingHorizontal: 20,
  },
  verifiedResult: {
    backgroundColor: "rgba(255,255,255,0.95)",
    borderRadius: 16,
    padding: 20,
    borderLeftWidth: 5,
    borderLeftColor: "#28a745",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  notVerifiedResult: {
    backgroundColor: "rgba(255,255,255,0.95)",
    borderRadius: 16,
    padding: 20,
    borderLeftWidth: 5,
    borderLeftColor: "#dc3545",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statusHeader: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 15,
  },
  statusTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: "#28a745",
    marginLeft: 8,
  },
  statusTitleError: {
    fontSize: 18,
    fontWeight: "700",
    color: "#dc3545",
    marginLeft: 8,
  },
  userInfoCard: {
    backgroundColor: "#f8f9fa",
    borderRadius: 12,
    padding: 15,
  },
  errorInfoCard: {
    backgroundColor: "#fff5f5",
    borderRadius: 12,
    padding: 15,
  },
  infoRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: "#e9ecef",
  },
  infoLabel: {
    fontSize: 16,
    fontWeight: "600",
    color: "#495057",
    flex: 1,
  },
  scrollContainer: {
    flexGrow: 1,
    justifyContent: "center",
    paddingBottom: 50,  // buffer for Android navbar
  },

  infoValue: {
    fontSize: 16,
    fontWeight: "500",
    color: "#212529",
    flex: 2,
    textAlign: "right",
  },
  errorLabel: {
    fontSize: 16,
    fontWeight: "600",
    color: "#6c757d",
    marginBottom: 8,
  },
  errorValue: {
    fontSize: 14,
    color: "#dc3545",
    fontStyle: "italic",
    lineHeight: 20,
  },
  proceedBtn: {
    backgroundColor: "#007AFF",
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    flex: 1,
  },
});
