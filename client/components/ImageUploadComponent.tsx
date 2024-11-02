import React, { useState } from 'react';
import { Button, Image, View } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import ImageCropPicker from 'react-native-image-crop-picker';

const ImageUploadComponent = () => {
  const [imageUri, setImageUri] = useState<string | null>(null);

  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3],
      quality: 1,
    });

    if (!result.canceled) {
      setImageUri(result.assets[0].uri);
      await uploadImage(result.assets[0].uri);
    }
  };

  const uploadImage = async (imagePath: string) => {
    const formData = new FormData();

    formData.append('image', {
      uri: imagePath,
      name: 'upload.jpg',
      type: 'image/jpeg',
    } as any);

    try {
      const response = await fetch('http://192.168.135.206:5001/upload', {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json',
        },
      });

      const result = await response.json();
      console.log('Upload result:', result);
    } catch (error) {
      console.error('Error uploading image:', error);
    }
  };

  return (
    <View>
      <Button title="Pick an Image" onPress={pickImage} />
      {imageUri && <Image source={{ uri: imageUri }} style={{ width: 256, height: 256 }} />}
    </View>
  );
};

export default ImageUploadComponent;