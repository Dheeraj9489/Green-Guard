import Ionicons from '@expo/vector-icons/Ionicons';
import { StyleSheet, Image, Platform , View} from 'react-native';
import MapView from 'react-native-maps';
import { Collapsible } from '@/components/Collapsible';
import { ExternalLink } from '@/components/ExternalLink';
import ParallaxScrollView from '@/components/ParallaxScrollView';
import { ThemedText } from '@/components/ThemedText';
import { ThemedView } from '@/components/ThemedView';
import { MapInterface } from '@/components/MapInterface';


export default function TabTwoScreen() {

  return (
    <MapInterface />
  );
}

const styles = StyleSheet.create({
  headerImage: {
    color: '#808080',
    bottom: -90,
    left: -35,
    position: 'absolute',
  },
  titleContainer: {
    flexDirection: 'row',
    gap: 8,
  },
});
