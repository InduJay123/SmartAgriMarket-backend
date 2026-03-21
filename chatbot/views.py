from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer, ChatMessageCreateSerializer
import uuid
import json
import re
from datetime import datetime

# Import ML predictors

# Singleton predictors to avoid reloading on every request
_price_predictor = None
_yield_predictor = None
_demand_predictor = None


def get_price_predictor():
    global _price_predictor
    if _price_predictor is None:
        _price_predictor = PricePredictor()
    return _price_predictor


def get_yield_predictor():
    global _yield_predictor
    if _yield_predictor is None:
        _yield_predictor = YieldPredictor()
    return _yield_predictor


def get_demand_predictor():
    global _demand_predictor
    if _demand_predictor is None:
        _demand_predictor = DemandPredictor()
    return _demand_predictor


# List of known crops/vegetables
KNOWN_CROPS = [
    'tomato', 'potato', 'carrot', 'beans', 'cabbage', 'brinjal', 'pumpkin',
    'snake gourd', 'big onion', 'red onion', 'green chilli', 'dried chilli',
    'lime', 'coconut', 'rice', 'maize', 'wheat', 'soybean', 'groundnut',
    'sugarcane', 'cotton', 'tea', 'rubber', 'pepper', 'cinnamon', 'clove',
    'nutmeg', 'cardamom', 'ginger', 'turmeric', 'papaya', 'banana', 'mango',
    'pineapple', 'orange', 'lemon', 'grapes', 'apple', 'watermelon', 'cucumber',
    'bitter gourd', 'bottle gourd', 'ridge gourd', 'drumstick', 'okra', 'radish',
    'beetroot', 'spinach', 'lettuce', 'cauliflower', 'broccoli', 'leeks',
    'spring onion', 'garlic', 'mushroom', 'capsicum', 'eggplant', 'zucchini'
]


def extract_crop_from_message(message):
    """Extract crop name from user message"""
    message_lower = message.lower()
    
    # Check for known crops
    for crop in KNOWN_CROPS:
        if crop in message_lower:
            return crop.title()
    
    # Also check for common variations
    variations = {
        'aubergine': 'Brinjal',
        'eggplant': 'Brinjal',
        'chili': 'Green Chilli',
        'chilli': 'Green Chilli',
        'onion': 'Big Onion',
        'gourd': 'Snake gourd',
    }
    
    for variation, crop in variations.items():
        if variation in message_lower:
            return crop
    
    return None


class ChatbotIntentEngine:
    """Smart intent matching engine with ML predictions"""
    
    INTENTS = {
        'price_prediction': {
            'keywords': ['price', 'cost', 'rate', 'how much', 'market price', 'selling price', 'buying price'],
            'response': 'I can help you check current market prices. Which crop are you interested in?'
        },
        'yield_prediction': {
            'keywords': ['yield', 'harvest', 'production', 'how much produce', 'output', 'crop yield'],
            'response': 'I can predict crop yield for you. Please tell me the crop type and farming conditions.'
        },
        'demand_prediction': {
            'keywords': ['demand', 'forecast', 'market demand', 'need', 'requirement', 'consumption'],
            'response': 'I can forecast market demand. Which crop would you like to check?'
        },
        'crop_recommendation': {
            'keywords': ['recommend', 'suggest', 'best crop', 'what to grow', 'what to plant', 'which crop'],
            'response': 'I can help you find the best crop to plant. Tell me about your location and climate conditions.'
        },
        'weather': {
            'keywords': ['weather', 'rain', 'temperature', 'humid', 'forecast', 'climate'],
            'response': 'I can provide weather insights. What location are you interested in?'
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
            'keywords': ['hello', 'hi', 'help', 'thanks', 'ok', 'hey'],
            'response': 'Hello! I\'m your agricultural assistant. I can help with:\n• Price predictions\n• Yield predictions\n• Demand forecasting\n• Crop recommendations\n• Pest management\n• Fertilizer advice\n\nJust ask me something like "What is the price of tomato?" or "Predict yield for rice".'
        }
    }

    @staticmethod
    def match_intent(message):
        """Smart keyword matching for intent"""
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
    def get_response(intent, message, session_context=None):
        """Generate intelligent response based on intent and extract predictions"""
        crop = extract_crop_from_message(message)
        
        # Price prediction
        if intent == 'price_prediction':
            if crop:
                try:
                    predictor = get_price_predictor()
                    price = predictor.predict({
                        'product': crop,
                        'date': datetime.now()
                    })
                    return f"📊 **Price Prediction for {crop}**\n\nThe predicted wholesale price for {crop} is **Rs. {price:.2f}** per kg.\n\nThis prediction is based on historical market data from Pettah and Dambulla markets."
                except Exception as e:
                    return f"Sorry, I couldn't predict the price for {crop}. Error: {str(e)}"
            else:
                return "I can predict prices. Please specify a crop, for example: 'What is the price of tomato?' or 'Potato price prediction'"
        
        # Yield prediction
        elif intent == 'yield_prediction':
            if crop:
                try:
                    predictor = get_yield_predictor()
                    # Default features for yield prediction
                    features = {
                        'crop_type': crop,
                        'area': 1.0,  # 1 hectare
                        'rainfall': 1500,  # mm
                        'temperature': 28,  # Celsius
                        'soil_type': 'loamy',
                        'fertilizer_used': 100,  # kg
                    }
                    yield_value = predictor.predict(features)
                    return f"🌾 **Yield Prediction for {crop}**\n\nPredicted yield: **{yield_value:.2f} kg/hectare**\n\nThis is based on average conditions (1500mm rainfall, 28°C temperature, loamy soil). For more accurate predictions, provide specific farming conditions."
                except Exception as e:
                    return f"Sorry, I couldn't predict the yield for {crop}. Error: {str(e)}"
            else:
                return "I can predict crop yields. Please specify a crop, for example: 'What is the yield of rice?' or 'Tomato yield prediction'"
        
        # Demand prediction
        elif intent == 'demand_prediction':
            if crop:
                try:
                    predictor = get_demand_predictor()
                    if hasattr(predictor, 'forecast_days'):
                        import os
                        from django.conf import settings
                        excel_path = os.path.join(settings.BASE_DIR, "data", "demand_dataset.xlsx")
                        df = pd.read_excel(excel_path)
                        result = predictor.forecast_days(
                            product_name=crop,
                            forecast_days=7,
                            consumption_trend='Stable',
                            excel_df=df
                        )
                        if result and 'data' in result:
                            total_demand = sum([f.get('demand_tonnes', 0) for f in result['data']])
                            avg_demand = total_demand / len(result['data'])
                            return f"📈 **Demand Forecast for {crop}**\n\nAverage daily demand: **{avg_demand:.2f} tonnes**\n7-day total demand: **{total_demand:.2f} tonnes**\n\nTrend: {result.get('consumption_trend', 'Stable')}"
                        else:
                            return f"📈 **Demand Forecast for {crop}**\n\nDemand prediction model is processing. The market shows stable demand patterns for {crop}."
                    else:
                        return f"Demand forecasting is available for {crop}. Please check back later for detailed predictions."
                except Exception as e:
                    return f"Sorry, I couldn't predict the demand for {crop}. Error: {str(e)}"
            else:
                return "I can forecast market demand. Please specify a crop, for example: 'What is the demand for cabbage?' or 'Tomato demand forecast'"
        
        # Default response for other intents
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
        
        # Generate bot response with ML predictions
        bot_response_text = ChatbotIntentEngine.get_response(intent, user_message, session.context)
        
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
