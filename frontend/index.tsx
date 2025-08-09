import { useRouter } from 'expo-router';
import * as SystemUI from 'expo-system-ui';
import React, { useEffect } from 'react';
import {
  BackHandler,
  Image,
  ImageBackground,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';

export default function WelcomeScreen() {
  
  const router = useRouter();

  useEffect(() => {
    SystemUI.setBackgroundColorAsync('transparent');
  }, []);

  const handleExit = () => {
    BackHandler.exitApp();
  };

  // ✅ Backend Test on First Load

  return (
    <ImageBackground
      source={require('../assets/sexypic.jpg')} // 🔁 Background image
      style={styles.background}
      imageStyle={{ opacity: 0.3 }}
    >
      <View style={styles.overlay}>
        <Image
          source={require('../assets/logo.png')} // 🔁 Logo at top (optional)
          style={styles.logo}
          resizeMode="contain"
        />

        <Text style={styles.welcomeText}>Welcome to CAL Line OXO Verification</Text>

        <TouchableOpacity style={styles.button} onPress={() => router.push('/scanperson')}>
          <Text style={styles.buttonText}>📷 Start</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.button} onPress={() => router.push('/settings')}>
          <Text style={styles.buttonText}>⚙️ Settings</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, { backgroundColor: '#ff4d4d' }]}
          onPress={handleExit}
        >
          <Text style={styles.buttonText}>❌ Exit</Text>
        </TouchableOpacity>

        {/* Footer */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>Powered by</Text>
          <Image
            source={require('../assets/poweredbylogo.png')} // 🔁 Small logo at bottom
            style={styles.footerLogo}
            resizeMode="contain"
          />
        </View>
      </View>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  background: {
    flex: 1,
    width: '100%',
    height: '100%',
  },
  overlay: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  logo: {
    width: 160,
    height: 160,
    marginBottom: 10,
  },
  welcomeText: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 30,
    textAlign: 'center',
    color: '#333',
  },
  button: {
    width: '80%',
    backgroundColor: '#007AFF',
    paddingVertical: 14,
    borderRadius: 10,
    marginBottom: 16,
    alignItems: 'center',
    elevation: 3,
  },
  buttonText: {
    color: '#fff',
    fontSize: 17,
    fontWeight: '600',
  },
  footer: {
    position: 'absolute',
    bottom: 15,
    alignItems: 'center',
    opacity: 0.8,
  },
  footerText: {
    fontSize: 12,
    color: '#888',
    marginBottom: 2,
  },
  footerLogo: {
    width: 80,
    height: 20,
  },
});
