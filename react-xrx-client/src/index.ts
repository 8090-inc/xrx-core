import { useState, useRef, useCallback, useEffect } from 'react';

interface xRxProps {
  orchestrator_host: string;
  orchestrator_port: string;
  orchestrator_path: string;
  greeting_filename: string;
  orchestrator_ssl: boolean;
  tts_sample_rate: number;
  stt_sample_rate: number;
}

type ChatMessage = {
  sender: string;
  message: string;
  widget?: any;
  timestamp: Date;
  type?: string;
};
  
const xRxClient = ({
  orchestrator_host = 'localhost',
  orchestrator_port = '8090',
  orchestrator_path = '/api/v1/ws',
  greeting_filename = 'greeting.mp3',
  orchestrator_ssl = false,
  tts_sample_rate = 16000,
  stt_sample_rate = 16000
}: xRxProps) => {  
  const recordingContextRef = useRef<AudioContext | null>(null);
  const playbackContextRef = useRef<AudioContext | null>(null);
  const [isAudioContextStarted, setIsAudioContextStarted] = useState(false);
  const incomingAudioBufferRef = useRef<ArrayBuffer[]>([]);
  const isPlayingAudioRef = useRef(false);
  
  const [isRecording, setIsRecording] = useState(false);
  const [isVoiceMode, setIsVoiceMode] = useState(true);
  const [isUserSpeaking, setIsUserSpeaking] = useState(false);
  const isUserSpeakingRef = useRef(false);

  const mediaRecorderRef = useRef<ScriptProcessorNode | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const socketRef = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const [isAgentSpeaking, setIsAgentSpeaking] = useState(false);
  const [isAgentThinking, setIsAgentThinking] = useState(false);
  const [isAudioPlaying, setIsAudioPlaying] = useState(false);
  const currentBufferSourceRef = useRef<AudioBufferSourceNode | null>(null);

  const [showStartButton, setShowStartButton] = useState(true);
  const [isAudioGenerationDone, setIsAudioGenerationDone] = useState(false);

  const widgetQueueRef = useRef<ChatMessage[]>([]); // queue used for widgets to make them play at the right time

  useEffect(() => {
    isUserSpeakingRef.current = isUserSpeaking;
  }, [isUserSpeaking]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  const iconAnimationTimeout = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    scrollToBottom()
  }, [chatHistory]);

  const playReceivedAudio = useCallback((arrayBuffer: ArrayBuffer | null) => {
    if (playbackContextRef.current) {
      if (arrayBuffer !== null && !isUserSpeakingRef.current) {
        incomingAudioBufferRef.current.push(arrayBuffer as ArrayBuffer);
      }
      if (incomingAudioBufferRef.current.length > 0 && !isPlayingAudioRef.current && !isUserSpeakingRef.current) {

        const audioData = incomingAudioBufferRef.current.shift() as ArrayBuffer;
        const int16Array = new Int16Array(audioData);

        if (!isAgentSpeaking) {
          setIsAgentSpeaking(true);
          console.log("starting icon animation");
        }
        const durationSec = (int16Array.length / tts_sample_rate);
        console.log("received audio of duration : " + durationSec);
        if (iconAnimationTimeout.current) {
          clearTimeout(iconAnimationTimeout.current as NodeJS.Timeout);
        }
        iconAnimationTimeout.current = setTimeout(() => {
          console.log("stopping icon animation");
          setIsAgentSpeaking(false);
        }, durationSec * 1000);

        const float32Array = new Float32Array(int16Array.length);
        for (let i = 0; i < int16Array.length; i++) {
          float32Array[i] = int16Array[i] / 0x8000;
        }

        const channels = 1;
        const buffer = playbackContextRef.current.createBuffer(channels, float32Array.length, tts_sample_rate);
        buffer.getChannelData(0).set(float32Array);

        const source = playbackContextRef.current.createBufferSource();
        source.buffer = buffer;
        source.connect(playbackContextRef.current.destination);
        source.start();
        currentBufferSourceRef.current = source; // Store the reference to the current BufferSource
        console.log("start playing audio");
        isPlayingAudioRef.current = true;
        setIsAudioPlaying(true);
        console.log("isPlayingAudioRef.current after start:", isPlayingAudioRef.current);
        source.onended = () => {
          source.disconnect();
          isPlayingAudioRef.current = false;
          console.log("end playing audio");
          setIsAudioPlaying(false);
          console.log("isPlayingAudioRef.current after end:", isPlayingAudioRef.current);
          playReceivedAudio(null);
          processWidgetQueue();
        }
      }
    }
  }, [isAgentSpeaking, isUserSpeaking, isPlayingAudioRef, isUserSpeakingRef]);


  const processWidgetQueue = () => {
    console.log(`processing the widget queue with length: ${widgetQueueRef.current.length}`);
    while (widgetQueueRef.current.length > 0 && !isPlayingAudioRef.current) {
      const widgetMessage = widgetQueueRef.current.shift();
      if (widgetMessage) {
        setChatHistory(currentChatHistory => [
          ...currentChatHistory,
          widgetMessage
        ]);
      }
    }
  };

  const sendAction = async (tool: string, parameters: any) => {
    try {
      if (socketRef.current) {
        const payload = {
          type: "action",
          content: {
            tool: tool,
            parameters: JSON.stringify(parameters)
          },
          modality: isVoiceMode ? "audio" : "text"
        };
        socketRef.current.send(JSON.stringify(payload));
        console.log("Action sent successfully:", payload);
      }
    } catch (error) {
      console.error("Error sending action to backend:", error);
    }
  };

  const sendMessage = (message: string) => {
    if (socketRef.current) {
      socketRef.current.send(message);

      setChatHistory(currentChatHistory => [
        ...currentChatHistory,
        { sender: 'user', message: `${message}`, timestamp: new Date() }
      ]);
    }
  };

  useEffect(() => {
    if (!socketRef.current) {

      const protocol = orchestrator_ssl ? 'wss' : 'ws';
      const socket = new WebSocket(`${protocol}://${orchestrator_host}:${orchestrator_port}${orchestrator_path}`);
      socketRef.current = socket;
      socket.binaryType = 'arraybuffer';

      socket.onopen = () => {
        console.log("WebSocket connection established");
      };

      socketRef.current.onmessage = (event) => {
        console.log("Message received from server :" + event);
        if (typeof event.data === 'string') {
          const message = JSON.parse(event.data);
          let content, widget:any;
          if (message.type === 'widget') {
            console.log(`widget received from server side and audio playing has value: ${isPlayingAudioRef.current}`);
            widget = message.content;
            content = '';
            
            if (isPlayingAudioRef.current) {
              // Enqueue the widget message if audio is playing
              console.log(`queuing the widget message`);
              widgetQueueRef.current.push({
                sender: message.user,
                type: message.type,
                message: message.content,
                timestamp: new Date()
              });
              console.log(`widget queue length: ${widgetQueueRef.current.length}`);
            } else {
              // Display the widget message immediately if audio is not playing
              setChatHistory(currentChatHistory => [
                ...currentChatHistory,
                { sender: message.user, type: message.type, message: message.content, timestamp: new Date() }
              ]);
            }
          } else if(message.type === 'action') {
            if(message.content === 'agent_started_thinking') {
              setIsAgentThinking(true);
            } else if(message.content === 'agent_ended_thinking') {
              // wait a small amount of time here before making this change to allow for better animation
              setTimeout(() => {
                setIsAgentThinking(false);
              }, 800);
            }

            // determine if the audio has been generated which is currently playing
            if(message.content === 'audio_generation_done') {
              console.log(`audio generation done from server side and audio playing has value: ${isPlayingAudioRef.current}`);
              setIsAudioGenerationDone(true);
            }

            // perform action such as cancel audio.
            if(message.content === 'clear_audio_buffer') {
              console.log("Clearing audio buffer");
              incomingAudioBufferRef.current = [];
              setIsAudioPlaying(false);
            }
            return; // do not continue or set the chat history
          }
          else {
            content = message.content;
            setChatHistory(currentChatHistory => [
              ...currentChatHistory,
              { sender: message.user, type: message.type, message: message.content, timestamp: new Date() }
            ]);
          }

        } else if (event.data instanceof ArrayBuffer) {
          // Handle binary messages
          console.log("Binary message received, starting audio playback");
          playReceivedAudio(event.data);
        }
      }

      socket.onerror = (error) => {
        console.error("WebSocket error:", error);
      };

      socket.onclose = () => {
        console.log("WebSocket connection closed");
      };

    };
  }, [playReceivedAudio, isUserSpeaking]);

  const sendPCMData = useCallback((pcmData: Int16Array) => {
    // Send PCM data to the WebSocket server if the connection is open
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(pcmData.buffer);
    }
  }, [socketRef.current]);

  const startAudioCapture = useCallback(async () => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      console.error("MediaDevices are not supported by this browser.");
      return;
    }

    if (!recordingContextRef.current) {
      recordingContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)({
        sampleRate: stt_sample_rate
      });
      console.log(`AudioContext CREATED ${recordingContextRef.current}`);
    } else {
      await recordingContextRef.current.resume();
      console.log(`AudioContext RESUMED ${recordingContextRef.current}`);
    }

    setIsAudioContextStarted(true);

    // Request permission to access the microphone and get the audio stream
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        noiseSuppression: true,
        autoGainControl: true,
        echoCancellation: true
      }
    });
    let track = stream.getAudioTracks()[0];

    // Create a MediaStreamSource from the audio stream
    const mediaStreamSource = recordingContextRef.current.createMediaStreamSource(stream);
    mediaStreamRef.current = stream;

    // Create a ScriptProcessorNode to process the audio data
    const scriptProcessor = recordingContextRef.current.createScriptProcessor(4096, 1, 1);
    mediaRecorderRef.current = scriptProcessor; // Store the reference

    // Connect the media stream source to the script processor
    mediaStreamSource.connect(scriptProcessor);

    // Connect the script processor to the audio context destination (speakers)
    scriptProcessor.connect(recordingContextRef.current.destination);

    // Event handler for processing the audio data
    scriptProcessor.onaudioprocess = (audioProcessingEvent) => {
      const inputBuffer = audioProcessingEvent.inputBuffer;

      for (let channel = 0; channel < inputBuffer.numberOfChannels; channel++) {
        const inputData = inputBuffer.getChannelData(channel);
        const pcmData = new Int16Array(inputData.length);

        // Convert Float32Array data to Int16Array data
        for (let sample = 0; sample < inputData.length; sample++) {
          const normalizedSample = Math.max(-1, Math.min(1, inputData[sample]));
          pcmData[sample] = normalizedSample < 0
            ? normalizedSample * 0x8000
            : normalizedSample * 0x7FFF;
        }

        // Send PCM data to WebSocket server
        sendPCMData(pcmData);
      }
    };
  }, [sendPCMData]);

  const stopAudioCapture = useCallback(() => {
    if (recordingContextRef.current) {
      // Disconnect the script processor from the audio context's destination
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.disconnect();
        mediaRecorderRef.current.onaudioprocess = null; // Clear the event handler
        mediaRecorderRef.current = null; // Clear the reference
      }

      // Suspend the audio context instead of closing it
      recordingContextRef.current.suspend().then(() => {
        console.log("AudioContext suspended");
      });
    }

    setIsRecording(false);
  }, [recordingContextRef, mediaStreamRef]);

  useEffect(() => {
    if(!playbackContextRef.current) {
      playbackContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)({
        sampleRate: tts_sample_rate
      });
    }
    if (!isRecording) {
      stopAudioCapture();
    } else {
      setIsAudioContextStarted(false);
      startAudioCapture();
    }
  }, [isRecording, startAudioCapture, stopAudioCapture]);
  
  const startAgent = useCallback(() => {
    const audio = new Audio(`/${greeting_filename}`);
    audio.play();
    setIsAgentSpeaking(true);
    audio.onended = () => {
      setIsAgentSpeaking(false);
      setIsRecording(true);
    }
    setShowStartButton(false);

  }, [isRecording, isAgentSpeaking]);
  

  const toggleVoiceMode = useCallback(() => {
    if(isVoiceMode === true) {
      setIsVoiceMode(false);
      setIsRecording(false);
      setShowStartButton(false);
    } else {
      setIsVoiceMode(true);
    }
  }, [isVoiceMode, setIsVoiceMode, isRecording, setIsRecording]);

  const toggleIsRecording = useCallback(() => {
    if(isRecording === true) {
      setIsRecording(false);
    } else {
      setIsRecording(true);
    }
  }, [isRecording, setIsRecording]);

  return {
    // State variables
    isRecording,
    isVoiceMode,
    isUserSpeaking,
    chatHistory,
    isAgentSpeaking,
    isAgentThinking,
    isAudioPlaying,
    showStartButton,
    isAudioGenerationDone,

  
    // Set functions
    setIsRecording,
    setIsVoiceMode,
    setIsUserSpeaking,
    setChatHistory,
    setIsAgentSpeaking,
    setIsAgentThinking,
    setIsAudioPlaying,
    setShowStartButton,
    setIsAudioGenerationDone,

  
    // Handler functions
    startAgent,
    toggleIsRecording,
    toggleVoiceMode,
    sendMessage,
    sendAction
  };

};

export default xRxClient;
export type { ChatMessage };


