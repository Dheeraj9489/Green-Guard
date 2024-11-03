import React, { useEffect, useState } from 'react';
import { View, Text, Button, Alert } from 'react-native';
import * as Location from 'expo-location';
import axios from 'axios';
import { useNavigation } from '@react-navigation/native';
import {useRouter, useLocalSearchParams} from "expo-router";

const PlantInfoComponent = () => {
  // Sample JSON data
  const [plantData, setPlantData] = useState({ plant: 'Tomato', disease: 'Blight' });
  const router = useRouter();
  const { plant, disease } = useLocalSearchParams();

  const handleGetLocationAndSubmit = async () => {
    // Request permission to access location
    let { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission to access location was denied');
      return;
    }

    // Get current location
    let location = await Location.getCurrentPositionAsync({});
    const { latitude, longitude } = location.coords;

    // Prepare data for the API call
    const payload = {
      plant,
      disease,
      latitude,
      longitude,
    };

    // Replace with your API endpoint
    const apiEndpoint = 'http://192.168.135.206:5001/report';


    try {
      // Make the API call
      const response = await fetch(apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('Error:', errorData);
        Alert.alert('Error', `Failed to submit data: ${errorData.message || response.statusText}`);
      } else {
        const responseData = await response.json();
        Alert.alert('Success', responseData.message);
      }
    } catch (error) {
      console.error(error);
      Alert.alert('Error', 'Something went wrong while submitting the data.');
    }

    // Navigate back to the previous tab
    router.back();
  };

  const handleGoBack = () => {
    // Just navigate back to the previous tab
    router.back();
  };

  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', padding: 16 }}>
      <Text style={{ fontSize: 20, fontWeight: 'bold' }}>Plant Information</Text>
      <Text>Plant: {plantData.plant}</Text>
      <Text>Disease: {plantData.disease}</Text>

      <View style={{ marginVertical: 20 }}>
        <Button title="Get Location and Submit" onPress={handleGetLocationAndSubmit} />
      </View>
      <Button title="Go Back" onPress={handleGoBack} />
    </View>
  );
};

export default PlantInfoComponent;
