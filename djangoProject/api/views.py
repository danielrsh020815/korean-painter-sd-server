import os

from dotenv import load_dotenv

# Create your views here.
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import requests


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
        negative_prompt = 'text, watermark, nude'
        workflow = 'kimhongdo'
        image = None

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
    _gpu_server_id = None
    _gpu_server_password = None

    @classmethod
    def load(cls):
        if not cls._loaded:
            load_dotenv()
            cls._gpu_machine_url = os.getenv('GPU_MACHINE_URL')
            cls._gpu_server_id = os.getenv('GPU_SERVER_ID')
            cls._gpu_server_password = os.getenv('GPU_SERVER_PASSWORD')

    @classmethod
    def gpu_machine_url(cls):
        cls.load()
        return cls._gpu_machine_url

    @classmethod
    def gpu_server_id(cls):
        cls.load()
        return cls._gpu_server_id

    @classmethod
    def gpu_server_password(cls):
        cls.load()
        return cls._gpu_server_password
