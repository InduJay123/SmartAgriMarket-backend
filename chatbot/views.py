from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer, ChatMessageCreateSerializer
import uuid
import json


class ChatbotIntentEngine:
    """Simple intent matching engine"""
    
    INTENTS = {
        'crop_recommendation': {
            'keywords': ['crop', 'recommend', 'suggest', 'best', 'grow', 'plant', 'what'],
            'response': 'I can help you find the best crop to plant. Tell me about your location and climate conditions.'
        },
        'weather': {
            'keywords': ['weather', 'rain', 'temperature', 'humid', 'forecast', 'climate'],
            'response': 'I can provide weather insights. What location are you interested in?'
        },
        'price': {
            'keywords': ['price', 'market', 'cost', 'sell', 'buy', 'rate', 'how much'],
            'response': 'I can help you check current market prices. Which crop are you interested in?'
        },
        'pest': {
            'keywords': ['pest', 'disease', 'insect', 'problem', 'damage', 'sick', 'control'],
            'response': 'I can help with pest and disease management. Describe the issue you\'re facing.'
        },
        'fertilizer': {
            'keywords': ['fertilizer', 'nutrient', 'soil', 'fertilize', 'npk', 'compost'],
            'response': 'I can advise on fertilizer use. What crop are you growing?'
        },
        'general': {
            'keywords': ['hello', 'hi', 'help', 'thanks', 'ok'],
            'response': 'Hello! I\'m your agricultural assistant. I can help with crop recommendations, market prices, weather, pests, and fertilizer advice.'
        }
    }

    @staticmethod
    def match_intent(message):
        """Simple keyword matching for intent"""
        message_lower = message.lower()
        scores = {}
        
        for intent, data in ChatbotIntentEngine.INTENTS.items():
            score = sum(1 for keyword in data['keywords'] if keyword in message_lower)
            scores[intent] = score
        
        best_intent = max(scores, key=scores.get)
        confidence = min(scores[best_intent] / max(1, len(message.split())), 1.0)
        
        if scores[best_intent] == 0:
            best_intent = 'general'
            confidence = 0.3
        
        return best_intent, confidence

    @staticmethod
    def get_response(intent):
        """Get response template for intent"""
        return ChatbotIntentEngine.INTENTS.get(intent, {}).get('response', 
            'I\'m here to help! Please tell me more about what you need.')


class ChatSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for chat sessions"""
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer

    @action(detail=False, methods=['post'])
    def create_session(self, request):
        """Create a new chat session"""
        session_id = str(uuid.uuid4())
        session = ChatSession.objects.create(session_id=session_id)
        serializer = self.get_serializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message and get bot response"""
        session = self.get_object()
        user_message = request.data.get('message', '').strip()
        
        if not user_message:
            return Response({'error': 'Message cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Detect intent
        intent, confidence = ChatbotIntentEngine.match_intent(user_message)
        
        # Save user message
        user_msg = ChatMessage.objects.create(
            session=session,
            role='user',
            message=user_message,
            intent=intent,
            confidence=confidence,
            metadata={'intent_scores': {intent: confidence}}
        )
        
        # Generate bot response
        bot_response_text = ChatbotIntentEngine.get_response(intent)
        
        bot_msg = ChatMessage.objects.create(
            session=session,
            role='bot',
            message=bot_response_text,
            intent=intent,
            confidence=confidence,
            metadata={'intent': intent}
        )
        
        # Update session context
        session.context['last_intent'] = intent
        session.save()
        
        return Response({
            'user_message': {
                'message': user_msg.message,
                'intent': user_msg.intent,
                'confidence': user_msg.confidence
            },
            'bot_response': {
                'message': bot_msg.message,
                'intent': bot_msg.intent,
                'confidence': bot_msg.confidence
            }
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get conversation history"""
        session = self.get_object()
        messages = session.messages.all()
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)
