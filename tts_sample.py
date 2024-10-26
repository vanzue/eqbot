import os
import azure.cognitiveservices.speech as speechsdk
import dotenv
import wave

dotenv.load_dotenv()

def synthesize_speech(text: str, voice_name: str = "en-US-AvaMultilingualNeural", style: str = "general"):
    """
    Synthesizes speech from the given text and uploads it to Azure Blob Storage.

    Parameters:
    - text (str): The text to be synthesized into speech.
    - container_name (str): The name of the blob container where the audio will be uploaded.
    - blob_name (str): The name of the blob where the audio will be stored.
    - voice_name (str): The voice to use for synthesis (default is "en-US-AvaMultilingualNeural").
    - style (str): The speaking style (e.g., "cheerful", "sad", "angry", etc., default is "general").
    """
    # Set up the Speech Configuration with your Azure Speech Service subscription key and region
    speech_config = speechsdk.SpeechConfig(
        subscription=os.environ.get('AZURE_SPEECH_KEY'), 
        region=os.environ.get('AZURE_SPEECH_REGION')
    )

    # Set the voice for the speech synthesis
    speech_config.speech_synthesis_voice_name = voice_name

    # Create the Speech Synthesizer with the given configurations
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

    # Define SSML structure to include voice and style
    ssml_string = f"""
    <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="en-US">
        <voice name="{voice_name}">
            <mstts:express-as style="{style}">
                {text}
            </mstts:express-as>
        </voice>
    </speak>
    """

    # Perform the speech synthesis using SSML to apply the style
    speech_synthesis_result = speech_synthesizer.speak_ssml_async(ssml_string).get()

    # Check the result of the synthesis
    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        # Retrieve the audio data from the result
        audio_stream = speechsdk.AudioDataStream(speech_synthesis_result)
        audio_data = bytearray()
        buffer = bytes(4096)
        
        while True:
            read_size = audio_stream.read_data(buffer)
            if read_size == 0:
                break
            audio_data.extend(buffer[:read_size])
        
        return audio_data
        
    
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print(f"Error details: {cancellation_details.error_details}")
                print("Did you set the speech resource key and region values?")
        return None
    print("Error happened generating voice.")
    return None


def save_audio_to_wav(audio_data: bytearray, filename: str = "output.wav"):
    """
    Save the given audio data as a .wav file.

    Parameters:
    - audio_data (bytearray): The synthesized audio data.
    - filename (str): The filename for the .wav file.
    """
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)  # Mono channel
        wf.setsampwidth(2)  # Sample width in bytes (16-bit)
        wf.setframerate(24000)  # Sample rate
        wf.writeframes(audio_data)

# Example usage of the function
if __name__ == "__main__":
    # Example text and blob details
    text_input = "I'm really angry at this situation. I need to calm down and think clearly."
    result = synthesize_speech(text_input)
    save_audio_to_wav(result)
