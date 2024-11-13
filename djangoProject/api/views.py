import os

from dotenv import load_dotenv
from pyexpat.errors import messages

# Create your views here.
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import requests
from openai import OpenAI


class Login(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        response = requests.post(
            f'{_ConfigManager.gpu_machine_url()}/users/login/',
            json={'username': username, 'password': password},
        )

        if response.status_code == 200:
            response = response.json()
            return Response({'success': True, 'refresh': response.get('refresh'), 'access': response.get('access')}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)


class PromptRequest(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        access = request.data.get('access')
        prompt = request.data.get('prompt')
        use_llm = request.data.get('use_llm')
        negative_prompt = 'text, watermark, nude, realistic, cinematic lighting'
        workflow = 'kimhongdo'
        image = None

        if use_llm:
            prompt = self._get_revised_prompt(prompt)

        # GPU 머신으로 요청 전송
        response = requests.post(
            f'{_ConfigManager.gpu_machine_url()}/generation/prompt/',
            headers={'Authorization': f'{access}', 'Content-Type': 'application/json'},
            json={'prompt': prompt, 'negative_prompt': negative_prompt, 'workflow': workflow, 'image': image},
        )

        if response.status_code == 201:
            return Response({'success': True, 'prompt_id': response.json().get('data').get('prompt_id')}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)

    def _get_revised_prompt(self, prompt):
        print(prompt)
        response = _ConfigManager.openai_client().chat.completions.create(
            model='gpt-4o',
            messages=[
                {
                    'role': 'system',
                    'content': 'You are an agent that optimizes the input provided by the user to generate an improved prompt for Stable Diffusion. You only answer with improved prompt.'
                },
                {
                    'role': 'user',
                    'content': prompt
                },
            ]
        )

        return response.choices[0].message.content.strip()


class ProgressRequest(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        access = request.data.get('access')
        prompt_id = request.data.get('prompt_id')
        response = requests.post(
            f'{_ConfigManager.gpu_machine_url()}/generation/progress/',
            headers={'Authorization': f'{access}', 'Content-Type': 'application/json'},
            json={'prompt_id': prompt_id},
        )

        if response.status_code == 200:
            return Response({'progress': response.json().get('data').get('progress')}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)


class ImageRequest(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        access = request.data.get('access')
        prompt_id = request.data.get('prompt_id')
        response = requests.post(
            f'{_ConfigManager.gpu_machine_url()}/generation/fetch/',
            headers={'Authorization': f'{access}', 'Content-Type': 'application/json'},
            json={'prompt_id': prompt_id},
        )

        if response.status_code == 201:
            image_url = response.json().get('data').get('image_url')
            return Response({'image_url': image_url}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)


class _ConfigManager:
    _loaded = False
    _gpu_machine_url = None
    _openai_client = None

    @classmethod
    def load(cls):
        if not cls._loaded:
            load_dotenv()
            cls._gpu_machine_url = os.getenv('GPU_MACHINE_URL')
            cls._openai_client = OpenAI(
                api_key=os.getenv('OPENAI_API_KEY'),
            )

    @classmethod
    def gpu_machine_url(cls):
        cls.load()
        return cls._gpu_machine_url

    @classmethod
    def openai_client(cls) -> OpenAI:
        cls.load()
        return cls._openai_client
