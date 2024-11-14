import pyaudio
import asyncio
from deepgram import DeepgramClient, LiveTranscriptionEvents,LiveOptions
from config import DEEPGRAM_API_KEY

# Audio recording settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024 

# Async function to stream audio to Deepgram in real-time
async def transcribe_stream():
    # Open audio stream
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True, frames_per_buffer=CHUNK)
    print("Recording started... Speak into the microphone.")

    try:
        deepgram: DeepgramClient = DeepgramClient(DEEPGRAM_API_KEY)
        dg_connection = deepgram.listen.websocket.v("1")
        
        def process_transcript(self, result, **kwargs):
            # print(result)
            if result.channel:
                transcript = result.channel.alternatives[0].transcript
                words = transcript.split()
                for word in words:
                    print(word, end=' ', flush=True)
                # print("Transcript:", transcript)
                
        dg_connection.on(LiveTranscriptionEvents.Transcript, process_transcript)
        
        options = LiveOptions(model="nova-2", 
                              language="multi", 
                              encoding="linear16", 
                              sample_rate=RATE, 
                              interim_results = False)
        
        if dg_connection.start(options) is False:
            print("Failed to start Deepgram connection")
            raise Exception("Deepgram connection failed")
        else:
            print("Deepgram Connection Successful")
            
        while True:
            # Read audio data from the microphone
            data = stream.read(CHUNK, exception_on_overflow=False)
            # Send the audio chunk to Deepgram
            dg_connection.send(data)

    except KeyboardInterrupt:
        print("Stopping transcription.")
        
    finally:
        # Stop audio stream and close connection
        dg_connection.finish()
        stream.stop_stream()
        stream.close()
        audio.terminate()

asyncio.run(transcribe_stream())
