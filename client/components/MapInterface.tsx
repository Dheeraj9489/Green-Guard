import React, { useEffect, useState } from 'react';
import MapView, { Marker } from 'react-native-maps';
import {ActivityIndicator, StyleSheet, View} from 'react-native';
import * as Location from 'expo-location';
import { useFocusEffect } from '@react-navigation/native';

type MarkerData = {
  plant: string;
  disease: string;
  latitude: number;
  longitude: number;
};

export function MapInterface() {
  const [markers, setMarkers] = useState<MarkerData[]>([]);
  const [userLocation, setUserLocation] = useState<{ latitude: number; longitude: number } | null>(null);
  const [loading, setLoading] = useState(true);

  const requestLocationPermission = async () => {
    const { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== 'granted') {
      alert('Permission to access location was denied');
      return false;
    }
    return true;
  };

  const getUserLocation = async () => {
    let location = await Location.getCurrentPositionAsync({});
    const { latitude, longitude } = location.coords;
    // const location = await Location.getCurrentPositionAsync({});
    setUserLocation({
      latitude: latitude,
      longitude: longitude
    });
  };

  useEffect(() => {
    const fetchMarkers = async () => {
  try {
    const response = await fetch('http://192.168.135.206:5001/get_reports'); // CHANGE WHEN SERVER CHANGES
    if (response.ok) {
      const data = await response.json();

      // Convert latitude and longitude to numbers
      const formattedData = data.map((item: { plant: string; disease: string; latitude: string; longitude: string; }) => ({
        plant: item.plant,
        disease: item.disease,
        latitude: parseFloat(item.latitude),  // Convert to number
        longitude: parseFloat(item.longitude) // Convert to number
      }));

      setMarkers(formattedData);
    } else {
      console.error('Failed to fetch markers:', response.statusText);
    }
  } catch (error) {
    console.error('Error fetching markers:', error);
  }
};


    const initializeMap = async () => {
      const hasPermission = await requestLocationPermission();
      if (hasPermission) {
        await getUserLocation();
        await fetchMarkers();
        setLoading(false);
      }
    };

    initializeMap();
  }, []);

  if (loading){
    return(
        <View >
          <ActivityIndicator size="large" color="#0000ff" />
        </View>
    );
  }


  return (
    <View style={styles.container}>
      <MapView
        style={styles.map}
        initialRegion={{
          latitude: userLocation ? userLocation.latitude : 34.945850, // Default to Mizzou
          longitude: userLocation ? userLocation.longitude : -92.329531,
          latitudeDelta: 0.1,
          longitudeDelta: 0.1,
        }}
      >
        {markers.map((marker, index) => (
          <Marker
            key={index}
            coordinate={{
              latitude: marker.latitude,
              longitude: marker.longitude,
            }}
            title={marker.plant}
            description={marker.disease}
          />
        ))}
      </MapView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  map: {
    width: '100%',
    height: '100%',
  },
});

export default MapInterface;
