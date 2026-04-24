# voiceagent/app/routers/calls.py
import logging
import json
from fastapi import APIRouter, Request, Response
from azure.communication.callautomation import (
    CallAutomationClient,
    TextSource,
    RecognizeInputType,
)
from openai import AzureOpenAI

from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/calls", tags=["calls"])

# Initialize clients
acs_client = CallAutomationClient.from_connection_string(
    settings.ACS_CONNECTION_STRING
) if settings.ACS_CONNECTION_STRING else None

openai_client = AzureOpenAI(
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_key=settings.AZURE_OPENAI_API_KEY,
    api_version=settings.AZURE_OPENAI_API_VERSION,
) if settings.AZURE_OPENAI_API_KEY else None

conversation_history: dict = {}


@router.post("/incoming")
async def incoming_call(request: Request):
    body = await request.json()
    logger.info(f"Incoming call event: {json.dumps(body)}")

    for event in body:
        event_type = event.get("type", "")
        event_data = event.get("data", {})

        if event_type == "Microsoft.EventGrid.SubscriptionValidationEvent":
            validation_code = event_data.get("validationCode")
            return {"validationResponse": validation_code}

        if event_type == "Microsoft.Communication.IncomingCall":
            incoming_call_context = event_data.get("incomingCallContext")
            call_id = event_data.get("correlationId", "unknown")
            logger.info(f"Answering call: {call_id}")

            acs_client.answer_call(
                incoming_call_context=incoming_call_context,
                callback_url=f"{settings.CALLBACK_BASE_URL}/calls/events",
            )

            conversation_history[call_id] = [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful AI voice assistant. "
                        "Keep responses short and conversational. "
                        "You are speaking on a phone call."
                    )
                }
            ]

    return Response(status_code=200)


@router.post("/events")
async def call_events(request: Request):
    body = await request.json()
    logger.info(f"Call event received: {json.dumps(body)}")

    for event in body:
        event_type = event.get("type", "")
        event_data = event.get("data", {})
        call_connection_id = event_data.get("callConnectionId")

        if event_type == "Microsoft.Communication.CallConnected":
            logger.info(f"Call connected: {call_connection_id}")
            await _play_greeting(call_connection_id)

        elif event_type == "Microsoft.Communication.RecognizeCompleted":
            speech_result = event_data.get("speechResult", {})
            user_speech = speech_result.get("speech", "")
            call_id = event_data.get("correlationId", "unknown")
            logger.info(f"User said: {user_speech}")
            await _process_speech(call_connection_id, call_id, user_speech)

        elif event_type == "Microsoft.Communication.RecognizeFailed":
            logger.warning(f"Recognize failed: {call_connection_id}")
            await _play_text(
                call_connection_id,
                "I'm sorry, I didn't catch that. Could you please repeat?"
            )

        elif event_type == "Microsoft.Communication.CallDisconnected":
            logger.info(f"Call disconnected: {call_connection_id}")
            call_id = event_data.get("correlationId", "unknown")
            conversation_history.pop(call_id, None)

    return Response(status_code=200)


async def _play_greeting(call_connection_id: str):
    call_connection = acs_client.get_call_connection(call_connection_id)
    call_connection.start_recognizing_media(
        input_type=RecognizeInputType.SPEECH,
        play_prompt=TextSource(
            text="Hello! I'm your AI assistant. How can I help you today?",
            voice_name="en-US-JennyNeural"
        ),
        end_silence_timeout=3,
        callback_url=f"{settings.CALLBACK_BASE_URL}/calls/events",
    )


async def _process_speech(call_connection_id: str, call_id: str, user_speech: str):
    if not openai_client:
        await _play_text(call_connection_id, "AI service is not configured.")
        return

    history = conversation_history.get(call_id, [])
    history.append({"role": "user", "content": user_speech})

    response = openai_client.chat.completions.create(
        model=settings.AZURE_OPENAI_GPT4O_DEPLOYMENT,
        messages=history,
        max_tokens=150,
        temperature=0.7,
    )

    assistant_reply = response.choices[0].message.content
    history.append({"role": "assistant", "content": assistant_reply})
    conversation_history[call_id] = history

    logger.info(f"GPT-4o response: {assistant_reply}")
    await _play_text_and_listen(call_connection_id, assistant_reply)


async def _play_text(call_connection_id: str, text: str):
    call_connection = acs_client.get_call_connection(call_connection_id)
    call_connection.play_media_to_all(
        play_source=TextSource(text=text, voice_name="en-US-JennyNeural")
    )


async def _play_text_and_listen(call_connection_id: str, text: str):
    call_connection = acs_client.get_call_connection(call_connection_id)
    call_connection.start_recognizing_media(
        input_type=RecognizeInputType.SPEECH,
        play_prompt=TextSource(text=text, voice_name="en-US-JennyNeural"),
        end_silence_timeout=3,
        callback_url=f"{settings.CALLBACK_BASE_URL}/calls/events",
    )