import os
import azure.cognitiveservices.speech as speechsdk
import dotenv

dotenv.load_dotenv()


def synthesize_speech(
    text: str,
    voice_name: str = "en-US-AvaMultilingualNeural",
    style: str = "general",
    rate: str = "0%"
):
    """
    合成语音并返回音频数据。

    参数：
    - text (str): 要合成的文本。
    - voice_name (str): 使用的语音名称。
    - style (str): 语音风格。
    - rate (str): 语速，默认为"0%"

    返回：
    - bytes: 合成的音频数据。
    """
    speech_config = speechsdk.SpeechConfig(
        subscription=os.environ.get('AZURE_SPEECH_KEY'),
        region=os.environ.get('AZURE_SPEECH_REGION')
    )

    # 设置语音和输出格式
    speech_config.speech_synthesis_voice_name = voice_name
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm
    )

    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=None
    )

    ssml_string = f"""
    <speak version="1.0"
           xmlns="http://www.w3.org/2001/10/synthesis"
           xmlns:mstts="http://www.w3.org/2001/mstts"
           xml:lang="en-US">
        <voice name="{voice_name}">
            <mstts:express-as style="{style}">
                <prosody rate="{rate}">
                    {text}
                </prosody>
            </mstts:express-as>
        </voice>
    </speak>
    """

    speech_synthesis_result = speech_synthesizer.speak_ssml_async(
        ssml_string
    ).get()

    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        # 获取音频数据
        audio_data = speech_synthesis_result.audio_data
        return audio_data
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print(f"语音合成被取消: {cancellation_details.reason}")
        if (
            cancellation_details.reason == speechsdk.CancellationReason.Error
            and cancellation_details.error_details
        ):
            print(f"错误详情: {cancellation_details.error_details}")
            print("请检查您的语音服务密钥和区域设置。")
        return None
    else:
        print("生成语音时发生错误。")
        return None


if __name__ == "__main__":
    text_input = "I'm really angry at this situation. I need to calm down and think clearly."
    # 使用默认语速
    audio_data = synthesize_speech(text_input)
    if audio_data:
        # 将音频数据保存为文件，供测试
        with open("output_default_rate.wav", "wb") as f:
            f.write(audio_data)
        print("音频已生成并保存为output_default_rate.wav")

    # 调整语速为比默认慢10%
    audio_data_slow = synthesize_speech(text_input, rate="-10%")
    if audio_data_slow:
        with open("output_slow_rate.wav", "wb") as f:
            f.write(audio_data_slow)
        print("音频已生成并保存为output_slow_rate.wav")
