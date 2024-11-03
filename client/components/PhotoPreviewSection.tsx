import { Fontisto } from '@expo/vector-icons';
import { CameraCapturedPicture } from 'expo-camera';
import React from 'react';
import { TouchableOpacity, SafeAreaView, Image, StyleSheet, View } from 'react-native';

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
                Accept: 'application/json',
            },
        });

        const result = await response.json();
        console.log('Upload result:', result);
    } catch (error) {
        console.error('Error uploading image:', error);
    }
};

const PhotoPreviewSection = ({
    photo,
    handleRetakePhoto,
}: {
    photo: CameraCapturedPicture;
    handleRetakePhoto: () => void;
}) => {
    // Extract the image URI directly from the photo prop
    const imageUri = photo.uri || `data:image/jpg;base64,${photo.base64}`; // Use the URI or fall back to base64

    return (
        <SafeAreaView style={styles.container}>
            <View style={styles.box}>
                <Image
                    style={styles.previewContainer}
                    source={{ uri: imageUri }}
                />
            </View>

            <View style={styles.buttonContainer}>
                <TouchableOpacity style={styles.button} onPress={handleRetakePhoto}>
                    <Fontisto name='trash' size={36} color='black' />
                </TouchableOpacity>
                <TouchableOpacity
                    style={styles.button}
                    onPress={() => uploadImage(imageUri)} // Pass the image URI here
                >
                    <Fontisto name='home' size={36} color='black'/>
                </TouchableOpacity>
            </View>
        </SafeAreaView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: 'black',
        alignItems: 'center',
        justifyContent: 'center',
    },
    box: {
        borderRadius: 15,
        padding: 1,
        width: '95%',
        backgroundColor: 'darkgray',
        justifyContent: 'center',
        alignItems: 'center',
    },
    previewContainer: { // Fixed typo from 'previewConatiner' to 'previewContainer'
        width: '95%',
        height: '85%',
        borderRadius: 15,
    },
    buttonContainer: {
        marginTop: '4%',
        flexDirection: 'row',
        justifyContent: "center",
        width: '100%',
    },
    button: {
        backgroundColor: 'gray',
        borderRadius: 25,
        padding: 10,
        alignItems: 'center',
        justifyContent: 'center',
    }
});

export default PhotoPreviewSection;
